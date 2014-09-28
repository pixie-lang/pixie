import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.jit import elidable, elidable_promote, promote


BYTECODES = ["LOAD_CONST",
             "ADD",
             "EQ",
             "INVOKE",
             "TAIL_CALL",
             "DUP_NTH",
             "RETURN",
             "COND_BR",
             "JMP",
             "CLOSED_OVER",
             "MAKE_CLOSURE",
             "SET_VAR",
             "POP",
             "DEREF_VAR",
             "INSTALL"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)

class TailCall(object.Object):
    _type = object.Type("TailCall")
    __immutable_fields_ = ["_f", "_args"]
    def __init__(self, f, args):
        self._f = f
        self._args = args

    def run(self):
        return self._f._invoke(self._args)


class BaseCode(object.Object):
    def __init__(self):
        pass

    def _invoke(self, args):
        raise NotImplementedError()

    def get_consts(self):
        raise NotImplementedError()

    def get_bytecode(self):
        raise NotImplementedError()

    def invoke(self, args):
        result = self._invoke(args)
        while isinstance(result, TailCall):
            result = result.run()
        return result




class NativeFn(BaseCode):
    """Wrapper for a native function"""
    _type = object.Type("NativeFn")

    def __init__(self):
        BaseCode.__init__(self)

    def type(self):
        return NativeFn._type

    def _invoke(self, args):
        return self.inner_invoke(args)

    def inner_invoke(self, args):
        raise NotImplementedError()


class Code(BaseCode):
    """Interpreted code block. Contains consts and """
    _type = object.Type("Code")
    __immutable_fields__ = ["_consts[*]", "_bytecode"]

    def type(self):
        return Code._type

    def __init__(self, name, bytecode, consts):
        BaseCode.__init__(self)
        self._bytecode = bytecode
        self._consts = consts
        self._name = name

    def _invoke(self, args):
        return interpret(self, args)

    def get_consts(self):
        return self._consts

    def get_bytecode(self):
        return self._bytecode

class Closure(Code):
    _type = object.Type("Closure")
    __immutable_fields__ = ["_closed_overs[*]", "_code"]
    def type(self):
        return Closure._type

    def __init__(self, code, closed_overs):
        BaseCode.__init__(self)
        self._code = code
        self._closed_overs = closed_overs

    def _invoke(self, args):
        return interpret(self, args)

    def get_closed_over(self, idx):
        return self._closed_overs[idx]

    def get_consts(self):
        return self._code.get_consts()

    def get_bytecode(self):
        return self._code.get_bytecode()

class Var(object.Object):
    _type = object.Type("Var")
    _immutable_fields_ = ["_rev?"]

    def type(self):
        return Var._type

    def __init__(self, name):
        self._name = name
        self._rev = 0

    def set_root(self, o):
        self._rev += 1
        self._root = o
        return self

    @elidable
    def get_root(self, rev):
        return self._root


    def deref(self):
        rev = promote(self._rev)
        return self.get_root(rev)


class VarRegistry(__builtins__.object):
    def __init__(self):
        self._registry = {}

    def intern_or_make(self, name):
        assert isinstance(name, str)
        v = self._registry.get(name, None)
        if v is None:
            v = Var(name).set_root(nil)
            self._registry[name] = v
        return v

_var_registry = VarRegistry()

def intern_var(name):
    return _var_registry.intern_or_make(name)



def as_var(name):
    var = intern_var(name)
    def with_fn(fn):
        inst = type("W"+fn.__name__, (NativeFn,), {"inner_invoke": fn})()
        var.set_root(inst)
        return inst
    return with_fn


