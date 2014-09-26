import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint


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

def add(a, b):
    if isinstance(a, Integer):
        if isinstance(b, Integer):
            return Integer(a.int_val() + b.int_val())

    raise Exception("Add error")

def eq(a, b):
    if isinstance(a, Integer):
        if isinstance(b, Integer):
            return true if a.int_val() == b.int_val() else false

    raise Exception("Add error")

