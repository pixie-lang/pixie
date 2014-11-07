from pixie.vm.object import Object, _type_registry, affirm, InterpreterCodeInfo
from pixie.vm.primitives import nil, true, false, Bool
from pixie.vm.persistent_vector import EMPTY, PersistentVector
from pixie.vm.persistent_hash_set import PersistentHashSet
import pixie.vm.numbers as numbers
from pixie.vm.cons import cons, Cons
import pixie.vm.symbol as symbol
import pixie.vm.code as code
from pixie.vm.keyword import Keyword, keyword
from pixie.vm.string import Character, String
from pixie.vm.atom import Atom
import pixie.vm.stdlib as proto
from rpython.rlib.rarithmetic import r_uint

import pixie.vm.rt as rt
from pixie.vm.util import *

NS_VAR = code.intern_var(u"pixie.stdlib", u"*ns*")
NS_VAR.set_dynamic()

FN_NAME = code.intern_var(u"pixie.stdlib", u"*fn-name*")
FN_NAME.set_dynamic()

DYNAMIC_KW = keyword(u"dynamic")

gensym_id = Atom(numbers.zero_int)

def gensym1():
    return gensym2(rt.wrap(u"gensym_"))

def gensym2(prefix):
    rt.reset_BANG_(gensym_id, rt._add(rt.deref(gensym_id), rt.wrap(1)))
    i = rt.deref(gensym_id)

    return rt.symbol(rt.str(prefix, i))

gensym = code.intern_var(u"pixie.stdlib", u"gensym")
gensym.set_root(code.MultiArityFn({0: code.wrap_fn(gensym1), 1: code.wrap_fn(gensym2)}))

class with_ns(object):
    def __init__(self, nm):
        assert isinstance(nm, unicode)
        self._ns = nm
    def __enter__(self):
        code._dynamic_vars.push_binding_frame()
        NS_VAR.set_value(code._ns_registry.find_or_make(self._ns))

    def __exit__(self, exc_type, exc_val, exc_tb):
        code._dynamic_vars.pop_binding_frame()

def clone(lst):
    arr = [None] * len(lst)
    i = 0
    while i < len(lst):
        arr[i] = lst[i]
        i += 1

    return arr



class Context(object):
    def __init__(self, name, argc, parent_ctx):
        if parent_ctx is not None:
            affirm(isinstance(parent_ctx, Context), u"Parent Context must be a Context")
            locals = parent_ctx.locals[-1].copy()
            for x in locals:
                locals[x] = Closure(locals[x], parent_ctx)
        else:
            locals = {}

        self.bytecode = []
        self.consts = []
        self.locals = [locals]
        self._sp = r_uint(0)
        self._max_sp = 0
        self.can_tail_call = False
        self.closed_overs = []
        self.name = name
        self.recur_points = []
        self.debug_points = {}

    def sp(self):
        return self._sp

    def add_sp(self, v):
        self._sp += v
        if self._max_sp < self._sp:
            self._max_sp = self._sp

    def sub_sp(self, v):
        assert self._sp >= v, (v, self._sp)
        if self._max_sp < self._sp:
            self._max_sp = self._sp
        self._sp -= v


    def get_recur_point(self):
        return self.recur_points[-1]

    def push_recur_point(self, point):
        self.recur_points.append(point)

    def pop_recur_point(self):
        self.recur_points.pop()

    def to_code(self, required_args=-1):
        return code.Code(self.name, self.bytecode, clone(self.consts), self._max_sp + 1, self.debug_points)

    def push_arg(self, idx):
        self.bytecode.append(code.ARG)
        self.bytecode.append(r_uint(idx))
        self.add_sp(1)


    def pop_locals(self, i=1):
        for x in range(i):
            self.locals.pop()

    def add_local(self, name, arg):
        self.locals.append(self.locals[-1].copy())
        self.locals[-1][name] = arg


    def get_local(self, s_name):
        local = self.locals[-1].get(s_name, None)
        if local is not None and isinstance(local, Closure):
            idx = 0
            for x in self.closed_overs:
                if x is local:
                    break
                idx += 1
            if isinstance(local.local, Closure):
                self.closed_overs.append(local.ctx.get_local(s_name))
            else:
                self.closed_overs.append(local.local)

            return ClosureCell(idx)
        return local


    def undef_local(self):
        self.locals.pop()

    def add_const(self, v):
        for x in range(len(self.consts)):
            if self.consts[x] is v:
                return r_uint(x)

        idx = len(self.consts)
        self.consts.append(v)
        return r_uint(idx)

    def push_const(self, v):
        self.bytecode.append(code.LOAD_CONST)
        self.bytecode.append(self.add_const(v))
        self.add_sp(1)

    def label(self):
        lbl = len(self.bytecode)
        self.bytecode.append(r_uint(99))
        return lbl

    def mark(self, lbl):
        self.bytecode[lbl] = r_uint(len(self.bytecode)) - lbl

    def enable_tail_call(self):
        self.can_tail_call = True

    def disable_tail_call(self):
        self.can_tail_call = False

    def pop(self):
        self.bytecode.append(code.POP)
        self.sub_sp(1)



