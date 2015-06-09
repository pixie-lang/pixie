import pixie.vm2.object as object
from pixie.vm2.object import affirm
from pixie.vm2.primitives import true, false
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.rbigint import rbigint
import rpython.rlib.jit as jit
from pixie.vm2.code import DoublePolymorphicFn, extend, Protocol, as_var, wrap_fn, munge
#from pixie.vm.libs.pxic.util import add_marshall_handlers
import pixie.vm2.rt as rt

import math

class Number(object.Object):
    _type = object.Type(u"pixie.stdlib.Number")

    def type(self):
        return Number._type



class Integer(Number):
    _type = object.Type(u"pixie.stdlib.Integer", Number._type)
    _immutable_fields_ = ["_int_val"]

    def __init__(self, i_val):
        self._int_val = i_val

    def int_val(self):
        return self._int_val

    def r_uint_val(self):
        return r_uint(self._int_val)

    def type(self):
        return Integer._type

    def to_str(self):
        return unicode(str(self._int_val))

    def to_repr(self):
        return unicode(str(self._int_val))

class SizeT(Integer):
    _type = object.Type(u"pixie.stdlib.SizeT", Integer._type)
    _immutable_fields_ = ["_ruint_val"]

    def __init__(self, val):
        self._ruint_val = r_uint(val)

    def r_uint_val(self):
        return self._ruint_val

    def int_val(self):
        return intmask(self._ruint_val)

    def type(self):
        return self._type

    def to_str(self):
        return unicode(str(self._ruint_val))

    def to_repr(self):
        return unicode(str(self._ruint_val))

zero_int = Integer(0)
one_int = Integer(1)

class BigInteger(Number):
    _type = object.Type(u"pixie.stdlib.BigInteger", Number._type)
    _immutable_fields_ = ["_bigint_val"]

    def __init__(self, bi_val):
        self._bigint_val = bi_val

    def bigint_val(self):
        return self._bigint_val

    def type(self):
        return BigInteger._type

class Float(Number):
    _type = object.Type(u"pixie.stdlib.Float", Number._type)
    _immutable_fields_ = ["_float_val"]

    def __init__(self, f_val):
        self._float_val = f_val

    def float_val(self):
        return self._float_val

    def type(self):
        return Float._type

class Ratio(Number):
    _type = object.Type(u"pixie.stdlib.Ratio", Number._type)
    _immutable_fields_ = ["_numerator", "_denominator"]

    def __init__(self, numerator, denominator):
        assert numerator is not None and denominator is not None
        self._numerator = numerator
        self._denominator = denominator

    def numerator(self):
        return self._numerator

    def denominator(self):
        return self._denominator

    def type(self):
        return Ratio._type

@wrap_fn
def ratio_write(obj):
    assert isinstance(obj, Ratio)
    return rt.vector(rt.wrap(obj.numerator()), rt.wrap(obj.denominator()))

@wrap_fn
def ratio_read(obj):
    return Ratio(rt.nth(obj, rt.wrap(0)).int_val(), rt.nth(obj, rt.wrap(1)).int_val())

#add_marshall_handlers(Ratio._type, ratio_write, ratio_read)

IMath = as_var("IMath")(Protocol(u"IMath"))
_add = as_var("-add")(DoublePolymorphicFn(u"-add", IMath))
_sub = as_var("-sub")(DoublePolymorphicFn(u"-sub", IMath))
_mul = as_var("-mul")(DoublePolymorphicFn(u"-mul", IMath))
_div = as_var("-div")(DoublePolymorphicFn(u"-div", IMath))
_quot = as_var("-quot")(DoublePolymorphicFn(u"-quot", IMath))
_rem = as_var("-rem")(DoublePolymorphicFn(u"-rem", IMath))
_lt = as_var("-lt")(DoublePolymorphicFn(u"-lt", IMath))
_gt = as_var("-gt")(DoublePolymorphicFn(u"-gt", IMath))
_lte = as_var("-lte")(DoublePolymorphicFn(u"-lte", IMath))
_gte = as_var("-gte")(DoublePolymorphicFn(u"-gte", IMath))
_num_eq = as_var("-num-eq")(DoublePolymorphicFn(u"-num-eq", IMath))
_num_eq.set_default_fn(wrap_fn(lambda a, b: false))

#as_var("MAX-NUMBER")(Integer(100000)) # TODO: set this to a real max number


# Ordering of conversions. If a given function is called with two numbers of different
# types, then the type lower on this list will always be upconverted before the opration is
# performed.

number_orderings = [Integer, SizeT, BigInteger, Float]

# Given a value of a certain type, how do we convert it to the *primitive* of another type?
# Notice that conversions for a type to itself must exist, this is then the simple upwrap case.
conversion_templates = {Integer: {Integer: "{x}.int_val()",
                                  SizeT: "{x}.r_uint_val()",
                                  Float: "float({x}.int_val())",
                                  BigInteger: "rbigint.fromint({x}.int_val())"},
                        SizeT:   {SizeT:"{x}.r_uint_val()",
                                  Float:"float({x}.int_val())",
                                  BigInteger:"rbigint.fromint({x}.int_val())"},
                        BigInteger: {BigInteger: "{x}.bigint_val()",
                                     Float: "{x}.bigint_val().tofloat()"},
                        Float:   {Float: "{x}.float_val()"}}

