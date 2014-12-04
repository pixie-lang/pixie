from pixie.vm.effects.effects import Object, Type, Answer, Thunk, ArgList, raise_Ef
from pixie.vm.effects.effect_transform import cps
from pixie.vm.effects.environment import Resolve, resolve_Ef, declare_Ef, throw_Ef, unresolved, jitdriver
from pixie.vm.array import array
from pixie.vm.primitives import true, false, nil
from pixie.vm.keyword import keyword
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR
import rpython.rlib.debug as debug

import rpython.rlib.jit as jit
from rpython.rlib.rarithmetic import r_uint

class Syntax(Object):
    _immutable_ = True
    def interpret_Ef(self, env):
        pass


def interpret_Ef(ast, env):
    return ast.interpret_Ef(env)

def syntax_thunk_Ef(ast, env):
    return TailCallSyntaxThunk(ast, env)


class Constant(Syntax):
    _immutable_ = True
    _immutable_fields_ = ["_w_val"]
    _type = Type(u"pixie.ast.Constant")
    def __init__(self, val):
        self._w_val = val

    def type(self):
        return Constant._type

    def interpret_Ef(self, locals):
        return Answer(jit.promote(self._w_val))

class Invoke(Syntax):
    _immutable_ = True
    _immutable_fields_ = ["_fn_and_args_w[*]"]
    _type = Type(u"pixie.ast.Invoke")
    def __init__(self, fn_and_args):
        self._fn_and_args_w = fn_and_args

    def type(self):
        return Invoke._type

    @staticmethod
    def call_and_enter_jit_Ef(fn_resolved, arg_list):
        result_thunk = fn_resolved.invoke_Ef(arg_list)
        return result_thunk

    @cps
    def interpret_Ef(self, env):
        arg_list = ArgList()

        fn = self._fn_and_args_w[0]
        fn_resolved = interpret_Ef(fn, env)
        # TODO: NPE?
        #assert fn_resolved is not None

        idx = 1
        while idx < len(self._fn_and_args_w):
            arg = self._fn_and_args_w[idx]
            arg_resolved = interpret_Ef(arg, env)
            arg_list = arg_list.append(arg_resolved)
            idx += 1

        return Invoke.call_and_enter_jit_Ef(fn_resolved, arg_list)


class Do(Syntax):
    _immutable_ = True
    _immutable_fields_ = ["_body_w[*]"]
    _type = Type(u"pixie.ast.Do")
    def __init__(self, w_body):
        self._body_w = w_body

    def type(self):
        return Do._type

    @cps
    def interpret_Ef(self, env):
        idx = 0

        while True:
            ast = self._body_w[idx]
            if idx + 1 < len(self._body_w):
                interpret_Ef(ast, env)
                idx += 1
            else:
                return interpret_Ef(ast, env)

class PixieFunction(Object):
    _immutable_ = True
    _type = Type(u"pixie.stdlib.PixieFunction")
    _immutable_fields_ = ["_w_name", "_args_w[*]", "_w_body", "_env", "_name_idx"]

    def type(self):
        return PixieFunction._type

    def __init__(self, name, args, body, name_idx, env=None):
        self._name_idx = name_idx
        self._w_name = name
        self._args_w = args
        self._w_body = body
        self._env = env

    def required_args(self):
        return len(self._args_w)

    def with_env(self, env):
        return PixieFunction(self._w_name, self._args_w, self._w_body, self._name_idx, env)

    @jit.unroll_safe
    def invoke_with_env_Ef(self, args, env):
        x = 0
        while x < args.arg_count():
            env = env.with_local(jit.promote(self._args_w[x]), args.get_arg(x))
            x += 1

        return syntax_thunk_Ef(self._w_body, env)


    @jit.unroll_safe
    def _invoke_Ef(self, args):
        env = self._env
        if self._w_name is not None:
            env = env.with_local(jit.promote(self._name_idx), self)
        return self.invoke_with_env_Ef(args, env)

