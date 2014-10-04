import pixie.vm.rt as rt
from pixie.vm.object import Object, Type
from pixie.vm.code import extend, as_var
import pixie.vm.protocols as proto

class String(Object):
    _type = Type("pixie.stdlib.String")

    def type(self):
        return String._type

    def __init__(self, s):
        self._str = s

@extend(proto._str, String._type)
def _str(x):
    return x

@extend(proto._repr, String._type)
def _repr(self):
    return "\"" + self._str + "\""