# Given an operation and a type, how do we perform that operation?

operations = {"-add": {Integer: "{x} + {y}",
                       SizeT: "{x} + {y}",
                       BigInteger: "{x}.add({y})",
                       Float: "{x} + {y}"},
              "-sub": {Integer: "{x} - {y}",
                       SizeT: "{x} - {y}",
                       BigInteger: "{x}.sub({y})",
                       Float: "{x} - {y}"},
              "-mul": {Integer: "{x} * {y}",
                       SizeT: "{x} * {y}",
                       BigInteger: "{x}.mul({y})",
                       Float: "{x} * {y}"},
              "-div": {Integer: "{x} / {y}",
                       SizeT: "{x} / {y}",
                       BigInteger: "{x}.div({y})",
                       Float: "{x} / {y}"},
              "-gt": {Integer: "{x} > {y}",
                       SizeT: "{x} > {y}",
                       BigInteger: "{x}.gt({y})",
                       Float: "{x} > {y}"},

              "-lt": {Integer: "{x} < {y}",
                       SizeT: "{x} < {y}",
                       BigInteger: "{x}.lt({y})",
                       Float: "{x} < {y}"},

              "-gte": {Integer: "{x} >= {y}",
                       SizeT: "{x} >= {y}",
                       BigInteger: "{x}.ge({y})",
                       Float: "{x} >= {y}"},

              "-lte": {Integer: "{x} <= {y}",
                       SizeT: "{x} <= {y}",
                       BigInteger: "{x}.le({y})",
                       Float: "{x} <= {y}"},

              "-num-eq": {Integer: "{x} == {y}",
                       SizeT: "{x} == {y}",
                       BigInteger: "{x}.eq({y})",
                       Float: "{x} == {y}"},
              }

# These functions return bool and so should always be returned via rt.wrap
binop_names = {"-gt", "-lt", "-gte", "-lte", "-num-eq"}

# How do we wrap primitives?
wrappers = {Integer: "rt.wrap({x})",
            SizeT: "SizeT({x})",
            BigInteger: "rt.wrap({x})",
            Float: "rt.wrap({x})"}



op_template = """
@extend({pfn}, {t1}._type, {t2}._type)
def {pfn}_{t1}_{t2}(x, y):
    return {result}
"""

def get_rank(t1):
    for idx, tp in enumerate(number_orderings):
        if tp == t1:
            return idx

    assert False, str(t1) + " not found"


def make_num_op(pfn, t1, t2):
    t1rank = get_rank(t1)
    t2rank = get_rank(t2)

    if t1rank >= t2rank:
        t1_conv = t1
        t2_conv = t1
    else:
        t1_conv = t2
        t2_conv = t2

    wrapper = wrappers[t1_conv] if pfn not in binop_names else "rt.wrap({x})"

    result = wrapper.format(x=operations[pfn][t1_conv].format(x=conversion_templates[t1][t1_conv].format(x="x"),
                                                              y=conversion_templates[t2][t2_conv].format(x="y")))

    templated = op_template.format(pfn=munge(pfn),
                                   t1=str(t1._type._name.split(".")[-1]),
                                   t2=str(t2._type._name.split(".")[-1]),
                                   result=result)

    return templated

for pfn in operations:
    for t1 in number_orderings:
        for t2 in number_orderings:
            exec make_num_op(pfn, t1, t2)



def gcd(u, v):
    while v != 0:
        r = u % v
        u = v
        v = r
    return u

@extend(_div, Integer._type, Integer._type)
def _div(n, d):
    assert isinstance(n, Integer) and isinstance(d, Integer)
    nv = n.int_val()
    dv = d.int_val()
    object.affirm(dv != 0, u"Divide by zero")
    g = gcd(nv, dv)
    if g == 0:
        return rt.wrap(0)
    nv = nv / g
    dv = dv / g
    if dv == 1:
        return rt.wrap(nv)
    elif dv == -1:
        return rt.wrap(-1 * nv)
    else:
        if dv < 0:
            nv = nv * -1
            dv = dv * -1
        return Ratio(nv, dv)

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

mixed_op_tmpl = """@extend({pfn}, {ty1}._type, {ty2}._type)
def {pfn}_{ty1}_{ty2}(a, b):
    assert isinstance(a, {ty1}) and isinstance(b, {ty2})
    return rt.{pfn}({conv1}(a), {conv2}(b))
"""

def to_ratio(x):
    if isinstance(x, Ratio):
        return x
    else:
        return Ratio(x.int_val(), 1)

def to_ratio_conv(c):
    if c == Ratio:
        return ""
    else:
        return "to_ratio"

def to_float(x):
    if isinstance(x, Float):
        return x
    if isinstance(x, Ratio):
        return rt.wrap(x.numerator() / float(x.denominator()))
    if isinstance(x, BigInteger):
        return rt.wrap(x.bigint_val().tofloat())
    assert False

