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

    def interpret(self, val, locals):
        return self._interpret(val, locals)

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


class KVal(Object):
    _immutable_fields_ = ["_c_k", "_c_prev"]
    def type(self):
        runtime_error(u"KVal escaped")

    def __init__(self, prev, k):
        self._c_k = k
        self._c_prev = prev

    def get_k(self):
        return self._c_k

    def get_prev(self):
        return self._c_prev



class PrevASTNil(AST):
    def __init__(self):
        AST.__init__(self, nil)

@expose("_c_ast", "_c_locals")
class InterpretK(Continuation):
    _immutable_ = True
    def __init__(self, ast, locals):
        self._c_ast = ast
        self._c_locals = locals

    @jit.unroll_safe
    def call_continuation(self, val, stack):
        ast = jit.promote(self._c_ast)
        result = ast.interpret(val, self._c_locals)

        ## This AST created a continuation, so unpack it onto the stack
        return maybe_unpack(result, stack)

    def get_ast(self):
        return self._c_ast

@as_var("pixie.ast.internal", "->Const")
def new_const(val, meta):
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

    def _interpret(self, _, locals):
        return self._c_val

    def gather_locals(self):
        return {}


class Locals(object):
    _immutable_ = True
    def __init__(self, prev):
        assert prev is None or isinstance(prev, Locals)
        self._c_prev = prev

    @staticmethod
    def idx_tuple(self, name):
        stack_idx = 0
        c = self
        while c is not None:
            idx = c.idx_for_name(name)
            if idx != -1:
                return (stack_idx, idx)

            c = c._c_prev
            stack_idx += 1

        return (-1, -1)

    @jit.unroll_safe
    def val_at(self, idx_tuple):
        stack_idx, idx = idx_tuple
        assert stack_idx >= 0
        c = self
        for x in range(stack_idx):
            c = c._c_prev

        return c.val_for_idx(idx)

    def get_local_slow(self, name):
        tuple = Locals.idx_tuple(self, name)
        return self.val_at(tuple)


class ArrayLocals(Locals):
    _immutable_fields_ = ["_c_names[*]", "_c_vals[*]"]
    _immutable_ = True
    def __init__(self, prev, names, vals):
        Locals.__init__(self, prev)
        self._c_names = names
        self._c_vals = vals

    def idx_for_name(self, name):
        for idx, nm in enumerate(self._c_names):
            if nm is name:
                return idx
        return -1

    def val_for_idx(self, idx):
        assert idx >= 0
        return self._c_vals[idx]

class SingleLocal(Locals):
    _immutable_ = True
    def __init__(self, prev, name, val):
        Locals.__init__(self, prev)
        self._c_name = name
        self._c_val = val

    def idx_for_name(self, name):
        if name is self._c_name:
            return 0
        return -1

    def val_for_idx(self, idx):
        assert idx == 0
        return self._c_val

@as_var("pixie.ast.internal", "->Lookup")
def new_lookup(name, meta):
    return Lookup(name, meta)

class Lookup(AST):
    _immutable_fields_ = ["_c_name", "_q_idx?"]
    _type = Type(u"pixie.ast-internal.Lookup")

    def type(self):
        return VDeref._type

    def __init__(self, name, meta=nil):
        assert isinstance(name, Keyword)
        AST.__init__(self, meta)
        self._c_name = name
        self._q_idx = (-1, -1)


    def get_idx(self, locals):
        stack_idx, _ = self._q_idx
        if stack_idx == -1:
            self._q_idx = Locals.idx_tuple(locals, self._c_name)
            if not we_are_translated():
                (stack_idx, idx) = self._q_idx
                assert stack_idx >= 0, u"Local unfound" + unicode(str(self._c_name))
            return self._q_idx
        else:
            return jit.promote(self._q_idx)

    def _interpret(self, _, locals):
        idx = self.get_idx(locals)
        stack_idx, _ = idx
        assert stack_idx >= 0, u"Can't find " + self._c_name.get_name()
        return locals.val_at(idx)

    def gather_locals(self):
        return {self._c_name: self._c_name}

@as_var("pixie.ast.internal", "->Fn")
def new_fn(name, args, body, meta):
    return Fn(name, args.array_val(), body, meta=meta)

