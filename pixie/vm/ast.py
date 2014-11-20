from pixie.vm.effects.effects import Object, Type, Answer, Thunk, ArgList, raise_Ef
from pixie.vm.effects.effect_transform import cps
from pixie.vm.effects.environment import Resolve, resolve_Ef
from pixie.vm.primitives import true, false, nil
import rpython.rlib.jit as jit

class Syntax(Object):
    def interpret_Ef(self, env):
        pass


class Constant(Syntax):
    _immutable_fields_ = ["_val"]
    _type = Type(u"pixie.ast.Constant")
    def __init__(self, val):
        self._w_val = val

    def type(self):
        return Constant._type

    def interpret_Ef(self, locals):
        return Answer(self._w_val)

class Invoke(Syntax):
    _immutable_fields_ = ["_w_fn_and_args"]
    _type = Type(u"pixie.ast.Invoke")
    def __init__(self, fn_and_args):
        self._w_fn_and_args = fn_and_args

    def type(self):
        return Invoke._type

    @cps
    def interpret_Ef(self, env):
        arg_list = ArgList()

        fn = self._w_fn_and_args.nth(0)
        fn_resolved = fn.interpret_Ef(env)

        idx = 1
        while idx < self._w_fn_and_args.count():
            arg = self._w_fn_and_args.nth(idx)
            arg_resolved = arg.interpret_Ef(env)
            arg_list = arg_list.append(arg_resolved)
            idx += 1

        return fn_resolved.invoke_Ef(arg_list)

class Do(Syntax):
    _immutable_fields_ = ["_w_body"]
    _type = Type(u"pixie.ast.Do")
    def __init__(self, w_body):
        self._w_body = w_body

    def type(self):
        return Do._type

    @cps
    def interpret_Ef(self, env):
        idx = 0

        while True:
            ast = self._w_body.nth(idx)
            if idx + 1 < self._w_body.count():
                ast.interpret_Ef(env)
                idx += 1
            else:
                return syntax_thunk_Ef(ast, env)

class PixieFunction(Object):
    _type = Type(u"pixie.stdlib.PixieFunction")

    def __init__(self, name, args, body, env=None):
        self._w_name = name
        self._w_args = args
        self._w_body = body
        self._env = env

    def with_env(self, env):
        return PixieFunction(self._w_name, self._w_args, self._w_body, env)

    @jit.unroll_safe
    def invoke_Ef(self, args):
        env = self._env
        env = env.with_local(self._w_name, self)
        for x in range(args.arg_count()):
            env = env.with_local(self._w_args.nth(x), args.get_arg(x))

        return SyntaxThunk(self._w_body, env)


class FnLiteral(Object):
    _type = Type(u"pixie.stdlib.PixieFunction")

    def __init__(self, fn):
        self._w_fn = fn

    def interpret_Ef(self, env):
        return Answer(self._w_fn.with_env(env))






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

        ns = self._w_ns
        nm = self._w_nm
        return resolve_Ef(ns, nm)


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
        result = self._w_test.interpret_Ef(env)
        if not (result is false or result is nil):
            ast = self._w_then

        else:
            ast = self._w_else

        return syntax_thunk_Ef(ast, env)

def syntax_thunk_Ef(ast, env):
    return SyntaxThunk(ast, env)

class SyntaxThunk(Thunk):
    _immutable_ = True
    def __init__(self, ast, locals):
        self._w_ast = ast
        self._w_locals = locals

    def execute_thunk(self):
        return self._w_ast.interpret_Ef(self._w_locals)

    def get_loc(self):
        return (self._w_ast, self._w_locals)


NOT_FOUND = -1

class Locals(Object):
    _immutable_fields_ = ["_names[*]", "_vals[*]"]
    #_virtualizable_ = ["_names[*]", "_vals[*]"]

    def __init__(self, names=[], vals=[]):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)
        self._names = names
        self._vals = vals

    @jit.unroll_safe
    def name_idx(self, nm):
        x = 0
        while x < len(self._names):
            val = self._names[x]
            if nm is val:
                return x
            x += 1
        return NOT_FOUND

    def lookup_local(self, nm):
        idx = self.name_idx(nm)
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