from pixie.vm2.object import Object, Type, Continuation, stack_cons, runtime_error, affirm
from pixie.vm2.code import ns_registry, as_var
from pixie.vm2.primitives import nil, false
from pixie.vm2.array import Array
from pixie.vm2.arraymap import ArrayMap
import pixie.vm2.code as code
from pixie.vm2.keyword import Keyword, keyword
from pixie.vm2.code import BaseCode
import pixie.vm2.rt as rt
import rpython.rlib.jit as jit
from pixie.vm2.debugger import expose

kw_type = keyword(u"type")
kw_handler = keyword(u"handler")
kw_invoke = keyword(u"invoke")
kw_ast = keyword(u"ast")
kw_resolve_all = keyword(u"resolve-all")
kw_args = keyword(u"args")
kw_acc = keyword(u"acc")
kw_let = keyword(u"let")
kw_do = keyword(u"do")
kw_delimited_continuation = keyword(u"delimited-continuation")
kw_slice = keyword(u"slice")
kw_meta = keyword(u"meta")
kw_line = keyword(u"line")
kw_file = keyword(u"file")
kw_line_number = keyword(u"line-number")
kw_column_number = keyword(u"column-number")

class Args(Object):
    _type = Type(u"pixie.interpreter.Args")
    _immutable_fields = ["_c_list[*]"]

    def type(self):
        return Args._type

    def __init__(self, lst):
        self._c_list = lst

    def c_array_value(self):
        return self._c_list





class AST(Object):
    _immutable_fields_ = ["_c_meta"]
    def __init__(self, meta):
        self._c_meta = meta

    def get_short_location(self):
        if self._c_meta != nil:
            return self._c_meta.get_short_location()
        return "<unknown>"

    def get_long_location(self):
        if self._c_meta != nil:
            return self._c_meta.get_long_location()
        return "<unknown of " + str(self) + ">"

    def describe(self):
        if self._c_meta != nil:
            return ArrayMap([kw_type, kw_ast, kw_meta, self._c_meta.describe()])

@as_var("pixie.ast.internal", "->Meta")
def new_meta(line, file, line_number, column_number):
    return Meta((line.get_name(), file.get_name(), line_number.int_val()), column_number.int_val())

class Meta(Object):
    _type = Type(u"pixie.stdlib.Meta")
    _immutable_fields_ = ["_c_column_number", "_c_line_tuple"]
    def __init__(self, line_tuple, column_number):
        self._c_column_number = column_number
        self._c_line_tuple = line_tuple

    def get_short_location(self):
        (line, file, line_number) = self._c_line_tuple

        cl = self._c_column_number - 1
        assert cl >= 0
        return str(file) + " @ " + str(line[:cl]) + "^" + str(line[cl:])

    def get_long_location(self):
        (line, file, line_number) = self._c_line_tuple
        ld = []
        ld.append(str(line))
        ld.append(" in ")
        ld.append(str(file))
        ld.append(" at ")
        ld.append(str(line_number)+":"+str(self._c_column_number))
        ld.append("\n")
        for x in range(self._c_column_number - 1):
            ld.append(" ")
        ld.append("^\n")

        return "".join(ld)

    def describe(self):
        (line, file, line_number) = self._c_line_tuple
        return ArrayMap([kw_type, kw_meta,
                         kw_line, rt.wrap(line),
                         kw_file, rt.wrap(file),
                         kw_line_number, rt.wrap(line_number),
                         kw_column_number, rt.wrap(self._c_column_number)])



class PrevASTNil(AST):
    def __init__(self):
        AST.__init__(self, nil)

@expose("_c_ast", "_c_locals")
class InterpretK(Continuation):
    _immutable_ = True
    def __init__(self, ast, locals):
        self._c_ast = ast
        self._c_locals = locals

    def call_continuation(self, val, stack):
        ast = self._c_ast
        return ast.interpret(val, self._c_locals, stack)

    def get_ast(self):
        return self._c_ast

