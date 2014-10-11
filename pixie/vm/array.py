import pixie.vm.rt as rt
import pixie.vm.object as object
from pixie.vm.code import extend, as_var
from pixie.vm.numbers import Integer
from pixie.vm.primitives import nil
import pixie.vm.protocols as proto

import pixie.vm.protocols as proto

class Array(object.Object):
    _type = object.Type(u"pixie.stdlib.Array")
    __immutable_fields__ = ["_list[*]"]
    def type(self):
        return Array._type

    def __init__(self, lst):
        self._list = lst


@extend(proto._count, Array._type)
def _count(self):
    return Integer(len(self._list))

@extend(proto._nth, Array._type)
def _nth(self, idx):
    return self._list[idx.int_val()]


def array(lst):
    assert isinstance(lst, list)
    return Array(lst)

