import pixie.vm.rt as rt
from pixie.vm.string import String
from pixie.vm.code import as_var, extend, intern_var, wrap_fn, MultiArityFn
from pixie.vm.object import affirm, runtime_error, Object, Type
import pixie.vm.stdlib as proto
from pixie.vm.keyword import keyword
from pixie.vm.numbers import Integer
from rpython.rlib.clibffi import get_libc_name
from rpython.rlib.unicodedata import unicodedb_6_2_0 as unicodedb
import rpython.rlib.rstring as rstring
import os
import pixie.vm.rt as rt



@as_var("pixie.string", "starts-with")
def startswith(a, b):
    return rt.wrap(rt.name(a).startswith(rt.name(b)))


@as_var("pixie.string", "ends-with")
def endswith(a, b):
    return rt.wrap(rt.name(a).endswith(rt.name(b)))

@as_var("pixie.string", "split")
def split(a, b):
    affirm(rt.count(b) > 0, u"separator can't be empty")
    v = rt.vector()
    for s in rstring.split(rt.name(a), rt.name(b)):
        v = rt.conj(v, rt.wrap(s))
    return v

def index_of2(a, sep):
    return rt.wrap(rt.name(a).find(rt.name(sep)))

def index_of3(a, sep, start):
    affirm(isinstance(start, Integer), u"Third argument must be an integer")
    start = start.int_val()
    if start > 0:
        return rt.wrap(rt.name(a).find(rt.name(sep), start))
    else:
        runtime_error(u"Third argument must be a non-negative integer")

def index_of4(a, sep, start, end):
    affirm(isinstance(start, Integer) and isinstance(end, Integer), u"Third and fourth argument must be integers")
    start = start.int_val()
    end = end.int_val()
    if start > 0 and end > 0:
        return rt.wrap(rt.name(a).find(rt.name(sep), start, end))
    else:
        runtime_error(u"Third and fourth argument must be non-negative integers")

index_of = intern_var(u"pixie.string", u"index-of")
index_of.set_root(MultiArityFn({2: wrap_fn(index_of2), 3: wrap_fn(index_of3), 4: wrap_fn(index_of4)},
                               required_arity = 2))

@as_var("pixie.string", "upper-case")
def upper_case(a):
    a = rt.name(a)
    res = ""
    for ch in a:
        res += chr(unicodedb.toupper(ord(ch)))
    return rt.wrap(res)

@as_var("pixie.string", "lower-case")
def lower_case(a):
    a = rt.name(a)
    res = ""
    for ch in a:
        res += chr(unicodedb.tolower(ord(ch)))
    return rt.wrap(res)

@as_var("pixie.string", "capitalize")
def capitalize(a):
    a = rt.name(a)
    res = u""
    res += unichr(unicodedb.toupper(ord(a[0])))
    res += a[1:]
    return rt.wrap(res)

@as_var("pixie.string", "trim")
def trim(a):
    a = rt.name(a)
    i = 0
    while i < len(a) and unicodedb.isspace(ord(a[i])):
        i += 1
    j = len(a)
    while j > 0 and unicodedb.isspace(ord(a[j - 1])):
        j -= 1
    if j <= i:
        return rt.wrap(u"")
    return rt.wrap(a[i:j])

@as_var("pixie.string", "triml")
def triml(a):
    a = rt.name(a)
    i = 0
    while i < len(a) and unicodedb.isspace(ord(a[i])):
        i += 1
    return rt.wrap(a[i:len(a)])

@as_var("pixie.string", "trimr")
def trimr(a):
    a = rt.name(a)
    j = len(a)
    while j > 0 and unicodedb.isspace(ord(a[j - 1])):
        j -= 1
    if j <= 0:
        return rt.wrap(u"")
    return rt.wrap(a[0:j])