class RecurPoint(object):
    pass

class FunctionRecurPoint(RecurPoint):
    def __init__(self):
        pass

    def emit(self, ctx, argc):
        ctx.bytecode.append(code.RECUR)
        ctx.bytecode.append(argc)

class LoopRecurPoint(RecurPoint):
    def __init__(self, argc, ctx):
        self._argc = argc
        self._ip = len(ctx.bytecode)
        self._old_sp = ctx.sp() - argc

    def emit(self, ctx, argc):
        affirm(self._argc == argc, u"Recur must have same number of forms as matching loop")
        ctx.bytecode.append(code.LOOP_RECUR)
        ctx.bytecode.append(argc)
        ctx.bytecode.append(ctx.sp() - argc - self._argc - self._old_sp)
        ctx.bytecode.append(self._ip)


class LocalType(object):
    pass

class Arg(LocalType):
    def __init__(self, idx):
        self.idx = r_uint(idx)

    def emit(self, ctx):
        ctx.push_arg(self.idx)

class LetBinding(LocalType):
    def __init__(self, sp):
        self.sp = sp

    def emit(self, ctx):
        ctx.bytecode.append(code.DUP_NTH)
        assert 0 <= ctx.sp() - self.sp < 100000
        ctx.bytecode.append(r_uint(ctx.sp() - self.sp))
        ctx.add_sp(1)

class Self(LocalType):
    def __init__(self):
        pass

    def emit(self, ctx):
        ctx.bytecode.append(code.PUSH_SELF)
        ctx.add_sp(1)

class Closure(LocalType):
    def __init__(self, local, ctx):
        self.local = local
        self.ctx = ctx

class ClosureCell(LocalType):
    def __init__(self, idx):
        self.idx = r_uint(idx)

    def emit(self, ctx):
        ctx.bytecode.append(code.CLOSED_OVER)
        ctx.bytecode.append(self.idx)
        ctx.add_sp(1)




def resolve_var(ctx, name):
    return NS_VAR.deref().resolve(name)

def resolve_local(ctx, name):
    return ctx.get_local(name)


def is_macro_call(form, ctx):
    if rt.seq_QMARK_(form) is true and isinstance(rt.first(form), symbol.Symbol):
        name = rt.first(form)._str
        if resolve_local(ctx, name):
            return None
        var = resolve_var(ctx, rt.first(form))

        if var and var.is_defined():
            val = var.deref()
            if isinstance(val, code.BaseCode) and val.is_macro():
                return val
    return None

def call_macro(var, form, ctx):
    form = rt.next(form)
    args = [None] * rt.count(form)
    i = 0
    while form is not nil:
        args[i] = rt.first(form)
        form = rt.next(form)
        i += 1
    return var.invoke(args)