class Fn(AST):
    _immutable_fields_ = ["_c_name", "_c_args", "_c_body", "_c_closed_overs", "_c_closed_over_tuples?"]

    _type = Type(u"pixie.ast.internal.Fn")
    def type(self):
        return Fn._type

    def __init__(self, name, args, body, closed_overs=[], meta=nil):
        AST.__init__(self, meta)
        self._c_name = name
        self._c_args = args
        self._c_body = body
        self._c_closed_over_tuples = None

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

    def get_closed_over_tuples(self, local_vals):
        tuples = [(-1, -1)] * len(self._c_closed_overs)

        for idx, nm in enumerate(self._c_closed_overs):
            stack_idx, idx_val = Locals.idx_tuple(local_vals, nm)
            if not we_are_translated():
                if not stack_idx >= 0:
                    print "INTERNAL ERROR: LOCAL NOT FOUND", nm
                assert stack_idx >= 0, u"Local error" + str(nm)

            tuples[idx] = (stack_idx, idx_val)
        return tuples

    @jit.unroll_safe
    def get_closed_overs(self, locals):
        if self._c_closed_over_tuples is None:
            self._c_closed_over_tuples = self.get_closed_over_tuples(locals)

        closed_overs = [None] * len(self._c_closed_overs)
        for idx, n in enumerate(jit.promote(self._c_closed_over_tuples)):
            closed_overs[idx] = locals.val_at(jit.promote(n))

        return closed_overs


    @jit.unroll_safe
    def _interpret(self, _, locals):
        if len(self._c_closed_overs) > 0:
            closed_overs = self.get_closed_overs(locals)
            locals_prefix = ArrayLocals(None, self._c_closed_overs, closed_overs)

        else:
            locals_prefix = None

        return InterpretedFn(self._c_name, self._c_args, locals_prefix, self._c_body, self)

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
        self._c_locals = locals_prefix
        self._c_fn_ast = ast
        self._c_fn_def_ast = fn_def_ast

    def invoke_k(self, args):
        return self.invoke_k_with(args, self)

    @jit.unroll_safe
    def invoke_k_with(self, args, self_fn):
        if not len(args) == len(self._c_arg_names):

            runtime_error(u"Wrong number args to" +
                          self.to_repr() +
                          u", got " +
                          unicode(str(len(args))) +
                          u" expected " + unicode(str(len(self._c_arg_names))) +
                          u"\n" + unicode(self._c_fn_def_ast.get_long_location()),
                          u"pixie.stdlib.ArityException")

        locals = SingleLocal(self._c_locals, jit.promote(self._c_name), self_fn)
        locals = ArrayLocals(locals, self._c_arg_names, args)

        return self._c_fn_ast.interpret(nil, locals)


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

    @jit.unroll_safe
    def trim_array(self, arr, size):
        ret = [None] * size
        for x in range(size):
            ret[x] = arr[x]

        return ret

    @jit.unroll_safe
    def _interpret(self, _, locals):
        resolved = [None] * len(self._c_args)
        for idx, ast in enumerate(self._c_args):
            val = ast.interpret(nil, locals)

            if isinstance(val, KVal):
                trimmed = self.trim_array(resolved, idx)
                return KVal(val, ResolveAllK(self, locals, trimmed, False))

            resolved[idx] = val

        fn, args = fn_and_args(resolved)

        return fn.invoke_k(args)

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
        fn, args = fn_and_args(self._c_invoke_args)
        return invoke_fn(fn, args, stack)

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

    def _interpret(self, _, locals):
        ret = KVal(None, InterpretK(self._c_args[0], locals))
        ret = KVal(ret, ResolveAllK(self, locals, [], True))
        return ret

class RecurK(InvokeK):
    _immutable_ = True
    should_enter_jit = True
    def __init__(self, invoke_args, ast):
        InvokeK.__init__(self, invoke_args, ast)

    def get_ast(self):
        return self._c_ast

@jit.unroll_safe
def fn_and_args(acc):
    fn = acc[0]
    new_args = [None] * (len(acc) - 1)

    for x in range(len(new_args)):
        new_args[x] = acc[x + 1]

    return fn, new_args

@jit.unroll_safe
def maybe_unpack(val, stack):
    if isinstance(val, KVal):
        sval = val
        while sval is not None:
            stack = stack_cons(stack, sval.get_k())
            sval = sval.get_prev()
        return nil, stack
    return val, stack

