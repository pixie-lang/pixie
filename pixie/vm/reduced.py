import pixie.vm.object as object
from pixie.vm.code import extend, as_var, returns
from pixie.vm.primitives import true, false
import pixie.vm.stdlib as proto


class Reduced(object.Object):
    _type = object.Type(u"pixie.stdlib.Reduced")

    def __init__(self, boxed_value):
        self._boxed_value = boxed_value

@extend(proto._deref, Reduced._type)
def _deref(self):
    assert isinstance(self, Reduced)
    return self._boxed_value

@as_var("reduced")
def reduced(val):
    return Reduced(val)

@returns(bool)
@as_var("reduced?")
def reduced_QMARK_(val):
    return true if isinstance(val, Reduced) else false