class CompileMapRf(code.NativeFn):
    def __init__(self, ctx):
        self._ctx = ctx
    def invoke(self, args):
        map_entry = args[1]
        compile_form(rt.key(map_entry), self._ctx)
        compile_form(rt.val(map_entry), self._ctx)
        return nil

def compile_map_literal(form, ctx):
    ctx.push_const(code.intern_var(u"pixie.stdlib", u"hashmap"))

    rt.reduce(CompileMapRf(ctx), nil, form)

    size = rt.count(form) * 2
    ctx.bytecode.append(code.INVOKE)
    ctx.bytecode.append(r_uint(size) + 1)
    if size > 0:
        ctx.sub_sp(size)

    compile_meta(rt.meta(form), ctx)

class ConsReduce(code.NativeFn):
    def invoke(self, args):
        return rt.cons(args[1], args[0])

def compile_set_literal(form, ctx):
    vals = rt.reduce(ConsReduce(), nil, form)
    vector_call = rt.cons(rt.symbol(rt.wrap(u"vector")), vals)
    set_call = rt.cons(rt.symbol(rt.wrap(u"set")), rt.cons(vector_call, nil))

    compile_cons(set_call, ctx)

def compile_meta(meta, ctx):
    ctx.push_const(code.intern_var(u"pixie.stdlib", u'with-meta'))
    ctx.bytecode.append(code.DUP_NTH)
    ctx.bytecode.append(r_uint(1))
    ctx.add_sp(1)
    ctx.push_const(meta)
    ctx.bytecode.append(code.INVOKE)
    ctx.bytecode.append(r_uint(3))
    ctx.sub_sp(2)
    ctx.bytecode.append(code.POP_UP_N)
    ctx.bytecode.append(1)
    ctx.sub_sp(1)

def compile_form(form, ctx):
    if form is nil:
        ctx.push_const(nil)
        return

    if rt.satisfies_QMARK_(rt.ISeq.deref(), form) and form is not nil:
        return compile_cons(form, ctx)
    if isinstance(form, numbers.Integer):
        ctx.push_const(form)
        return
    if isinstance(form, numbers.Float):
        ctx.push_const(form)
        return
    if isinstance(form, numbers.Ratio):
        ctx.push_const(form)
        return

    if isinstance(form, symbol.Symbol):
        name = form._str
        loc = resolve_local(ctx, name)
        if loc is None:
            var = resolve_var(ctx, form)

            if var is None:
                var = NS_VAR.deref().intern_or_make(name)

            ctx.push_const(var)

            meta = rt.meta(form)
            if meta is not nil:
                ctx.debug_points[len(ctx.bytecode)] = rt.interpreter_code_info(meta)

            ctx.bytecode.append(code.DEREF_VAR)
            return
        loc.emit(ctx)
        return

    if isinstance(form, Bool) or form is nil:
        ctx.push_const(form)
        return

    if isinstance(form, Keyword):
        ctx.push_const(form)
        return

    if isinstance(form, PersistentVector):
        vector_var = rt.vector()
        size = rt.count(form)
        #assert rt.count(form).int_val() == 0
        ctx.push_const(code.intern_var(u"pixie.stdlib", u"vector"))
        for x in range(size):
            compile_form(rt.nth(form, rt.wrap(x)), ctx)

        ctx.bytecode.append(code.INVOKE)
        ctx.bytecode.append(r_uint(size + 1))
        ctx.sub_sp(size)

        compile_meta(rt.meta(form), ctx)

        return

    if isinstance(form, PersistentHashSet):
        compile_set_literal(form, ctx)
        return

    if rt.satisfies_QMARK_(rt.IMap.deref(), form):
        compile_map_literal(form, ctx)
        return

    if isinstance(form, String):
        ctx.push_const(form)
        return

    if isinstance(form, Character):
        ctx.push_const(form)
        return

    raise Exception("Can't compile ")

