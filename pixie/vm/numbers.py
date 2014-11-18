from pixie.vm.effects.effects import Object, Type
from pixie.vm.primitives import nil, true, false
from pixie.vm.code import extend
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.rbigint import rbigint
import rpython.rlib.jit as jit
#from pixie.vm.code import DoublePolymorphicFn, extend, Protocol, as_var, wrap_fn
import pixie.vm.rt as rt

import math

class Number(Object):
    _type = Type(u"pixie.stdlib.Number")

    def type(self):
        return Number._type

class Integer(Number):
    _immutable_fields_ = ["_int_val"]
    _type = Type(u"pixie.stdlib.Integer", Number._type)

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

class BigInteger(Number):
    _immutable_fields_ = ["_bigint_val"]

    _type = Type(u"pixie.stdlib.BigInteger", Number._type)

    def __init__(self, bi_val):
        self._bigint_val = bi_val

    def bigint_val(self):
        return self._bigint_val

    def type(self):
        return self._type

class Float(Number):
    _immutable_fields_ = ["_float_val"]

    _type = Type(u"pixie.stdlib.Float", Number._type)

    def __init__(self, f_val):
        self._float_val = f_val

    def float_val(self):
        return self._float_val

    def type(self):
        return Float._type

class Ratio(Number):
    _immutable_fields_ = ["_numerator", "_denominator"]

    _type = Type(u"pixie.stdlib.Ratio", Number._type)
    def __init__(self, numerator, denominator):
        self._numerator = numerator
        self._denominator = denominator

    def numerator(self):
        return self._numerator

    def denominator(self):
        return self._denominator

    def type(self):
        return Ratio._type

