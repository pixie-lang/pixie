import loki_vm.vm.object as object
from loki_vm.vm.primitives import nil, true, false
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
             "DEREF_VAR"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)

class BaseCode(object.Object):

    @elidable
    def get_consts(self):
        raise NotImplementedError()

    @elidable
    def get_bytecode(self):
        raise NotImplementedError()



class Code(BaseCode):
    _type = object.Type("Code")
    _immutable_fields_ = ["_consts", "_bytecode"]
    def __init__(self, bytecode, consts):
        self._bytecode = bytecode
        self._consts = consts

    @elidable
    def get_consts(self):
        return self._consts

    @elidable
    def get_bytecode(self):
        return self._bytecode

class Closure(BaseCode):
    _type = object.Type("Closure")
    def __init__(self, code, closed_overs):
        self._code = code
        self._closed_overs = closed_overs

    @elidable
    def get_closed_over(self, idx):
        return self._closed_overs[idx]

    @elidable
    def get_consts(self):
        return self._code.get_consts()

    @elidable
    def get_bytecode(self):
        return self._code.get_bytecode()

class Var(object.Object):
    type = object.Type("Var")
    _immutable_fields_ = ["_rev?"]
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