class VariadicFunction(Object):
    _immutable_ = True
    _immutable_fields_ = ["_w_name", "_args_w[*]", "_w_body", "_env", "_required_args", "_name_idx"]
    def type(self):
        return PixieFunction._type

    def __init__(self, name, args, required_args, body, name_idx, env=None):
        self._name_idx = name_idx
        self._w_name = name
        self._args_w = args
        self._w_body = body
        self._required_args = required_args
        self._env = env

    def required_args(self):
        return -1

    def with_env(self, env):
        return VariadicFunction(self._w_name, self._args_w, self._required_args, self._w_body, self._name_idx, env)

    @jit.unroll_safe
    def invoke_with_env_Ef(self, args, env):
        if self._required_args == 0:
            args = ArgList([array(args.list())])
        if args.arg_count() == self._required_args:
            new_args = resize_list(args.list(), args.arg_count() + 1)
            new_args[args.arg_count()] = array([])
            args = ArgList(new_args)
        elif args.arg_count() > self._required_args:
            start = slice_from_start(args.list(), self._required_args, 1)
            rest = slice_to_end(args.list(), self._required_args)
            start[self._required_args] = array(rest)
            args = ArgList(start)

        x = 0
        while x < args.arg_count():
            env = env.with_local(jit.promote(self._args_w[x]), args.get_arg(x))
            x += 1

        return TailCallSyntaxThunk(self._w_body, env)

    @jit.unroll_safe
    def _invoke_Ef(self, args):
        env = self._env
        if self._w_name is not None:
            env = env.with_local(self._name_idx, self)
        return self.invoke_with_env_Ef(args, env)
    
    
class MultiArityFn(Object):
    _immutable_ = True
    _immutable_fields_ = ["_w_name", "_arities[*]", "_rest_fn", "_meta", "_env", "_name_idx"]
    def type(self):
        return PixieFunction._type

    def __init__(self, w_name, arities, name_idx, rest_fn=None, env=None, meta=nil):
        self._name_idx = name_idx
        self._w_name = w_name
        self._arities = arities
        self._rest_fn = rest_fn
        self._meta = meta
        self._env = env


    def with_env(self, env):
        return MultiArityFn(self._w_name, self._arities, self._name_idx, self._rest_fn, env, self._meta)

    @jit.elidable_promote()
    def get_fn(self, arity):
        f = self._arities.get(arity, None)
        if f is not None:
            return f
        return self._rest_fn

    def _invoke_Ef(self, args):
        env = jit.promote(self._env)
        if self._w_name is not None:
            env = env.with_local(self._name_idx, self)
        return self.get_fn(args.arg_count()).invoke_with_env_Ef(args, env)


class FnLiteral(Syntax):
    _immutable_ = True
    _type = Type(u"pixie.stdlib.PixieFunction")
    _immutable_fields_ = ["_w_fn"]
    def __init__(self, fn):
        self._w_fn = fn

    def interpret_Ef(self, env):
        return Answer(self._w_fn.with_env(env))


class Def(Syntax):
    _immutable_ = True
    _type = Type(u"pixie.ast.Def")
    _immutable_fields_ = ["_w_nm", "_w_nm", "_w_expr"]

    def type(self):
        return Def._type

    def __init__(self, w_ns, w_nm, w_expr):
        self._w_ns = w_ns
        self._w_nm = w_nm
        self._w_expr = w_expr

    @cps
    def interpret_Ef(self, locals):
        ast = self._w_expr
        val = interpret_Ef(ast, locals)
        ns = self._w_ns
        nm = self._w_nm
        return declare_Ef(ns, nm, val)

class Binding(Syntax):
    _immutable_ = True
    _type = Type(u"pixie.ast.Binding")
    _immutable_fields_ = ["_w_nm", "_w_binding_expr", "_w_body_expr", "_idx"]

    def type(self):
        return Binding._type

    def __init__(self, idx, w_binding_expr, w_body_expr):
        assert isinstance(idx, r_uint)
        self._idx = idx
        self._w_binding_expr = w_binding_expr
        self._w_body_expr = w_body_expr

    @cps
    def interpret_Ef(self, locals):
        ast = self._w_binding_expr
        result = interpret_Ef(ast, locals)
        locals = locals.with_local(jit.promote(self._idx), result)
        ast = self._w_body_expr
        return interpret_Ef(ast, locals)






KW_UNRESOVLED_SYMBOL = keyword(u"UNRESOLVED-SYMBOL")

class LookupGlobal(Syntax):
    _immutable_ = True

    _type = Type(u"pixie.ast.LookupGlobal")
    _immutable_fields_ = ["_w_ns", "_w_nm", "_explicit_namespace"]

    def __init__(self, ns, nm, explicit_namespace = False):
        self._w_ns = ns
        self._w_nm = nm
        self._explicit_namespace = explicit_namespace


    def type(self):
        return LookupGlobal._type

    @cps
    def interpret_Ef(self, env):
        val = resolve_Ef(self._w_ns, self._w_nm)
        if val is unresolved:
            msg = self._w_nm.str() + u" is unresolved in " + self._w_ns.str()
            return throw_Ef(KW_UNRESOVLED_SYMBOL, msg)

        return val