# IMath = as_var("IMath")(Protocol(u"IMath"))
# _add = as_var("-add")(DoublePolymorphicFn(u"-add", IMath))
# _sub = as_var("-sub")(DoublePolymorphicFn(u"-sub", IMath))
# _mul = as_var("-mul")(DoublePolymorphicFn(u"-mul", IMath))
# _div = as_var("-div")(DoublePolymorphicFn(u"-div", IMath))
# _quot = as_var("-quot")(DoublePolymorphicFn(u"-quot", IMath))
# _rem = as_var("-rem")(DoublePolymorphicFn(u"-rem", IMath))
# _lt = as_var("-lt")(DoublePolymorphicFn(u"-lt", IMath))
# _gt = as_var("-gt")(DoublePolymorphicFn(u"-gt", IMath))
# _lte = as_var("-lte")(DoublePolymorphicFn(u"-lte", IMath))
# _gte = as_var("-gte")(DoublePolymorphicFn(u"-gte", IMath))
# _num_eq = as_var("-num-eq")(DoublePolymorphicFn(u"-num-eq", IMath))
# _num_eq.set_default_fn(wrap_fn(lambda a, b: false))
#
# as_var("MAX-NUMBER")(Integer(100000)) # TODO: set this to a real max number
#
#
# num_op_template = """@extend({pfn}, {ty1}._type, {ty2}._type)
# def {pfn}_{ty1}_{ty2}(a, b):
#     assert isinstance(a, {ty1}) and isinstance(b, {ty2})
#     return {wrap_start}a.{conv1}() {op} b.{conv2}(){wrap_end}
# """
#
# def extend_num_op(pfn, ty1, ty2, conv1, op, conv2, wrap_start = "rt.wrap(", wrap_end = ")"):
#     tp = num_op_template.format(pfn=pfn, ty1=ty1.__name__, ty2=ty2.__name__,
#                                 conv1=conv1, op=op, conv2=conv2,
#                                 wrap_start=wrap_start, wrap_end=wrap_end)
#     exec tp
#
# extend_num_op("_quot", Integer, Integer, "int_val", "/", "int_val")
# extend_num_op("_rem", Integer, Integer, "int_val", "%", "int_val")
#
# def define_num_ops():
#     # maybe define get_val() instead of using tuples?
#     num_classes = [(Integer, "int_val"), (Float, "float_val")]
#     for (c1, conv1) in num_classes:
#         for (c2, conv2) in num_classes:
#             for (op, sym) in [("_add", "+"), ("_sub", "-"), ("_mul", "*"), ("_div", "/")]:
#                 if op == "_div" and c1 == Integer and c2 == Integer:
#                     continue
#                 extend_num_op(op, c1, c2, conv1, sym, conv2)
#             extend_num_op("_quot", c1, c2, conv1, "/", conv2, wrap_start = "rt.wrap(math.floor(", wrap_end = "))")
#             extend_num_op("_rem", c1, c2, conv1, ",", conv2, wrap_start = "rt.wrap(math.fmod(", wrap_end = "))")
#             for (op, sym) in [("_num_eq", "=="), ("_lt", "<"), ("_gt", ">"), ("_lte", "<="), ("_gte", ">=")]:
#                 extend_num_op(op, c1, c2, conv1, sym, conv2,
#                               wrap_start = "true if ", wrap_end = " else false")
#
# define_num_ops()
#
# bigint_ops_tmpl = """@extend({pfn}, {ty1}._type, {ty2}._type)
# def _{pfn}_{ty1}_{ty2}(a, b):
#     assert isinstance(a, {ty1}) and isinstance(b, {ty2})
#     return rt.wrap({conv1}(a.{get1}()).{op}({conv2}(b.{get2}())))
# """
#
# def define_bigint_ops():
#     num_classes = [(Integer, "rbigint.fromint", "int_val"), (BigInteger, "", "bigint_val")]
#     for (c1, conv1, get1) in num_classes:
#         for (c2, conv2, get2) in num_classes:
#             if c1 == Integer and c2 == Integer:
#                 continue
#             for (pfn, op) in [("_add", "add"), ("_sub", "sub"), ("_mul", "mul"), ("_div", "div"),
#                               ("_num_eq", "eq"), ("_lt", "lt"), ("_gt", "gt"), ("_lte", "le"), ("_gte", "ge")]:
#                 code = bigint_ops_tmpl.format(pfn=pfn, op=op,
#                                               ty1=c1.__name__, conv1=conv1, get1=get1,
#                                               ty2=c2.__name__, conv2=conv2, get2=get2)
#                 exec code
#
# define_bigint_ops()
#
# def gcd(u, v):
#     while v != 0:
#         r = u % v
#         u = v
#         v = r
#     return u
#
# @extend(_div, Integer._type, Integer._type)
# def _div(n, d):
#     assert isinstance(n, Integer) and isinstance(d, Integer)
#     nv = n.int_val()
#     dv = d.int_val()
#     object.affirm(dv != 0, u"Divide by zero")
#     g = gcd(nv, dv)
#     if g == 0:
#         return rt.wrap(0)
#     nv = nv / g
#     dv = dv / g
#     if dv == 1:
#         return rt.wrap(nv)
#     elif dv == -1:
#         return rt.wrap(-1 * nv)
#     else:
#         if dv < 0:
#             nv = nv * -1
#             dv = dv * -1
#         return Ratio(nv, dv)
#
# @extend(_add, Ratio._type, Ratio._type)
# def _add(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return rt._div(rt._add(rt.wrap(b.numerator() * a.denominator()),
#                            rt.wrap(a.numerator() * b.denominator())),
#                    rt.wrap(a.denominator() * b.denominator()))
#
# @extend(_sub, Ratio._type, Ratio._type)
# def _sub(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return rt._div(rt._add(rt.wrap(-1 * b.numerator() * a.denominator()),
#                            rt.wrap(a.numerator() * b.denominator())),
#                    rt.wrap(a.denominator() * b.denominator()))
#
# @extend(_mul, Ratio._type, Ratio._type)
# def _mul(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return rt._div(rt.wrap(b.numerator() * a.numerator()),
#                    rt.wrap(b.denominator() * a.denominator()))
#
# @extend(_div, Ratio._type, Ratio._type)
# def _div(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return rt._div(rt.wrap(b.denominator() * a.numerator()),
#                    rt.wrap(b.numerator() * a.denominator()))
#
# @extend(_quot, Ratio._type, Ratio._type)
# def _quot(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return rt.wrap((a.numerator() * b.denominator()) / (a.denominator() * b.numerator()))
#
# @extend(_rem, Ratio._type, Ratio._type)
# def _rem(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     q = rt.wrap((a.numerator() * b.denominator()) / (a.denominator() * b.numerator()))
#     return rt._sub(a, rt._mul(q, b))
#
# @extend(_lt, Ratio._type, Ratio._type)
# def _lt(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return true if a.numerator() * b.denominator() < b.numerator() * a.denominator() else false
#
# @extend(_gt, Ratio._type, Ratio._type)
# def _gt(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return rt._lt(b, a)
#
# @extend(_lte, Ratio._type, Ratio._type)
# def _lte(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return true if rt._lt(b, a) is false else false
#
# @extend(_gte, Ratio._type, Ratio._type)
# def gte(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return true if rt._lt(a, b) is false else false
#
# @extend(_num_eq, Ratio._type, Ratio._type)
# def _num_eq(a, b):
#     assert isinstance(a, Ratio) and isinstance(b, Ratio)
#     return true if a.numerator() == b.numerator() and a.denominator() == b.denominator() else false
#
# mixed_op_tmpl = """@extend({pfn}, {ty1}._type, {ty2}._type)
# def {pfn}_{ty1}_{ty2}(a, b):
#     assert isinstance(a, {ty1}) and isinstance(b, {ty2})
#     return rt.{pfn}({conv1}(a), {conv2}(b))
# """
#
# def to_ratio(x):
#     if isinstance(x, Ratio):
#         return x
#     else:
#         return Ratio(x.int_val(), 1)
#
# def to_ratio_conv(c):
#     if c == Ratio:
#         return ""
#     else:
#         return "to_ratio"
#
# def to_float(x):
#     if isinstance(x, Float):
#         return x
#     if isinstance(x, Ratio):
#         return rt.wrap(x.numerator() / float(x.denominator()))
#     if isinstance(x, BigInteger):
#         return rt.wrap(x.bigint_val().tofloat())
#     assert False
#
# def to_float_conv(c):
#     if c == Float:
#         return ""
#     else:
#         return "to_float"
#
# def define_mixed_ops():
#     for (c1, c2) in [(Integer, Ratio), (Ratio, Integer)]:
#         for op in ["_add", "_sub", "_mul", "_div", "_quot", "_rem", "_lt", "_gt", "_lte", "_gte", "_num_eq"]:
#             code = mixed_op_tmpl.format(pfn=op, ty1=c1.__name__, ty2=c2.__name__, conv1=to_ratio_conv(c1), conv2=to_ratio_conv(c2))
#             exec code
#
#     for (c1, c2) in [(Float, Ratio), (Ratio, Float)]:
#         for op in ["_add", "_sub", "_mul", "_div", "_quot", "_rem", "_lt", "_gt", "_lte", "_gte", "_num_eq"]:
#             code = mixed_op_tmpl.format(pfn=op, ty1=c1.__name__, ty2=c2.__name__, conv1=to_float_conv(c1), conv2=to_float_conv(c2))
#             exec code
#
#     for (c1, c2) in [(Float, BigInteger), (BigInteger, Float)]:
#         for op in ["_add", "_sub", "_mul", "_div", "_quot", "_rem", "_lt", "_gt", "_lte", "_gte", "_num_eq"]:
#             code = mixed_op_tmpl.format(pfn=op, ty1=c1.__name__, ty2=c2.__name__, conv1=to_float_conv(c1), conv2=to_float_conv(c2))
#             exec code
#
# define_mixed_ops()
#
# # def add(a, b):
# #     if isinstance(a, Integer):
# #         if isinstance(b, Integer):
# #             return Integer(a.int_val() + b.int_val())
# #
# #     raise Exception("Add error")
#
# def eq(a, b):
#     if isinstance(a, Integer):
#         if isinstance(b, Integer):
#             return true if a.int_val() == b.int_val() else false
#
#     raise Exception("Add error")
#
#
# def init():
#     import pixie.vm.stdlib as proto
#     from pixie.vm.string import String
#
#     @extend(proto._str, Integer._type)
#     def _str(i):
#         return rt.wrap(unicode(str(i.int_val())))
#
#     @extend(proto._repr, Integer._type)
#     def _repr(i):
#         return rt.wrap(unicode(str(i.int_val())))
#
#     @extend(proto._str, BigInteger._type)
#     def _str(b):
#         return rt.wrap(unicode(b.bigint_val().format('0123456789', suffix='N')))
#
#     @extend(proto._repr, BigInteger._type)
#     def _repr(b):
#         return rt.wrap(unicode(b.bigint_val().format('0123456789', suffix='N')))
#
#     @extend(proto._str, Float._type)
#     def _str(f):
#         return rt.wrap(unicode(str(f.float_val())))
#
#     @extend(proto._repr, Float._type)
#     def _repr(f):
#         return rt.wrap(unicode(str(f.float_val())))
#
#     @extend(proto._repr, Ratio._type)
#     def _repr(r):
#         return rt.wrap(unicode(str(r.numerator()) + "/" + str(r.denominator())))
#
#     @extend(proto._str, Ratio._type)
#     def _str(r):
#         return rt.wrap(unicode(str(r.numerator()) + "/" + str(r.denominator())))


@extend("pixie.stdlib.-str", Integer)
def _str(i):
    return rt.wrap(unicode(str(i.int_val())))