@as_var("pixie.ast.internal", "->Const")
def new_const(val, meta):
    print val, meta
    return Const(val, meta)

@expose("_c_val")
class Const(AST):
    _immutable_fields_ = ["_c_val"]
    _type = Type(u"pixie.interpreter.Const")

    def type(self):
        return Const._type

    def __init__(self, val, meta=nil):
        AST.__init__(self, meta)
        self._c_val = val

    def interpret(self, _, locals, stack):
        return self._c_val, stack

    def gather_locals(self):
        return {}


@expose("_c_value", "_c_name", "_c_next")
class Locals(object):
    _immutable_ = True
    def __init__(self, name, value, next):
        assert isinstance(name, Keyword)
        self._c_value = value
        self._c_name = name
        self._c_next = next



    @staticmethod
    @jit.unroll_safe
    def get_local(self, name):
        if self is None:
            return nil
        c = self
        while c._c_name is not name:
            c = c._c_next
            if c is None:
                runtime_error(u"Local" + name.to_repr() + u" is undefined")
        return c._c_value

@as_var("pixie.ast.internal", "->Lookup")
def new_lookup(name, meta):
    return Lookup(name, meta)

class Lookup(AST):
    _immutable_fields_ = ["_c_name"]
    _type = Type(u"pixie.ast-internal.Lookup")

    def type(self):
        return VDeref._type

    def __init__(self, name, meta=nil):
        assert isinstance(name, Keyword)
        AST.__init__(self, meta)
        self._c_name = name

    def interpret(self, _, locals, stack):
        return Locals.get_local(locals, self._c_name), stack

    def gather_locals(self):
        return {self._c_name: self._c_name}

@as_var("pixie.ast.internal", "->Fn")
def new_fn(name, args, body, meta):
    return Fn(name, args.array_val(), body, meta=meta)

class Fn(AST):
    _immutable_fields_ = ["_c_name", "_c_args", "_c_body", "_c_closed_overs"]

    _type = Type(u"pixie.ast.internal.Fn")
    def type(self):
        return Fn._type

    def __init__(self, name, args, body, closed_overs=[], meta=nil):
        AST.__init__(self, meta)
        self._c_name = name
        self._c_args = args
        self._c_body = body

        glocals = self._c_body.gather_locals()
        for x in self._c_args:
            if x in glocals:
                del glocals[x]

        if self._c_name in glocals:
            del glocals[self._c_name]


        closed_overs = [None] * len(glocals)
        idx = 0
        for k in glocals:
            closed_overs[idx] = glocals[k]
            idx += 1

        self._c_closed_overs = closed_overs

    def gather_locals(self):
        glocals = {}

        for x in self._c_closed_overs:
            glocals[x] = x

        return glocals


    @jit.unroll_safe
    def interpret(self, _, locals, stack):
        locals_prefix = None
        for n in self._c_closed_overs:
            locals_prefix = Locals(n, Locals.get_local(locals, n), locals_prefix)

        return InterpretedFn(self._c_name, self._c_args, locals_prefix, self._c_body, self), stack

