import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint
import rpython.rlib.jit as jit
from pixie.vm.code import DoublePolymorphicFn, extend, Protocol, as_var, wrap_fn
import pixie.vm.rt as rt

class Number(object.Object):
    pass



class Integer(Number):
    _type = object.Type(u"pixie.stdlib.Integer")
    _immutable_fields_ = ["_int_val"]

    def __init__(self, i_val):
        self._int_val = i_val

    def int_val(self):
        return self._int_val

    def r_uint_val(self):
        return r_uint(self._int_val)

    def promote(self):
        return Integer(jit.promote(self._int_val))

    def type(self):
        return Integer._type

zero_int = Integer(0)
one_int = Integer(1)

class Float(Number):
    _type = object.Type(u"pixie.stdlib.Float")
    _immutable_fields_ = ["_float_val"]

    def __init__(self, f_val):
        self._float_val = f_val

    def float_val(self):
        return self._float_val

    def type(self):
        return Float._type

IMath = as_var("IMath")(Protocol(u"IMath"))
_add = as_var("-add")(DoublePolymorphicFn(u"-add", IMath))
_sub = as_var("-sub")(DoublePolymorphicFn(u"-sub", IMath))
_mul = as_var("-mul")(DoublePolymorphicFn(u"-mul", IMath))
_div = as_var("-div")(DoublePolymorphicFn(u"-div", IMath))
_num_eq = as_var("-num-eq")(DoublePolymorphicFn(u"-num-eq", IMath))
_num_eq.set_default_fn(wrap_fn(lambda a, b: false))



@extend(_add, Integer._type, Integer._type)
def _add(a, b):
    assert isinstance(a, Integer) and isinstance(b, Integer)
    return Integer(a.int_val() + b.int_val())

@extend(_sub, Integer._type, Integer._type)
def _sub(a, b):
    assert isinstance(a, Integer) and isinstance(b, Integer)
    return rt.wrap(a.int_val() - b.int_val())

@extend(_mul, Integer._type, Integer._type)
def _mul(a, b):
    assert isinstance(a, Integer) and isinstance(b, Integer)
    return rt.wrap(a.int_val() * b.int_val())

@extend(_div, Integer._type, Integer._type)
def _div(a, b):
    assert isinstance(a, Integer) and isinstance(b, Integer)
    return rt.wrap(a.int_val() / b.int_val())

@extend(_num_eq, Integer._type, Integer._type)
def _div(a, b):
    assert isinstance(a, Integer) and isinstance(b, Integer)
    return true if a.int_val() == b.int_val() else false


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


@extend(_add, Float._type, Float._type)
def _add(a, b):
    assert isinstance(a, Float) and isinstance(b, Float)
    return Float(a.float_val() + b.float_val())

@extend(_sub, Float._type, Float._type)
def _sub(a, b):
    assert isinstance(a, Float) and isinstance(b, Float)
    return rt.wrap(a.float_val() - b.float_val())

@extend(_mul, Float._type, Float._type)
def _mul(a, b):
    assert isinstance(a, Float) and isinstance(b, Float)
    return rt.wrap(a.float_val() * b.float_val())

@extend(_div, Float._type, Float._type)
def _div(a, b):
    assert isinstance(a, Float) and isinstance(b, Float)
    return rt.wrap(a.float_val() / b.float_val())

@extend(_num_eq, Float._type, Float._type)
def _num_eq(a, b):
    assert isinstance(a, Float) and isinstance(b, Float)
    return true if a.float_val() == b.float_val() else false


def init():
    import pixie.vm.stdlib as proto
    from pixie.vm.string import String

    @extend(proto._str, Integer._type)
    def _str(i):
        return rt.wrap(unicode(str(i.int_val())))

    @extend(proto._repr, Integer._type)
    def _repr(i):
        return rt.wrap(unicode(str(i.int_val())))

    @extend(proto._str, Float._type)
    def _str(i):
        return rt.wrap(unicode(str(i.float_val())))

    @extend(proto._repr, Float._type)
    def _repr(i):
        return rt.wrap(unicode(str(i.float_val())))
