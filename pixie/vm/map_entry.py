py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint, intmask
import rpython.rlib.jit as jit
import pixie.vm.rt as rt


class MapEntry(object.Object):
    _type = object.Type(u"pixie.stdlib.MapEntry")

    def type(self):
        return MapEntry._type

    def __init__(self, key, val):
        self._key = key
        self._val = val



@as_var("map-entry")
def map_entry(k, v):
    return MapEntry(k, v)


@extend(proto._key, MapEntry)
def _key(self):
    assert isinstance(self, MapEntry)
    return self._key

@extend(proto._val, MapEntry)
def _val(self):
    assert isinstance(self, MapEntry)
    return self._val

