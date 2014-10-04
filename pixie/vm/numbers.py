import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint
from pixie.vm.code import DoublePolymorphicFn, extend, Protocol, as_var


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

IMath = as_var("IMath")(Protocol("IMath"))
_add = as_var("-add")(DoublePolymorphicFn("-add", IMath))
_sub = as_var("-sub")(DoublePolymorphicFn("-sub", IMath))
_mul = as_var("-mul")(DoublePolymorphicFn("-mul", IMath))
_div = as_var("-div")(DoublePolymorphicFn("-div", IMath))


@extend(_add, Integer._type, Integer._type)
def _add(a, b):
    return Integer(a.int_val() + b.int_val())

@extend(_sub, Integer._type, Integer._type)
def _sub(a, b):
    return Integer(a.int_val() - b.int_val())

@extend(_mul, Integer._type, Integer._type)
def _mul(a, b):
    return Integer(a.int_val() * b.int_val())

@extend(_div, Integer._type, Integer._type)
def _div(a, b):
    return Integer(a.int_val() / b.int_val())


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


def init():
    import pixie.vm.protocols as proto
    from pixie.vm.string import String

    @extend(proto._str, Integer._type)
    def _str(i):
        return String(str(i.int_val()))

    @extend(proto._repr, Integer._type)
    def _repr(i):
        return String(str(i.int_val()))