def compile_platform_plus(form, ctx):
    ctc = ctx.can_tail_call
    ctx.disable_tail_call()
    form = form.next()
    while form is not nil:
        compile_form(form.first(), ctx)
        form = form.next()

    ctx.bytecode.append(code.ADD)
    ctx.sub_sp(1)
    if ctc:
        ctx.enable_tail_call()
    return ctx

def compile_platform_eq(form, ctx):
    form = form.next()

    affirm(rt.count(form) == 2, u"TODO: REMOVE")
    while form is not nil:
        compile_form(form.first(), ctx)
        form = form.next()

    ctx.bytecode.append(code.EQ)
    ctx.sub_sp(1)
    return ctx

def add_args(name, args, ctx):
    required_args = -1
    local_idx = 0
    ctx.add_local(name, Self())
    for x in range(rt.count(args)):
        arg = rt.nth(args, rt.wrap(x))
        affirm(isinstance(arg, symbol.Symbol), u"Argument names must be symbols")
        if arg._str == u"&":

            required_args = intmask(x)
            continue
        ctx.add_local(arg._str, Arg(local_idx))
        local_idx += 1
    return required_args


def compile_fn(form, ctx):
    form = rt.next(form)
    if isinstance(rt.first(form), symbol.Symbol):
        name = rt.first(form)
        form = rt.next(form)
    else:
        name = symbol.symbol(u"-fn")




    if rt.satisfies_QMARK_(rt.ISeq.deref(), rt.first(form)):
        arities = []
        while form is not nil:
            required_arity, argc = compile_fn_body(name, rt.first(rt.first(form)), rt.next(rt.first(form)), ctx)
            arities.append(argc if required_arity == -1 else required_arity | 256)
            form = rt.next(form)

        ctx.bytecode.append(code.MAKE_MULTI_ARITY)
        ctx.bytecode.append(r_uint(len(arities)))
        arities.reverse()
        for x in arities:
            ctx.bytecode.append(r_uint(x))

        ctx.add_sp(1) # result
        ctx.sub_sp(len(arities))

    else:
        compile_fn_body(name, rt.first(form), rt.next(form), ctx)

    if rt.meta(name) is not nil:
        compile_meta(rt.meta(name), ctx)


def compile_fn_body(name, args, body, ctx):
    new_ctx = Context(name._str, rt.count(args), ctx)
    required_args = add_args(name._str, args, new_ctx)
    bc = 0

    if name is not None:
        affirm(isinstance(name, symbol.Symbol), u"Function names must be symbols")
        #new_ctx.add_local(name._str, Self())

    new_ctx.push_recur_point(FunctionRecurPoint())

    new_ctx.disable_tail_call()
    if body is nil:
        compile_form(body, new_ctx)
    else:
        while body is not nil:
            if rt.next(body) is nil:
                new_ctx.enable_tail_call()
            compile_form(rt.first(body), new_ctx)
            body = rt.next(body)
            if body is not nil:
                new_ctx.pop()

    new_ctx.bytecode.append(code.RETURN)
    closed_overs = new_ctx.closed_overs
    if len(closed_overs) == 0:
        ctx.push_const(new_ctx.to_code(required_args))
    else:
        ctx.push_const(new_ctx.to_code(required_args))
        for x in closed_overs:
            x.emit(ctx)
        ctx.bytecode.append(code.MAKE_CLOSURE)
        ctx.bytecode.append(r_uint(len(closed_overs)))
        ctx.sub_sp(len(closed_overs))

    if required_args >= 0:
        ctx.bytecode.append(code.MAKE_VARIADIC)
        ctx.bytecode.append(r_uint(required_args))

    return required_args, intmask(rt.count(args))

