import pixie.vm.rt as rt
import pixie.vm.object as object
from pixie.vm.code import extend, as_var
from pixie.vm.primitives import nil
import pixie.vm.protocols as proto

import pixie.vm.protocols as proto

class Atom(object.Object):
    _type = object.Type(u"pixie.stdlib.Type")
    def type(self):
        return Atom._type

    def __init__(self, boxed_value):
        self._boxed_value = boxed_value



@extend(proto._reset_BANG_, Atom._type)
def _reset(self, v):
    self._boxed_value = v
    return self

@extend(proto._deref, Atom._type)
def _deref(self):
    return self._boxed_value

@as_var("atom")
def atom(val=nil):
    return Atom(val)