def to_float_conv(c):
    if c == Float:
        return ""
    else:
        return "to_float"

def define_mixed_ops():
    for (c1, c2) in [(Integer, Ratio), (Ratio, Integer)]:
        for op in ["_add", "_sub", "_mul", "_div", "_quot", "_rem", "_lt", "_gt", "_lte", "_gte", "_num_eq"]:
            code = mixed_op_tmpl.format(pfn=op, ty1=c1.__name__, ty2=c2.__name__, conv1=to_ratio_conv(c1), conv2=to_ratio_conv(c2))
            exec code

    for (c1, c2) in [(Float, Ratio), (Ratio, Float)]:
        for op in ["_add", "_sub", "_mul", "_div", "_quot", "_rem", "_lt", "_gt", "_lte", "_gte", "_num_eq"]:
            code = mixed_op_tmpl.format(pfn=op, ty1=c1.__name__, ty2=c2.__name__, conv1=to_float_conv(c1), conv2=to_float_conv(c2))
            exec code

    for (c1, c2) in [(Float, BigInteger), (BigInteger, Float)]:
        for op in ["_add", "_sub", "_mul", "_div", "_quot", "_rem", "_lt", "_gt", "_lte", "_gte", "_num_eq"]:
            code = mixed_op_tmpl.format(pfn=op, ty1=c1.__name__, ty2=c2.__name__, conv1=to_float_conv(c1), conv2=to_float_conv(c2))
            exec code

#define_mixed_ops()

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
    import pixie.vm.stdlib as proto
    from pixie.vm.string import String

    @extend(proto._str, Integer._type)
    def _str(i):
        return rt.wrap(unicode(str(i.int_val())))

    @extend(proto._repr, Integer._type)
    def _repr(i):
        return rt.wrap(unicode(str(i.int_val())))

    @extend(proto._str, BigInteger._type)
    def _str(b):
        return rt.wrap(unicode(b.bigint_val().format('0123456789', suffix='N')))

    @extend(proto._repr, BigInteger._type)
    def _repr(b):
        return rt.wrap(unicode(b.bigint_val().format('0123456789', suffix='N')))

    @extend(proto._str, Float._type)
    def _str(f):
        return rt.wrap(unicode(str(f.float_val())))

    @extend(proto._repr, Float._type)
    def _repr(f):
        return rt.wrap(unicode(str(f.float_val())))

    @extend(proto._repr, Ratio._type)
    def _repr(r):
        return rt.wrap(unicode(str(r.numerator()) + "/" + str(r.denominator())))

    @extend(proto._str, Ratio._type)
    def _str(r):
        return rt.wrap(unicode(str(r.numerator()) + "/" + str(r.denominator())))

    @as_var("numerator")
    def numerator(r):
        affirm(isinstance(r, Ratio), u"First argument must be a Ratio")
        return rt.wrap(r.numerator())

    @as_var("denominator")
    def denominator(r):
        affirm(isinstance(r, Ratio), u"First argument must be a Ratio")
        return rt.wrap(r.denominator())

from rpython.rlib.rsre import rsre_re as re
# inspired by https://github.com/clojure/tools.reader/blob/9ee11ed/src/main/clojure/clojure/tools/reader/impl/commons.clj#L45
#                           sign      hex                    oct      radix                           decimal  biginteger
#                           1         2      3               4        5                 6             7        8
int_matcher = re.compile(u'^([-+]?)(?:(0[xX])([0-9a-fA-F]+)|0([0-7]+)|([1-9][0-9]?)[rR]([0-9a-zA-Z]+)|([0-9]*))(N)?$')

float_matcher = re.compile(u'^([-+]?[0-9]+(\.[0-9]*)?([eE][-+]?[0-9]+)?)$')
ratio_matcher = re.compile(u'^([-+]?[0-9]+)/([0-9]+)$')

def parse_int(m):
    sign = 1
    if m.group(1) == u'-':
        sign = -1

    radix = 10

    if m.group(7):
        num = m.group(7)
    elif m.group(2):
        radix = 16
        num = m.group(3)
    elif m.group(4):
        radix = 8
        num = m.group(4)
    elif m.group(5):
        radix = int(m.group(5))
        num = m.group(6)
    else:
        return None

    if m.group(8):
        return rt.wrap(rbigint.fromstr(str(m.group(1) + num), radix))
    else:
        return rt.wrap(sign * int(str(num), radix))

def parse_float(m):
    return rt.wrap(float(str(m.group(0))))

def parse_ratio(m):
    n = int(str(m.group(1)))
    d = int(str(m.group(2)))
    return Ratio(n, d)

def parse_number(s):
    m = int_matcher.match(s)
    if m:
        return parse_int(m)
    else:
        m = float_matcher.match(s)
        if m:
            return parse_float(m)
        else:
            m = ratio_matcher.match(s)
            if m:
                return parse_ratio(m)
            else:
                return None

@as_var(u"-parse-number")
def _parse_number(x):
    from pixie.vm2.string import String
    assert isinstance(x, String)
    return parse_number(x._str)