class InterpretedFn(code.BaseCode):
    _immutable_fields_ = ["_c_arg_names[*]", "_c_locals", "_c_fn_ast", "_c_name", "_c_arg_names", "_c_fn_def_ast"]
    _type = Type(u"pixie.stdlib.InterpretedFn")

    def type(self):
        return InterpretedFn._type

    def to_repr(self):
        return u"<Fn " + self._c_name.get_name() + u">"

    def to_str(self):
        return u"<Fn " + self._c_name.get_name() + u">"

    def __init__(self, name, arg_names, locals_prefix, ast, fn_def_ast):
        assert isinstance(name, Keyword)
        code.BaseCode.__init__(self)
        self._c_arg_names = arg_names
        self._c_name = name
        if name is not nil:
            self._c_locals = Locals(name, self, locals_prefix)
        else:
            self._c_locals = locals_prefix
        self._c_fn_ast = ast
        self._c_fn_def_ast = fn_def_ast

    def invoke_k(self, args, stack):
        return self.invoke_k_with(args, stack, self)

    @jit.unroll_safe
    def invoke_k_with(self, args, stack, self_fn):
        # TODO: Check arg count
        locals = self._c_locals
        locals = Locals(self._c_name, self_fn, locals)

        if not len(args) == len(self._c_arg_names):

            runtime_error(u"Wrong number args to" +
                          self.to_repr() +
                          u", got " +
                          unicode(str(len(args))) +
                          u" expected " + unicode(str(len(self._c_arg_names))) +
                          u"\n" + unicode(self._c_fn_def_ast.get_long_location()),
                          u"pixie.stdlib.ArityException")

        for idx in range(len(self._c_arg_names)):
            locals = Locals(self._c_arg_names[idx], args[idx], locals)

        return nil, stack_cons(stack, InterpretK(self._c_fn_ast, locals))


@as_var("pixie.ast.internal", "->Invoke")
def new_invoke(args, meta):
    return Invoke(args.array_val(), meta)

class Invoke(AST):
    _immutable_fields_ = ["_c_args[*]"]
    _type = Type(u"pixie.ast-internal.Invoke")

    def type(self):
        return Invoke._type

    def __init__(self, args, meta=nil):
        AST.__init__(self, meta)
        self._c_args = args

    def gather_locals(self):
        glocals = {}
        for x in self._c_args:
            glocals = merge_dicts(glocals, x.gather_locals())

        return glocals

    def interpret(self, _, locals, stack):
        stack = stack_cons(stack, ResolveAllK(self, locals, [], False))
        stack = stack_cons(stack, InterpretK(self._c_args[0], locals))
        return nil, stack

    @jit.elidable_promote()
    def arg_count(self):
        return len(self._c_args)

    @jit.elidable_promote()
    def get_arg(self, idx):
        return self._c_args[idx]


class InvokeK(Continuation):
    _immutable_ = True
    def __init__(self, invoke_args, ast):
        self._c_invoke_args = invoke_args
        self._c_ast = ast

    @jit.unroll_safe
    def fn_and_args(self):
        fn = self._c_invoke_args[0]
        new_args = [None] * (len(self._c_invoke_args) - 1)

        for x in range(len(new_args)):
            new_args[x] = self._c_invoke_args[x + 1]

        return fn, new_args


    def call_continuation(self, val, stack):
        fn, args = self.fn_and_args()
        return fn.invoke_k(args, stack)

    def get_ast(self):
        return self._c_ast

    def describe(self):
        return ArrayMap([kw_type, kw_invoke, kw_ast, self._c_ast])




@as_var("pixie.ast.internal", "->Recur")
def new_invoke(args, meta):
    return Recur(args.array_val(), meta)

class Recur(Invoke):
    _immutable_fields_ = ["_c_args", "_c_fn"]
    def __init__(self, args, meta=nil):
        Invoke.__init__(self, args, meta)
        self._c_args = args

    def interpret(self, _, locals, stack):
        stack = stack_cons(stack, ResolveAllK(self, locals, [], True))
        stack = stack_cons(stack, InterpretK(self._c_args[0], locals))
        return nil, stack

class RecurK(InvokeK):
    _immutable_ = True
    should_enter_jit = True
    def __init__(self, invoke_args, ast):
        InvokeK.__init__(self, invoke_args, ast)

    def get_ast(self):
        return self._c_ast

