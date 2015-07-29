import pixie.vm2.rt as rt
import pixie.vm2.object as object
from pixie.vm2.object import affirm
from pixie.vm2.code import extend, as_var, extend_var
from pixie.vm2.numbers import Integer
from pixie.vm2.primitives import nil
#import pixie.vm.stdlib as proto
import rpython.rlib.jit as jit
from rpython.rtyper.lltypesystem import lltype
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.objectmodel import we_are_translated
from pixie.vm2.keyword import keyword
from pixie.vm2.array import Array
import pixie.vm2.rt as rt
UNROLL_IF_SMALLER_THAN = 8

KW_count = keyword(u"count")


class ArrayMap(object.Object):
    _type = object.Type(u"pixie.stdlib.ArrayMap")
    _immutable_fields_ = ["_list"]
    def type(self):
        return ArrayMap._type

    def __init__(self, lst):
        self._list = lst

    def list_val(self):
        return self._list


@as_var(u"pixie.stdlib", u"array-map-to-array")
def to_list(this):
    return Array(this.list_val())

@as_var(u"pixie.stdlib", u"array-map")
def array_map__args(args):
    #_affirm((len(args) % 2) == 0, u"Must have even number of args to array-map")
    return ArrayMap(args)