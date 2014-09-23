import loki_vm.vm.object as object
from loki_vm.vm.primitives import nil, true, false


class Symbol(object.Object):
    _type = object.Type("Symbol")

    def __init__(self, s):
        self._str = s

    def type(self):
        return Symbol._type


def symbol(s):
    return Symbol(s)