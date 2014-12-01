from pixie.vm.effects.effects import Object, Type, Answer, Thunk, ArgList, raise_Ef
from pixie.vm.effects.effect_transform import cps
from pixie.vm.effects.environment import Resolve, resolve_Ef, declare_Ef, throw_Ef
from pixie.vm.array import array
from pixie.vm.primitives import true, false, nil
from pixie.vm.keyword import keyword
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR

import rpython.rlib.jit as jit
from rpython.rlib.rarithmetic import r_uint

class Syntax(Object):
    def interpret_Ef(self, env):
        pass


def syntax_thunk_Ef(ast, env):
    return SyntaxThunk(ast, env)


class Constant(Syntax):
    _immutable_fields_ = ["_w_val"]
    _type = Type(u"pixie.ast.Constant")
    def __init__(self, val):
        self._w_val = val

    def type(self):
        return Constant._type

    def interpret_Ef(self, locals):
        return Answer(self._w_val)

class Invoke(Syntax):
    _immutable_fields_ = ["_fn_and_args_w[*]"]
    _type = Type(u"pixie.ast.Invoke")
    def __init__(self, fn_and_args):
        self._fn_and_args_w = fn_and_args

    def type(self):
        return Invoke._type

    @cps
    def interpret_Ef(self, env):
        arg_list = ArgList()

        fn = self._fn_and_args_w[0]
        fn_resolved = syntax_thunk_Ef(fn, env)

        idx = 1
        while idx < len(self._fn_and_args_w):
            arg = self._fn_and_args_w[idx]
            arg_resolved = syntax_thunk_Ef(arg, env)
            arg_list = arg_list.append(arg_resolved)
            idx += 1

        return fn_resolved.invoke_Ef(arg_list)

class Do(Syntax):
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
                ast.interpret_Ef(env)
                idx += 1
            else:
                return syntax_thunk_Ef(ast, env)

class PixieFunction(Object):
    _type = Type(u"pixie.stdlib.PixieFunction")
    _immutable_fields_ = ["_w_name", "_args_w[*]", "_w_body", "_env"]

    def type(self):
        return PixieFunction._type

    def __init__(self, name, args, body, env=None):
        self._w_name = name
        self._args_w = args
        self._w_body = body
        self._env = env

    def required_args(self):
        return len(self._args_w)

    def with_env(self, env):
        return PixieFunction(self._w_name, self._args_w, self._w_body, env)

    def invoke_with_env_Ef(self, args, env):
        x = 0
        while x < args.arg_count():
            env = env.with_local(jit.promote(self._args_w[x]), args.get_arg(x))
            x += 1

        return SyntaxThunk(self._w_body, env)


    @jit.unroll_safe
    def _invoke_Ef(self, args):
        env = self._env
        if self._w_name is not None:
            env = env.with_local(jit.promote(self._w_name), self)
        return self.invoke_with_env_Ef(args, env)

class VariadicFunction(Object):
    _immutable_fields_ = ["_w_name", "_args_w[*]", "_w_body", "_env", "_required_args"]
    def type(self):
        return PixieFunction._type

    def __init__(self, name, args, required_args, body, env=None):
        self._w_name = name
        self._args_w = args
        self._w_body = body
        self._required_args = required_args
        self._env = env

    def required_args(self):
        return -1

    def with_env(self, env):
        return VariadicFunction(self._w_name, self._args_w, self._required_args, self._w_body, env)

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

        return SyntaxThunk(self._w_body, env)

    @jit.unroll_safe
    def _invoke_Ef(self, args):
        env = self._env
        if self._w_name is not None:
            env = env.with_local(jit.promote(self._w_name), self)
        return self.invoke_with_env_Ef(args, env)
    
    
class MultiArityFn(Object):
    _immutable_fields_ = ["_w_name", "_arities[*]", "_rest_fn", "_meta", "_env"]
    def type(self):
        return PixieFunction._type

    def __init__(self, w_name, arities, rest_fn=None, env=None, meta=nil):
        self._w_name = w_name
        self._arities = arities
        self._rest_fn = rest_fn
        self._meta = meta
        self._env = env


    def with_env(self, env):
        return MultiArityFn(self._w_name, self._arities, self._rest_fn, env, self._meta)


    @jit.elidable_promote()
    def get_fn(self, arity):
        f = self._arities.get(arity, None)
        if f is not None:
            return f
        return self._rest_fn

    def _invoke_Ef(self, args):
        env = self._env
        if self._w_name is not None:
            env = env.with_local(jit.promote(self._w_name), self)
        return self.get_fn(args.arg_count()).invoke_with_env_Ef(args, env)


