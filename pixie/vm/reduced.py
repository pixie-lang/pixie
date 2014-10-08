import pixie.vm.rt as rt
import pixie.vm.object as object
from pixie.vm.code import extend, as_var
from pixie.vm.primitives import nil, true, false
import pixie.vm.protocols as proto


class Reduced(object.Object):
    _type = object.Type(u"pixie.stdlib.Reduced")
    def type(self):
        return Reduced._type

    def __init__(self, boxed_value):
        self._boxed_value = boxed_value

@extend(proto._deref, Reduced._type)
def _deref(self):
    return self._boxed_value

@as_var("reduced")
def reduced(val):
    return Reduced(val)

@as_var("reduced?")
def reduced_QMARK_(val):
    return true if isinstance(val, Reduced) else false