class ResolveAllK(Continuation):
    _immutable_ = True
    def __init__(self, args, locals, acc, recur):
        self._c_args_ast = args
        self._c_locals = locals
        self._c_acc = acc
        self._c_recur = recur

    @jit.unroll_safe
    def append_to_acc(self, val):
        acc = [None] * (len(self._c_acc) + 1)
        for x in range(len(self._c_acc)):
            acc[x] = self._c_acc[x]
        acc[len(self._c_acc)] = val
        return acc

    def call_continuation(self, val, stack):
        if len(self._c_acc) + 1 < self._c_args_ast.arg_count():
            stack = stack_cons(stack, ResolveAllK(self._c_args_ast, self._c_locals, self.append_to_acc(val), self._c_recur))
            stack = stack_cons(stack, InterpretK(self._c_args_ast.get_arg(len(self._c_acc) + 1), self._c_locals))
        else:
            new_acc = self.append_to_acc(val)
            if self._c_recur:
                return nil, stack_cons(stack, RecurK(new_acc, self._c_args_ast.get_arg(0)))
            else:
                return nil, stack_cons(stack, InvokeK(new_acc, self._c_args_ast.get_arg(0)))

        return nil, stack

    def get_ast(self):
        return self._c_args_ast.get_arg(len(self._c_acc))

    def describe(self):
        return ArrayMap([kw_type, kw_resolve_all,
                         kw_args, self._c_args_ast,
                         #kw_locals, Array(self._c_locals),
                         kw_acc, Array(self._c_acc),
                         kw_ast, self._c_args_ast.get_arg(len(self._c_acc))])

@as_var("pixie.ast.internal", "->Let")
def new_let(names, bindings, body, meta):
    return Let(names.array_val(), bindings.array_val(), body, meta)

class Let(AST):
    _immutable_fields_ = ["_c_names", "_c_bindings", "_c_body"]
    _type = Type(u"pixie.ast-internal.Let")

    def type(self):
        return VDeref._type

    def __init__(self, names, bindings, body, meta=nil):
        AST.__init__(self, meta)
        self._c_names = names
        self._c_bindings = bindings
        self._c_body = body

    def gather_locals(self):
        glocals = {}
        for x in self._c_bindings:
            glocals = merge_dicts(glocals, x.gather_locals())

        glocals = merge_dicts(glocals, self._c_body.gather_locals())

        for x in self._c_names:
            if x in glocals:
                del glocals[x]

        return glocals

    def interpret(self, _, locals, stack):
        stack = stack_cons(stack, LetK(self, 0, locals))
        stack = stack_cons(stack, InterpretK(self._c_bindings[0], locals))
        return nil, stack

class LetK(Continuation):
    _immutable_ = True
    def __init__(self, ast, idx, locals):
        self._c_idx = idx
        self._c_ast = ast
        self._c_locals = locals

    def call_continuation(self, val, stack):
        assert isinstance(self._c_ast, Let)
        new_locals = Locals(self._c_ast._c_names[self._c_idx], val, self._c_locals)

        if self._c_idx + 1 < len(self._c_ast._c_names):
            stack = stack_cons(stack, LetK(self._c_ast, self._c_idx + 1, new_locals))
            stack = stack_cons(stack, InterpretK(self._c_ast._c_bindings[self._c_idx + 1], new_locals))
        else:
            stack = stack_cons(stack, InterpretK(self._c_ast._c_body, new_locals))

        return nil, stack


    def get_ast(self):
        return self._c_ast

    def describe(self):
        return ArrayMap([kw_type, kw_let, kw_ast, self._c_ast])

@as_var("pixie.ast.internal", "->If")
def new_if(test, then, els, meta):
    return If(test, then, els, meta)

class If(AST):
    _immutable_fields_ = ["_c_test", "_c_then", "_c_else"]
    _type = Type(u"pixie.ast-internal.If")

    def type(self):
        return If._type

    def __init__(self, test, then, els, meta=nil):
        AST.__init__(self, meta)
        self._c_test = test
        self._c_then = then
        self._c_else = els

    def interpret(self, val, locals, stack):
        stack = stack_cons(stack, IfK(self, locals))
        stack = stack_cons(stack, InterpretK(self._c_test, locals))
        return nil, stack

    def gather_locals(self):
        glocals = self._c_test.gather_locals()
        glocals = merge_dicts(glocals, self._c_then.gather_locals())
        glocals = merge_dicts(glocals, self._c_else.gather_locals())
        return glocals

