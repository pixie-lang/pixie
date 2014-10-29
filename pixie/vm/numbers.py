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

num_op_template = """@extend({pfn}, {ty1}._type, {ty2}._type)
def {pfn}_{ty1}_{ty2}(a, b):
    assert isinstance(a, {ty1}) and isinstance(b, {ty2})
    return {wrap_start}a.{conv1}() {op} b.{conv2}(){wrap_end}
"""

def extend_num_op(pfn, ty1, ty2, conv1, op, conv2, wrap_start = "rt.wrap(", wrap_end = ")"):
    tp = num_op_template.format(pfn=pfn, ty1=ty1.__name__, ty2=ty2.__name__,
                                conv1=conv1, op=op, conv2=conv2,
                                wrap_start=wrap_start, wrap_end=wrap_end)
    exec tp

def def_num_ops():
    # maybe define get_val() instead of using tuples?
    num_classes = [(Integer, "int_val"), (Float, "float_val")]
    for (c1, conv1) in num_classes:
        for (c2, conv2) in num_classes:
            for (op, sym) in [("_add", "+"), ("_sub", "-"), ("_mul", "*"), ("_div", "/")]:
                extend_num_op(op, c1, c2, conv1, sym, conv2)
            extend_num_op("_num_eq", c1, c2, conv1, "==", conv2,
                          wrap_start = "true if ", wrap_end = " else false")

define_num_ops()


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
    def _str(f):
        return rt.wrap(unicode(str(f.float_val())))

    @extend(proto._repr, Float._type)
    def _repr(f):
        return rt.wrap(unicode(str(f.float_val())))