class LookupLocal(Syntax):
    _immutable_ = True
    _type = Type(u"pixie.ast.LookupLocal")
    _immutable_fields_ = ["_idx"]

    def __init__(self, idx):
        self._idx = idx

    def type(self):
        return LookupLocal._type

    @cps
    def interpret_Ef(self, env):
        return env.lookup_local(jit.promote(self._idx))



class If(Syntax):
    _immutable_ = True
    _type = Type(u"pixie.ast.Lookup")
    _immutable_fields_ = ["_w_test", "_w_then", "_w_else"]

    def __init__(self, w_test, w_then, w_else):
        self._w_test = w_test
        self._w_then = w_then
        self._w_else = w_else

    def type(self):
        return If._type

    @cps
    def interpret_Ef(self, env):
        ast = self._w_test
        result = interpret_Ef(ast, env)
        if not (result is false or result is nil):
            ast = self._w_then

        else:
            ast = self._w_else

        return interpret_Ef(ast, env)

class SyntaxThunk(Thunk):
    _immutable_ = True
    def __init__(self, ast, locals):
        assert isinstance(ast, Syntax), type(ast)
        assert isinstance(locals, Locals)
        self._w_ast = ast
        self._w_locals = locals

    def execute_thunk(self):
        return self._w_ast.interpret_Ef(self._w_locals)

    def get_loc(self):
        return (self._w_ast, self._w_locals)

    def is_recur_point(self):
        return False

class TailCallSyntaxThunk(SyntaxThunk):
    _immutable_ = True
    def __init__(self, ast, locals):
        SyntaxThunk.__init__(self, ast, locals)

    def is_recur_point(self):
        return True

class Vector(Syntax):
    _immutable_ = True
    _immutable_fields_ = ["_array_w"]
    _type = Type(u"pixie.ast.Vector")

    def type(self):
        return Vector._type

    def __init__(self, array_w):
        self._array_w = array_w

    @cps
    def interpret_Ef(self, env):
        acc = EMPTY_VECTOR
        idx = 0
        while idx < len(self._array_w):
            acc = acc.conj(interpret_Ef(self._array_w[idx], env))
            idx += 1
        return acc


NOT_FOUND = r_uint(1024 * 1024)

class Locals(Object):
    _immutable_ = True
    _immutable_fields_ = ["_vals[*]"]
    #__virtualizable_ = ["_vals[*]"]

    def __init__(self, vals=[]):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)
        self._vals = vals
        debug.make_sure_not_resized(self._vals)

    def lookup_local(self, idx):
        assert isinstance(idx, r_uint)
        assert idx < len(self._vals)
        return self._vals[idx]

    @jit.unroll_safe
    def with_local(self, idx, val):
        #assert idx <= len(self._vals) + 1
        if idx >= len(self._vals):
            new_locals = [None] * (idx + 1)
        else:
            new_locals = [None] * len(self._vals)

        i = 0
        while i < len(self._vals):
            new_locals[i] = self._vals[i]
            i += 1

        new_locals[idx] = val

        return Locals(new_locals)


### Helpers

@jit.unroll_safe
def resize_list(lst, new_size):
    """'Resizes' a list, via reallocation and copy"""
    new_list = [None] * new_size
    i = r_uint(0)
    while i < len(lst):
        new_list[i] = lst[i]
        i += 1
    return new_list

@jit.unroll_safe
def list_copy(from_lst, from_loc, to_list, to_loc, count):
    from_loc = r_uint(from_loc)
    to_loc = r_uint(to_loc)
    count = r_uint(count)

    i = r_uint(0)
    while i < count:
        to_list[to_loc + i] = from_lst[from_loc+i]
        i += 1
    return to_list

@jit.unroll_safe
def slice_to_end(from_list, start_pos):
    start_pos = r_uint(start_pos)
    items_to_copy = len(from_list) - start_pos
    new_lst = [None] * items_to_copy
    list_copy(from_list, start_pos, new_lst, 0, items_to_copy)
    return new_lst

@jit.unroll_safe
def slice_from_start(from_list, count, extra=r_uint(0)):
    new_lst = [None] * (count + extra)
    list_copy(from_list, 0, new_lst, 0, count)
    return new_lst