def compile_if(form, ctx):
    form = form.next()
    affirm(2 <= rt.count(form) <= 3, u"If must have either 2 or 3 forms")

    test = rt.first(form)
    form = rt.next(form)
    then = rt.first(form)
    form = rt.next(form)
    els = rt.first(form)

    ctx.disable_tail_call()
    compile_form(test, ctx)
    ctx.bytecode.append(code.COND_BR)
    ctx.sub_sp(1)
    sp1 = ctx.sp()
    cond_lbl = ctx.label()

    ctx.enable_tail_call()

    compile_form(then, ctx)
    ctx.bytecode.append(code.JMP)
    ctx.sub_sp(1)
    affirm(ctx.sp() == sp1, u"If branches stacks are unequal " + unicode(str(ctx.sp())) + u", " + unicode(str(sp1)))
    else_lbl = ctx.label()

    ctx.mark(cond_lbl)
    compile_form(els, ctx)

    ctx.mark(else_lbl)

def compile_def(form, ctx):
    form = rt.next(form)
    name = rt.first(form)
    form = rt.next(form)
    val = rt.first(form)


    affirm(isinstance(name, symbol.Symbol), u"Def'd name must be a symbol")

    var = NS_VAR.deref().intern_or_make(rt.name(name))

    if rt._val_at(rt.meta(name), DYNAMIC_KW, nil) is true:
        assert isinstance(var, code.Var)
        var.set_dynamic()


    ctx.push_const(var)
    compile_form(val, ctx)
    ctx.bytecode.append(code.SET_VAR)
    ctx.sub_sp(1)

def compile_do(form, ctx):
    form = rt.next(form)

    while True:
        compile_form(rt.first(form), ctx)
        form = rt.next(form)

        if form is nil:
            return
        else:
            ctx.pop()

def compile_quote(form, ctx):
    data = rt.first(rt.next(form))
    ctx.push_const(data)

    if rt.meta(form) is not nil:
        compile_meta(rt.meta(form), ctx)

def compile_recur(form, ctx):
    form = form.next()
    affirm(ctx.can_tail_call, u"Can't recur in non-tail position")
    ctc = ctx.can_tail_call
    ctx.disable_tail_call()
    args = 0
    while form is not nil:
        compile_form(form.first(), ctx)
        args += 1
        form = form.next()

    #ctx.bytecode.append(code.RECUR)
    #ctx.bytecode.append(r_uint(args))
    ctx.get_recur_point().emit(ctx, args)
    if ctc:
        ctx.enable_tail_call()
    ctx.sub_sp(r_uint(args - 1))


def compile_let(form, ctx):
    form = rt.next(form)
    bindings = rt.first(form)
    affirm(isinstance(bindings, PersistentVector), u"Bindings must be a vector")
    body = rt.next(form)

    ctc = ctx.can_tail_call
    ctx.disable_tail_call()

    binding_count = 0
    for i in range(0, rt.count(bindings), 2):
        binding_count += 1
        name = rt.nth(bindings, rt.wrap(i))
        affirm(isinstance(name, symbol.Symbol), u"Let locals must be symbols")
        bind = rt.nth(bindings, rt.wrap(i + 1))

        compile_form(bind, ctx)

        ctx.add_local(name._str, LetBinding(ctx.sp()))

    if ctc:
        ctx.enable_tail_call()

    while True:
        compile_form(rt.first(body), ctx)
        body = rt.next(body)

        if body is nil:
            break
        else:
            ctx.pop()

    ctx.bytecode.append(code.POP_UP_N)
    ctx.sub_sp(binding_count)
    ctx.bytecode.append(binding_count)
    ctx.pop_locals(binding_count)