def invoke_fn(fn, args, stack):
    return maybe_unpack(fn.invoke_k(args), stack)

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
            fn, args = fn_and_args(new_acc)
            return invoke_fn(fn, args, stack)
        return nil, stack

    def is_loop_tail(self):
        return self._c_recur and len(self._c_acc) + 1 == self._c_args_ast.arg_count()

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
    _immutable_fields_ = ["_c_names[*]", "_c_bindings[*]", "_c_body"]
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

    @jit.unroll_safe
    def _interpret(self, _, locals):
        for idx in range(len(self._c_names)):
            result = self._c_bindings[idx].interpret(nil, locals)


            if isinstance(result, KVal):
                return KVal(result, LetK(self, idx, locals))

            locals = SingleLocal(locals, self._c_names[idx], result)

        return self._c_body.interpret(nil, locals)

class LetK(Continuation):
    _immutable_ = True
    def __init__(self, ast, idx, locals):
        self._c_idx = idx
        self._c_ast = ast
        self._c_locals = locals

    @jit.unroll_safe
    def call_continuation(self, val, stack):
        assert isinstance(self._c_ast, Let)
        locals = SingleLocal(self._c_locals, self._c_ast._c_names[self._c_idx], val)

        if self._c_idx + 1 < len(self._c_ast._c_names):
            for idx in range(self._c_idx + 1, len(self._c_ast._c_names)):
                val = self._c_ast._c_bindings[idx].interpret(nil, locals)

                if isinstance(val, KVal):
                    stack = stack_cons(stack, LetK(self._c_ast, idx, locals))
                    return maybe_unpack(val, stack)

                locals = SingleLocal(locals, self._c_ast._c_names[idx], val)

            return maybe_unpack(self._c_ast._c_body.interpret(nil, locals), stack)

        else:
            return maybe_unpack(self._c_ast._c_body.interpret(nil, locals), stack)


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

    def _interpret(self, val, locals):
        val = self._c_test.interpret(nil, locals)


        if isinstance(val, KVal):
            ret = KVal(val, IfK(self, locals))
            return ret

        if val is false or val is nil:
            return self._c_else.interpret(nil, locals)
        else:
            return self._c_then.interpret(nil, locals)

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
    def _interpret(self, _, locals):
        val = nil
        for idx in range(len(self._c_body_asts) - 1):
            val = self._c_body_asts[idx].interpret(nil, locals)

            if isinstance(val, KVal):
                return KVal(val, DoK(self, self._c_body_asts, locals, idx + 1))

        return self._c_body_asts[(len(self._c_body_asts) - 1)].interpret(nil, locals)

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

    @jit.unroll_safe
    def call_continuation(self, val, stack):
        if self._c_idx + 1 < len(self._c_body_asts):
            for idx in range(self._c_idx, len(self._c_body_asts) - 1):
                val = self._c_body_asts[idx].interpret(nil, self._c_locals)

                if isinstance(val, KVal):
                    stack = stack_cons(stack, DoK(self._c_ast, self._c_body_asts, self._c_locals, idx + 1))
                    return maybe_unpack(val, stack)

            return maybe_unpack(self._c_body_asts[len(self._c_body_asts) - 1].interpret(nil, self._c_locals), stack)
        else:
            return maybe_unpack(self._c_body_asts[self._c_idx].interpret(nil, self._c_locals), stack)

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

    def _interpret(self, val, locals):
        ns = ns_registry.find_or_make(self._c_in_ns)
        if ns is None:
            runtime_error(u"Namespace " + self._c_in_ns + u" is not found",
                          u"pixie.stdlib/UndefinedNamespace")

        var = ns.resolve_in_ns_ex(self._c_var_ns, self._c_var_name)
        if var is not None:
            if var.is_dynamic():
                return dynamic_var_get.invoke_k([dynamic_var_handler.deref(), var])
            else:
                return var.deref()
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

    def _interpret(self, val, locals):
        ns = ns_registry.find_or_make(self._c_in_ns)
        if ns is None:
            runtime_error(u"Namespace " + self._c_in_ns + u" is not found",
                          u"pixie.stdlib/UndefinedNamespace")

        var = ns.resolve_in_ns_ex(self._c_var_ns, self._c_var_name)
        if var is not None:
            return var
        else:
            if self._c_var_ns is not None:
                runtime_error(u"Var " +
                              (self._c_var_ns + u"/" if self._c_var_ns else u"")
                              + self._c_var_name +
                              u" is undefined in " +
                              self._c_in_ns,
                              u"pixie.stdlib/UndefinedVar")
            else:
                return ns.intern_or_make(self._c_var_name)


    def gather_locals(self):
        return {}



