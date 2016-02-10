import pixie.vm.rt as rt
from pixie.vm.object import Object, Type
from pixie.vm.code import as_var, extend
import pixie.vm.stdlib as proto

class StringBuilder(Object):
    _type = Type(u"pixie.stdlib.StringBuilder")

    def __init__(self):
        self._strs = []

    def add_str(self, s):
        self._strs.append(s)
        return self

    def to_string(self):
        return u"".join(self._strs)


@extend(proto._conj_BANG_, StringBuilder)
def _conj(self, val):
    return self.add_str(rt.name(rt._str(val)))

@extend(proto._persistent_BANG_, StringBuilder)
def _persistent(self):
    return rt._str(self)

@extend(proto._str, StringBuilder)
def _str(self):
    return rt.wrap(self.to_string())

@as_var("-string-builder")
def _string_builder():
    return StringBuilder()
