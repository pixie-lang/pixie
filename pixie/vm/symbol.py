import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
import pixie.vm.protocols as proto
from pixie.vm.code import extend
from pixie.vm.string import String

class Symbol(object.Object):
    _type = object.Type(u"Symbol")

    def __init__(self, s):
        assert isinstance(s, unicode)
        self._str = s

    def type(self):
        return Symbol._type


def symbol(s):
    return Symbol(s)

@extend(proto._eq, Symbol._type)
def _eq(self, other):
    if not isinstance(other, Symbol):
        return false
    return true if self._str == other._str else false

@extend(proto._str, Symbol._type)
def _str(self):
    return String(self._str)