class IfK(Continuation):
    _immutable_ = True
    def __init__(self, ast, locals):
        self._c_ast = ast
        self._c_locals = locals

    def call_continuation(self, val, stack):
        ast = self._c_ast
        assert isinstance(self._c_ast, If)
        if val is nil or val is false:
            stack = stack_cons(stack, InterpretK(ast._c_else, self._c_locals))
        else:
            stack = stack_cons(stack, InterpretK(ast._c_then, self._c_locals))
        return nil, stack

    def get_ast(self):
        return self._c_ast

@as_var("pixie.ast.internal", "->Do")
def new_do(args, meta):
    return Do(args.array_val(), meta)

class Do(AST):
    _immutable_fields_ = ["_c_body_asts"]
    _type = Type(u"pixie.ast-internal.Do")

    def type(self):
        return Do._type

    def __init__(self, args, meta=nil):
        AST.__init__(self, meta)
        self._c_body_asts = args

    @jit.unroll_safe
    def interpret(self, val, locals, stack):
        return nil, stack_cons(stack, DoK(self, self._c_body_asts, locals))

    def gather_locals(self):
        glocals = {}
        for x in self._c_body_asts:
            glocals = merge_dicts(glocals, x.gather_locals())

        return glocals


class DoK(Continuation):
    _immutable_ = True
    def __init__(self, ast, do_asts, locals, idx=0):
        self._c_ast = ast
        self._c_locals = locals
        self._c_body_asts = do_asts
        self._c_idx = idx

    def call_continuation(self, val, stack):
        if self._c_idx + 1 < len(self._c_body_asts):
            stack = stack_cons(stack, DoK(self._c_ast, self._c_body_asts, self._c_locals, self._c_idx + 1))
            stack = stack_cons(stack, InterpretK(self._c_body_asts[self._c_idx], self._c_locals))
            return nil, stack
        else:
            stack = stack_cons(stack, InterpretK(self._c_body_asts[self._c_idx], self._c_locals))
            return nil, stack

    def get_ast(self):
        return self._c_ast

    def describe(self):
        return ArrayMap([kw_type, kw_do, kw_ast, self._c_ast])

@as_var("pixie.ast.internal", "->VDeref")
def new_vderef(in_ns, var_name, meta):
    return VDeref(in_ns.get_name(), var_name, meta)

dynamic_var_get = code.intern_var(u"pixie.stdlib", u"-dynamic-var-get")
dynamic_var_handler = code.intern_var(u"pixie.stdlib", u"dynamic-var-handler")

@expose("_c_var")
class VDeref(AST):
    _immutable_fields_ = ["_c_in_ns", "_c_var_name", "_c_var_ns"]
    _type = Type(u"pixie.ast-internal.VDeref")

    def type(self):
        return VDeref._type

    def __init__(self, in_ns, var_name, meta=nil):
        AST.__init__(self, meta)
        self._c_in_ns = in_ns
        self._c_var_ns = None if var_name.get_ns() == u"" else var_name.get_ns()
        self._c_var_name = var_name.get_name()

    def interpret(self, val, locals, stack):
        ns = ns_registry.find_or_make(self._c_in_ns)
        if ns is None:
            runtime_error(u"Namespace " + self._c_in_ns + u" is not found",
                          u"pixie.stdlib/UndefinedNamespace")

        var = ns.resolve_in_ns_ex(self._c_var_ns, self._c_var_name)
        if var is not None:
            if var.is_dynamic():
                return dynamic_var_get.invoke_k([dynamic_var_handler.deref(), var], stack)
            else:
                return var.deref(), stack
        else:
            runtime_error(u"Var " +
                          (self._c_var_ns + u"/" if self._c_var_ns else u"")
                          + self._c_var_name +
                          u" is undefined in " +
                          self._c_in_ns,
                          u"pixie.stdlib/UndefinedVar")

    def gather_locals(self):
        return {}


