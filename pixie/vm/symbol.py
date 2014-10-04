import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false


class Symbol(object.Object):
    _type = object.Type(u"Symbol")

    def __init__(self, s):
        assert isinstance(s, unicode)
        self._str = s

    def type(self):
        return Symbol._type


def symbol(s):
    return Symbol(s)