class FnLiteral(Syntax):
    _type = Type(u"pixie.stdlib.PixieFunction")
    _immutable_fields_ = ["_w_fn"]
    def __init__(self, fn):
        self._w_fn = fn

    def interpret_Ef(self, env):
        return Answer(self._w_fn.with_env(env))


class Def(Object):
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
        val = syntax_thunk_Ef(ast, locals)
        ns = self._w_ns
        nm = self._w_nm
        return declare_Ef(ns, nm, val)

class Binding(Syntax):
    _type = Type(u"pixie.ast.Binding")
    _immutable_fields_ = ["_w_nm", "_w_binding_expr", "_w_body_expr"]

    def type(self):
        return Binding._type

    def __init__(self, w_nm, w_binding_expr, w_body_expr):
        self._w_nm = w_nm
        self._w_binding_expr = w_binding_expr
        self._w_body_expr = w_body_expr

    @cps
    def interpret_Ef(self, locals):
        ast = self._w_binding_expr
        result = syntax_thunk_Ef(ast, locals)
        locals = locals.with_local(self._w_nm, result)
        ast = self._w_body_expr
        return syntax_thunk_Ef(ast, locals)






KW_UNRESOVLED_SYMBOL = keyword(u"UNRESOLVED-SYMBOL")

class Lookup(Syntax):
    _type = Type(u"pixie.ast.Lookup")
    _immutable_fields_ = ["_w_ns", "_w_nm", "_explicit_namespace"]

    def __init__(self, ns, nm, explicit_namespace = False):
        self._w_ns = ns
        self._w_nm = nm
        self._explicit_namespace = explicit_namespace


    def type(self):
        return Lookup._type

    @cps
    def interpret_Ef(self, env):
        if not self._explicit_namespace:
            local = env.lookup_local(self._w_nm)
            if local is not None:
                return local

        val = resolve_Ef( self._w_ns, self._w_nm)

        if val is None:
            msg = self._w_nm.str() + u" is unresolved in " + self._w_ns.str()
            throw_Ef(KW_UNRESOVLED_SYMBOL, msg)

        return val


class If(Syntax):
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
        result = syntax_thunk_Ef(ast, env)
        if not (result is false or result is nil):
            ast = self._w_then

        else:
            ast = self._w_else

        return syntax_thunk_Ef(ast, env)

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

class Vector(Syntax):
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
            acc = acc.conj(self._array_w[idx].interpret_Ef(env))
            idx += 1
        return acc


NOT_FOUND = r_uint(1024 * 1024)

class Locals(Object):
    _immutable_fields_ = ["_names[*]", "_vals[*]"]
    _virtualizable_ = ["_names[*]", "_vals[*]"]

    def __init__(self, names=[], vals=[]):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)
        self._names = names
        self._vals = vals

    @jit.unroll_safe
    def name_idx(self, nm):
        x = r_uint(0)
        while x < r_uint(len(self._names)):
            val = self._names[x]
            if nm is val:
                return x
            x += 1
        return NOT_FOUND

    def lookup_local(self, nm):
        idx = jit.promote(self.name_idx(nm))
        if idx == NOT_FOUND:
            return None
        return self._vals[idx]

    @jit.unroll_safe
    def with_local(self, name, val):
        idx = 0
        while idx < len(self._names):
            if self._names[idx] is name:
                break
            idx += 1

        if idx == len(self._names):
            new_size = idx + 1
        else:
            new_size = len(self._names)

        new_names = [None] * new_size
        new_vals = [None] * new_size

        x = 0
        while x < len(self._names):
            new_names[x] = self._names[x]
            new_vals[x] = self._vals[x]
            x += 1

        new_names[idx] = name
        new_vals[idx] = val

        return Locals(new_names, new_vals)


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