import loki_vm.vm.object as object
from loki_vm.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint

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
             "DEREF_VAR"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)


class Code(object.Object):
    _type = object.Type("Code")
    _immutable_fields = ["_consts[*]", "_bytecode[*]"]
    def __init__(self, bytecode, consts):
        self._bytecode = bytecode
        self._consts = consts


class Closure(object.Object):
    _type = object.Type("Closure")
    def __init__(self, code, closed_overs):
        self._code = code
        self._closed_overs = closed_overs

class Var(object.Object):
    type = object.Type("Var")
    def __init__(self, name):
        self._name = name

    def set_root(self, o):
        self._root = o
        return self

    def deref(self):
        return self._root


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
