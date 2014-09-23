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
             "JMP"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)


class Code(object.Object):
    _type = object.Type("Code")
    def __init__(self, bytecode, consts):
        self._bytecode = bytecode
        self._consts = consts


class Fn(object.Object):
    _type = object.Type("Fn")
    def __init__(self, code):
        self._code = code