def compile_loop(form, ctx):
    form = rt.next(form)
    bindings = rt.first(form)
    affirm(isinstance(bindings, PersistentVector), u"Loop bindings must be a vector")
    body = rt.next(form)

    ctc = ctx.can_tail_call
    ctx.disable_tail_call()

    binding_count = 0
    for i in range(0, rt.count(bindings), 2):
        binding_count += 1
        name = rt.nth(bindings, rt.wrap(i))
        affirm(isinstance(name, symbol.Symbol), u"Loop must bindings must be symbols")
        bind = rt.nth(bindings, rt.wrap(i + 1))

        compile_form(bind, ctx)

        ctx.add_local(name._str, LetBinding(ctx.sp()))

    if ctc:
        ctx.enable_tail_call()

    ctx.push_recur_point(LoopRecurPoint(binding_count, ctx))
    while True:
        compile_form(rt.first(body), ctx)
        body = rt.next(body)

        if body is nil:
            break
        else:
            ctx.pop()

    ctx.pop_recur_point()
    ctx.bytecode.append(code.POP_UP_N)
    ctx.sub_sp(binding_count)
    ctx.bytecode.append(binding_count)
    ctx.pop_locals(binding_count)

def compile_comment(form, ctx):
    ctx.push_const(nil)

def compile_ns(form, ctx):
    affirm(rt.count(form) == 2, u"ns only takes one argument, a symbol")

    nm = rt.first(rt.next(form))

    affirm(isinstance(nm, symbol.Symbol), u"Namespace name must be a symbol")

    str_name = rt.name(nm)

    NS_VAR.set_value(code._ns_registry.find_or_make(str_name))
    NS_VAR.deref().include_stdlib()
    ctx.push_const(nil)

def compile_this_ns(form, ctx):
    ctx.push_const(NS_VAR.deref())

def compile_var(form, ctx):
    form = rt.next(form)
    name = rt.first(form)

    affirm(isinstance(name, symbol.Symbol), u"var name must be a symbol")

    if rt.namespace(name) is not None:
        var = code._ns_registry.find_or_make(rt.namespace(name))
    else:
        var = NS_VAR.deref().intern_or_make(rt.name(name))

    ctx.push_const(var)

def compile_catch(form, ctx):
    affirm(False, u"Catch used outside of try")

def compile_yield(form, ctx):
    affirm(rt.count(form) == 2, u"yield takes a single argument")
    arg = rt.first(rt.next(form))
    compile_form(arg, ctx)
    ctx.bytecode.append(code.YIELD)


builtins = {u"fn": compile_fn,
            u"if": compile_if,
            u"platform=": compile_platform_eq,
            u"def": compile_def,
            u"do": compile_do,
            u"quote": compile_quote,
            u"recur": compile_recur,
            u"let": compile_let,
            u"loop": compile_loop,
            u"comment": compile_comment,
            u"var": compile_var,
            u"__ns__": compile_ns,
            u"catch": compile_catch,
            u"this-ns-name": compile_this_ns,
            u"yield": compile_yield}

def compiler_special(s):
    if isinstance(s, symbol.Symbol):
        ns = rt.namespace(s)
        if ns is None or ns == u"pixie.stdlib":
            return builtins.get(rt.name(s), None)

    return None

def is_compiler_special(s):
    return True if compiler_special(s) is not None else False

def compile_cons(form, ctx):
    if isinstance(rt.first(form), symbol.Symbol):
        special = compiler_special(rt.first(form))
        if special is not None:
            return special(form, ctx)

    macro = is_macro_call(form, ctx)
    if macro:
        return compile_form(call_macro(macro, form, ctx), ctx)

    meta = rt.meta(form)

    cnt = 0
    ctc = ctx.can_tail_call
    while form is not nil:
        ctx.disable_tail_call()
        compile_form(rt.first(form), ctx)
        cnt += 1
        form = rt.next(form)

    if ctc:
        ctx.enable_tail_call()

    #if ctx.can_tail_call:
    #    ctx.bytecode.append(code.TAIL_CALL)
    #else:
    if meta is not nil:
        ctx.debug_points[len(ctx.bytecode)] = rt.interpreter_code_info(meta)
    ctx.bytecode.append(code.INVOKE)

    ctx.bytecode.append(cnt)
    ctx.sub_sp(r_uint(cnt - 1))


def compile(form):
    ctx = Context(u"main", 0, None)
    compile_form(form, ctx)
    ctx.bytecode.append(code.RETURN)
    return ctx.to_code()
