import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
import pixie.vm.protocols as proto
from pixie.vm.code import extend, as_var
from pixie.vm.string import String

class Symbol(object.Object):
    _type = object.Type(u"Symbol")

    def __init__(self, s):
        assert isinstance(s, unicode)
        self._str = s
        self._w_name = None
        self._w_ns = None

    def type(self):
        return Symbol._type

    def init_names(self):
        if self._w_name is None:
            s = self._str.split(u"/")
            if len(s) == 2:
                self._w_ns = String(s[0])
                self._w_name = String(s[1])
            elif len(s) == 1:
                self._w_name = String(s[0])
                self._w_ns = nil
            else:
                self._w_ns = String(s[0])
                self._w_name = String(u"/".join(s[1:]))



def symbol(s):
    return Symbol(s)

@extend(proto._eq, Symbol)
def _eq(self, other):
    if not isinstance(other, Symbol):
        return false
    return true if self._str == other._str else false

@extend(proto._str, Symbol)
def _str(self):
    return String(self._str)

@extend(proto._name, Symbol)
def _name(self):
    self.init_names()
    return self._w_name

@extend(proto._namespace, Symbol)
def _namespace(self):
    self.init_names()
    return self._w_ns

@as_var("symbol")
def _symbol(s):
    affirm(isinstance(s, String), u"Symbol name must be a string")
    return symbol(s._str)



