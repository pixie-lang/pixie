import pixie.vm.object as object
from pixie.vm.code import extend, as_var
from pixie.vm.primitives import nil
import pixie.vm.stdlib as proto


class Atom(object.Object):
    _type = object.Type(u"pixie.stdlib.Atom")

    def type(self):
        return Atom._type

    def with_meta(self, meta):
        return Atom(self._boxed_value, meta)

    def meta(self):
        return self._meta

    def __init__(self, boxed_value, meta=nil):
        self._boxed_value = boxed_value
        self._meta = meta


@extend(proto._reset_BANG_, Atom)
def _reset(self, v):
    assert isinstance(self, Atom)
    self._boxed_value = v
    return v


@extend(proto._deref, Atom)
def _deref(self):
    assert isinstance(self, Atom)
    return self._boxed_value

@extend(proto._meta, Atom)
def _meta(self):
    assert isinstance(self, Atom)
    return self.meta()

@extend(proto._with_meta, Atom)
def _with_meta(self, meta):
    assert isinstance(self, Atom)
    return self.with_meta(meta)

@as_var("atom")
def atom(val=nil):
    return Atom(val)
