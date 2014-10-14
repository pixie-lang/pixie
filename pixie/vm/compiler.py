from pixie.vm.object import Object, _type_registry
from pixie.vm.primitives import nil, true, false, Bool
from pixie.vm.persistent_vector import EMPTY, PersistentVector
import pixie.vm.numbers as numbers
from pixie.vm.cons import cons, Cons
import pixie.vm.symbol as symbol
import pixie.vm.code as code
from pixie.vm.keyword import Keyword
from pixie.vm.string import String
import pixie.vm.protocols as proto
from rpython.rlib.rarithmetic import r_uint

import pixie.vm.rt as rt
from pixie.vm.util import *

rt.init()


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
            assert isinstance(parent_ctx, Context)
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
        self.ns = u"user"
        self.recur_points = []

    def sp(self):
        return self._sp

    def add_sp(self, v):
        self._sp += v
        if self._max_sp < self._sp:
            self._max_sp = self._sp

    def sub_sp(self, v):
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
        return code.Code(self.name, self.bytecode, clone(self.consts), self._max_sp + 1)
        #if required_args != -1:
        #    return code.VariadicCode(self.name, self.bytecode, clone(self.consts), self._max_sp + 1, required_args)
        #else:
        #    return code.Code(self.name, self.bytecode, clone(self.consts), self._max_sp + 1)

    def push_arg(self, idx):
        self.bytecode.append(code.ARG)
        self.bytecode.append(r_uint(idx))
        self.add_sp(1)


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
        assert self._argc == argc
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
    var = code.get_var_if_defined(ctx.ns, name)
    if var is None:
        var = code.get_var_if_defined(u"pixie.stdlib", name)
    return var

def resolve_local(ctx, name):
    return ctx.get_local(name)


def is_macro_call(form, ctx):
    if rt.seq_QMARK_(form) is true and isinstance(rt.first(form), symbol.Symbol):
        name = rt.first(form)._str
        if resolve_local(ctx, name):
            return None
        var = resolve_var(ctx, name)

        if var and var.is_defined():
            val = var.deref()
            if isinstance(val, code.BaseCode) and val.is_macro():
                return val
    return None

def call_macro(var, form, ctx):
    form = rt.next(form)
    args = [None] * rt.count(form).int_val()
    i = 0
    while form is not nil:
        args[i] = rt.first(form)
        form = rt.next(form)
        i += 1
    return var.invoke(args)

def compile_form(form, ctx):
    if rt.instance_QMARK_(form, rt.ISeq.deref()) is true and form is not nil:
        return compile_cons(form, ctx)
    if isinstance(form, numbers.Integer):
        ctx.push_const(form)
        return

    if isinstance(form, symbol.Symbol):
        name = form._str
        loc = resolve_local(ctx, name)
        if loc is None:
            var = resolve_var(ctx, name)
            if var is None:
                var = _type_registry.get_by_name(name, None)
                if var is not None:
                    ctx.push_const(var)
                    return
                var = None

            if var is None:
                var = _type_registry.get_by_name(u"pixie.stdlib." + name, None)
                if var is not None:
                    ctx.push_const(var)
                    return

            if var is None:
                var = code.intern_var(ctx.ns, name)



            ctx.push_const(var)

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
        size = rt.count(form).int_val()
        #assert rt.count(form).int_val() == 0
        ctx.push_const(code.intern_var(u"pixie.stdlib", u"vector"))
        for x in range(size):
            compile_form(rt.nth(form, numbers.Integer(x)), ctx)

        ctx.bytecode.append(code.INVOKE)
        ctx.bytecode.append(r_uint(size + 1))
        ctx.sub_sp(size)
        return

    if isinstance(form, String):
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
    assert rt.count(form).int_val() == 2
    while form is not nil:
        compile_form(form.first(), ctx)
        form = form.next()

    ctx.bytecode.append(code.EQ)
    ctx.sub_sp(1)
    return ctx

def add_args(args, ctx):
    required_args = -1
    local_idx = 0
    for x in range(rt.count(args).int_val()):
        arg = rt.nth(args, numbers.Integer(x))
        assert isinstance(arg, symbol.Symbol)
        if arg._str == u"&":

            required_args = x
            continue
        ctx.add_local(arg._str, Arg(local_idx))
        local_idx += 1
    return required_args


def compile_fn(form, ctx):
    assert isinstance(form, Cons)


    form = rt.next(form)
    if isinstance(rt.first(form), symbol.Symbol):
        name = rt.first(form)
        form = rt.next(form)
    else:
        name = symbol.symbol(u"unknown")


    if rt.instance_QMARK_(rt.first(form), rt.ISeq.deref()) is true:
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

        ctx.sub_sp(len(arities))

    else:
        compile_fn_body(name, rt.first(form), rt.next(form), ctx)




