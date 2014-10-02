import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint
from pixie.vm.code import DoublePolymorphicFn, extend, Protocol


class Number(object.Object):
    pass



class Integer(Number):
    _type = object.Type("Integer")
    _immutable_fields_ = ["_int_val"]

    def __init__(self, i_val):
        self._int_val = i_val

    def int_val(self):
        return self._int_val

    def r_uint_val(self):
        return r_uint(self._int_val)

    def type(self):
        return Integer._type

zero_int = Integer(0)
one_int = Integer(1)

IMath = Protocol("IMath")
_add = DoublePolymorphicFn("-add", IMath)


@extend(_add, Integer._type, Integer._type)
def _add(a, b):
    return Integer(a.int_val() + b.int_val())


# def add(a, b):
#     if isinstance(a, Integer):
#         if isinstance(b, Integer):
#             return Integer(a.int_val() + b.int_val())
#
#     raise Exception("Add error")

def eq(a, b):
    if isinstance(a, Integer):
        if isinstance(b, Integer):
            return true if a.int_val() == b.int_val() else false

    raise Exception("Add error")