@as_var("pixie.ast.internal", "->VarConst")
def new_vderef(in_ns, var_name, meta):
    return VarConst(in_ns.get_name(), var_name, meta)

@expose("_c_var")
class VarConst(AST):
    _immutable_fields_ = ["_c_in_ns", "_c_var_name"]
    _type = Type(u"pixie.ast.internal.VarConst")

    def type(self):
        return VarConst._type

    def __init__(self, in_ns, var_name, meta=nil):
        AST.__init__(self, meta)
        self._c_in_ns = in_ns
        self._c_var_ns = None if var_name.get_ns() == u"" else var_name.get_ns()
        self._c_var_name = var_name.get_name()

    def interpret(self, val, locals, stack):
        ns = ns_registry.find_or_make(self._c_in_ns)
        if ns is None:
            runtime_error(u"Namespace " + self._c_in_ns + u" is not found",
                          u"pixie.stdlib/UndefinedNamespace")

        var = ns.resolve_in_ns_ex(self._c_var_ns, self._c_var_name)
        if var is not None:
            return var, stack
        else:
            if self._c_var_ns is not None:
                runtime_error(u"Var " +
                              (self._c_var_ns + u"/" if self._c_var_ns else u"")
                              + self._c_var_name +
                              u" is undefined in " +
                              self._c_in_ns,
                              u"pixie.stdlib/UndefinedVar")
            else:
                return ns.intern_or_make(self._c_var_name), stack


    def gather_locals(self):
        return {}



from rpython.rlib.jit import JitDriver
from rpython.rlib.objectmodel import we_are_translated
def get_printable_location(ast):
    return ast.get_short_location()

def should_unroll(ast):
    return True

jitdriver = JitDriver(greens=["ast"], reds=["stack", "val", "cont"], get_printable_location=get_printable_location,
                      should_unroll_one_iteration=should_unroll)


throw_var = code.intern_var(u"pixie.stdlib", u"throw")

def run_stack(val, cont, stack=None, enter_debug=True):
    stack = None
    val = None
    ast = cont.get_ast()
    while True:
        jitdriver.jit_merge_point(ast=ast, stack=stack, val=val, cont=cont)
        try:
            val, stack = cont.call_continuation(val, stack)
            ast = cont.get_ast()
        except SystemExit:
            raise
        except BaseException as ex:
            if enter_debug:
                from pixie.vm2.debugger import debug
                #debug(cont, stack, val)
            #print_stacktrace(cont, stack)
            if not we_are_translated():
                import traceback
                print(traceback.format_exc())
                print ex

            val, stack = throw_var.invoke_k([keyword(u"pixie.stdlib/InternalException"),
                                             keyword(u"TODO")], stack_cons(stack, cont))

        if stack:
            cont = stack._cont
            stack = stack._parent
        else:
            break

        if isinstance(cont, RecurK):
            jitdriver.can_enter_jit(ast=ast, stack=stack, val=val, cont=cont)


    return val

def stacktrace_for_cont(cont):
    ast = cont.get_ast()
    if ast:
        return ast.get_long_location()

def print_stacktrace(cont, stack):
    st = []
    st.append(stacktrace_for_cont(cont))
    while stack:
        st.append(stacktrace_for_cont(stack._cont))
        stack = stack._parent
    st.reverse()
    for line in st:
        print line



## Handler code


class WithHandler(code.BaseCode):
    def __init__(self):
        BaseCode.__init__(self)

    def invoke_k(self, args, stack):
        affirm(len(args) == 2, u"-with-handler takes one argument")
        handler = args[0]
        fn = args[1]

        stack = stack_cons(stack, Handler(handler))
        val, stack = fn.invoke_k([], stack)
        return val, stack