from rpython.rlib.jit import JitDriver
from rpython.rlib.objectmodel import we_are_translated
def get_printable_location(ast):
    if ast is not nil and ast is not None:
        return ast.get_long_location()
    return ""

def should_unroll(ast):
    return True

jitdriver = JitDriver(greens=["ast"], reds=["stack", "val", "cont"], get_printable_location=get_printable_location,
                      should_unroll_one_iteration=should_unroll)

jit.set_param(jitdriver, "trace_limit", 60000)

throw_var = code.intern_var(u"pixie.stdlib", u"throw")

def run_stack(val, cont, stack=None, enter_debug=True):
    stack = None
    val = None
    ast = cont.get_ast()
    while True:
        jitdriver.jit_merge_point(ast=ast, stack=stack, val=val, cont=cont)
        if not we_are_translated():
            get_printable_location(ast)

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

            val, stack = invoke_fn(throw_var, [keyword(u"pixie.stdlib/InternalException"), keyword(u"TODO")], stack)

        prev_cont = cont
        if stack:
            cont = stack._cont
            stack = stack._parent
        else:
            break

        if prev_cont.is_loop_tail():
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

    def invoke_k(self, args):
        affirm(len(args) == 2, u"-with-handler takes one argument")
        handler = args[0]
        fn = args[1]

        ## Kindof funny, we run the function first, if it never raises an effect, then we don't need to
        ## install the handler.
        ret_val = fn.invoke_k([])

        if isinstance(ret_val, KVal):
            return KVal(ret_val, Handler(handler))
        return ret_val



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

class ValK(Continuation):
    _immutable_ = True
    def __init__(self, val):
        self._c_val = val

    def call_continuation(self, val, stack):
        return self._c_val, stack

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
    def invoke_k(self, args):
        affirm(len(args) == 1, u"Delmited continuations only take one argument")
        ret = KVal(None, ValK(args[0]))
        # TODO: Improve this?
        for x in range(len(self._slice)-1, -1, -1):
            ret = KVal(ret, self._slice[x])
        return ret

@as_var(u"pixie.stdlib", u"describe-internal-object")
def describe_delimited_continuation(k):
    return k.describe()

class EffectK(Continuation):
    _immutable_ = True
    def __init__(self, args, inner_fn):
        self._c_args = args
        self._c_inner_fn = inner_fn

    def call_continuation(self, val, stack):
        args = self._c_args
        handler = args[0]
        stack, slice, handler = self.slice_stack(stack, handler)

        new_args = [None] * (len(args) + 1)

        # Patch in the handler because the original handler may be nil
        new_args[0] = handler
        for x in range(1, len(args)):
            new_args[x] = args[x]
        new_args[len(args)] = DelimitedContinuation(slice)


        return invoke_fn(self._c_inner_fn, new_args, stack)


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
            affirm(isinstance(self._c_inner_fn, code.PolymorphicFn), u"Can't dispatch with a nil handler from a non polymorphic effect")

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
               (handler is nil and isinstance(stack._cont, Handler) and self._c_inner_fn.satisfied_by(stack._cont.handler())):
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


class EffectFunction(code.BaseCode):
    _type = Type(u"pixie.stdlib.EffectFn")

    def type(self):
        return EffectFunction._type

    def __init__(self, inner_fn):
        BaseCode.__init__(self)
        self._inner_fn = inner_fn

    def invoke_k(self, args):
        affirm(len(args) >= 1, u"Effect functions require at least one argument")

        return KVal(None, EffectK(args, self._inner_fn))





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
    def invoke_k(self, args):
        affirm(len(args) == 1, u"Eval takes one argument")
        ast = args[0]

        result = ast.interpret(nil, None)
        return result

as_var("pixie.ast.internal", "eval")(EvalFn())
