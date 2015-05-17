import pixie.vm2.rt as rt
from pixie.vm2.object import Object, Type
from pixie.vm2.code import as_var, extend
import pixie.vm2.stdlib as proto

class StringBuilder(Object):
    _type = Type(u"pixie.stdlib.StringBuilder")

    def type(self):
        return StringBuilder._type

    def __init__(self):
        self._strs = []

    def add_str(self, s):
        self._strs.append(s)
        return self

    def to_str(self):
        return u"".join(self._strs)