class Handler(Continuation):
    _immutable_ = True
    def __init__(self, handler):
        self._handler = handler

    def handler(self):
        return self._handler

    def get_ast(self):
        return None

    def call_continuation(self, val, stack):
        return val, stack

    def describe(self):
        return ArrayMap([kw_type, kw_handler, kw_handler, self._handler])

class DelimitedContinuation(code.NativeFn):
    _immutable_fields_ = ["_slice[*]"]
    _type = Type(u"pixie.stdlib.DelmitedContinuation")

    def type(self):
        return DelimitedContinuation._type

    def __init__(self, slice):
        self._slice = slice

    def describe(self):
        arr = [None] * len(self._slice)
        for idx, x in enumerate(self._slice):
            arr[idx] = x.describe()

        return ArrayMap([kw_type, kw_delimited_continuation,
                      kw_slice, Array(arr)])

    @jit.unroll_safe
    def invoke_k(self, args, stack):
        affirm(len(args) == 1, u"Delmited continuations only take one argument")
        for x in range(len(self._slice)):
            stack = stack_cons(stack, self._slice[x])
        return args[0], stack

@as_var(u"pixie.stdlib", u"describe-internal-object")
def describe_delimited_continuation(k):
    return k.describe()

class EffectFunction(code.BaseCode):
    _type = Type(u"pixie.stdlib.EffectFn")

    def type(self):
        return EffectFunction._type

    def __init__(self, inner_fn):
        BaseCode.__init__(self)
        self._inner_fn = inner_fn

    def invoke_k(self, args, stack):
        affirm(len(args) >= 1, u"Effect functions require at least one argument")
        handler = args[0]

        stack, slice, handler = self.slice_stack(stack, handler)

        new_args = [None] * (len(args) + 1)

        # Patch in the handler because the original handler may be nil
        new_args[0] = handler
        for x in range(1, len(args)):
            new_args[x] = args[x]
        new_args[len(args)] = DelimitedContinuation(slice)


        return self._inner_fn.invoke_k(new_args, stack)


    @jit.unroll_safe
    def append_args(self, args, val):
        new_args = [None] * (len(args) + 1)
        for x in range(len(args)):
            new_args[x] = args[x]

        new_args[(len(args))] = val

        return new_args

    @jit.unroll_safe
    def slice_stack(self, orig_stack, handler):
        if handler is nil:
            affirm(isinstance(self._inner_fn, code.PolymorphicFn), u"Can't dispatch with a nil handler from a non polymorphic effect")

        size = 0
        stack = orig_stack
        ret_handler = None

        while True:
            if stack is None:
                ## No hander found
                if not we_are_translated():
                    print "Looking for handler, none found, ", handler

                raise SystemExit()

            if (isinstance(stack._cont, Handler) and stack._cont.handler() is handler) or \
               (handler is nil and isinstance(stack._cont, Handler) and self._inner_fn.satisfied_by(stack._cont.handler())):
                size += 1
                ret_handler = stack._cont.handler()
                break

            size += 1
            stack = stack._parent

        slice = [None] * size

        stack = orig_stack
        for x in range(size - 1, -1, -1):
            slice[x] = stack._cont
            stack = stack._parent

        return stack, slice, ret_handler


def merge_dicts(a, b):
    z = a.copy()
    z.update(b)
    return z


#  Eval support

class EvalFn(code.NativeFn):

    _type = Type(u"pixie.stdlib.EvalFn")

    def type(self):
        return EvalFn._type


    @jit.unroll_safe
    def invoke_k(self, args, stack):
        affirm(len(args) == 1, u"Eval takes one argument")
        ast = args[0]

        result = ast.interpret(nil, None, stack)
        return result

as_var("pixie.ast.internal", "eval")(EvalFn())