def compile_fn_body(name, args, body, ctx):
    new_ctx = Context(name._str, rt.count(args).int_val(), ctx)
    required_args = add_args(args, new_ctx)
    bc = 0

    if name is not None:
        assert isinstance(name, symbol.Symbol)
        new_ctx.add_local(name._str, Self())

    new_ctx.push_recur_point(FunctionRecurPoint())

    new_ctx.disable_tail_call()
    while body is not nil:
        if rt.next(body) is nil:
            new_ctx.enable_tail_call()
        compile_form(rt.first(body), new_ctx)
        if rt.next(body) is not nil:
            new_ctx.pop()
        bc += 1
        body = rt.next(body)

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

    return required_args, rt.count(args).int_val()

def compile_if(form, ctx):
    form = form.next()
    assert rt.count(form).int_val() == 3

    test = form.first()
    form = form.next()
    then = form.first()
    form = form.next()
    els = form.first()

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
    assert ctx.sp() == sp1, "If branches unequal " + str(ctx.sp()) + ", " + str(sp1)
    else_lbl = ctx.label()

    ctx.mark(cond_lbl)
    compile_form(els, ctx)

    ctx.mark(else_lbl)

def compile_def(form, ctx):
    form = rt.next(form)
    name = rt.first(form)
    form = rt.next(form)
    val = rt.first(form)

    assert isinstance(name, symbol.Symbol)

    var = code.intern_var(ctx.ns, name._str)
    ctx.push_const(var)
    compile_form(val, ctx)
    ctx.bytecode.append(code.SET_VAR)
    ctx.sub_sp(1)

def compile_do(form, ctx):
    form = rt.next(form)
    assert form is not nil

    while True:
        compile_form(rt.first(form), ctx)
        form = rt.next(form)

        if form is nil:
            return
        else:
            ctx.pop()

def compile_quote(form, ctx):
    data = form.next().first()
    ctx.push_const(data)

def compile_recur(form, ctx):
    form = form.next()
    assert ctx.can_tail_call
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
    ctx.sub_sp(args - 1)


def compile_let(form, ctx):
    form = next(form)
    bindings = rt.first(form)
    assert isinstance(bindings, PersistentVector)
    body = next(form)

    ctc = ctx.can_tail_call
    ctx.disable_tail_call()

    binding_count = 0
    for i in range(0, rt.count(bindings).int_val(), 2):
        binding_count += 1
        name = rt.nth(bindings, numbers.Integer(i))
        assert isinstance(name, symbol.Symbol)
        bind = rt.nth(bindings, numbers.Integer(i + 1))

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

def compile_loop(form, ctx):
    form = next(form)
    bindings = rt.first(form)
    assert isinstance(bindings, PersistentVector)
    body = next(form)

    ctc = ctx.can_tail_call
    ctx.disable_tail_call()

    binding_count = 0
    for i in range(0, rt.count(bindings).int_val(), 2):
        binding_count += 1
        name = rt.nth(bindings, numbers.Integer(i))
        assert isinstance(name, symbol.Symbol)
        bind = rt.nth(bindings, numbers.Integer(i + 1))

        compile_form(bind, ctx)

        ctx.add_local(name._str, LetBinding(ctx.sp()))

    if ctc:
        ctx.enable_tail_call()

    ctx.push_recur_point(LoopRecurPoint(binding_count, ctx))
    while True:
        compile_form(rt.first(body), ctx)
        body = next(body)

        if body is nil:
            break
        else:
            ctx.pop()

    ctx.pop_recur_point()
    ctx.bytecode.append(code.POP_UP_N)
    ctx.sub_sp(binding_count)
    ctx.bytecode.append(binding_count)

def compile_comment(form, ctx):
    ctx.push_const(nil)

builtins = {u"fn": compile_fn,
            u"if": compile_if,
            u"platform=": compile_platform_eq,
            u"def": compile_def,
            u"do": compile_do,
            u"quote": compile_quote,
            u"recur": compile_recur,
            u"let": compile_let,
            u"loop": compile_loop,
            u"comment": compile_comment}


def compile_cons(form, ctx):
    if isinstance(form.first(), symbol.Symbol) and form.first()._str in builtins:
        return builtins[form.first()._str](form, ctx)

    macro = is_macro_call(form, ctx)
    if macro:
        return compile_cons(call_macro(macro, form, ctx), ctx)

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
    ctx.bytecode.append(code.INVOKE)

    ctx.bytecode.append(cnt)
    ctx.sub_sp(cnt - 1)


def compile(form):
    ctx = Context(u"main", 0, None)
    compile_form(form, ctx)
    ctx.bytecode.append(code.RETURN)
    return ctx.to_code()