import pixie.vm2.rt as rt
from pixie.vm2.object import Object, Type, affirm
from pixie.vm2.code import extend, as_var, wrap_fn
from pixie.vm2.primitives import nil, true, false
from pixie.vm2.numbers import Integer
#import pixie.vm2.stdlib as proto
#import pixie.vm2.util as util
from rpython.rlib.rarithmetic import intmask, r_uint
import rpython.rlib.jit as jit
#from pixie.vm2.libs.pxic.util import add_marshall_handlers

class String(Object):
    _type = Type(u"pixie.stdlib.String")

    def type(self):
        return String._type

    def __init__(self, s):
        #assert isinstance(s, unicode)
        self._str = s


@as_var("-str-len")
def str_len(self):
    assert isinstance(self, String)
    return rt.wrap(len(self._str))

@as_var("-str-nth")
def str_len(self, idx):
    assert isinstance(self, String)
    i = idx.int_val()
    return char_cache.intern(ord(self._str[i]))




#
#
# @extend(proto._str, String)
# def _str(x):
#     return x
#
# @extend(proto._repr, String)
# def _repr(self):
#     res = u""
#     assert isinstance(self, String)
#     for c in self._str:
#         if c == "\"":
#             res += u"\\\""
#         elif c == "\n":
#             res += u"\\n"
#         elif c == "\t":
#             res += u"\\t"
#         elif c == "\b":
#             res += u"\\b"
#         elif c == "\f":
#             res += u"\\f"
#         elif c == "\r":
#             res += u"\\r"
#         else:
#             res += c
#     return rt.wrap(u"\"" + res + u"\"")
#
# @extend(proto._count, String)
# def _count(self):
#     assert isinstance(self, String)
#     return rt.wrap(len(self._str))
#
# @extend(proto._nth, String)
# def _nth(self, idx):
#     assert isinstance(self, String)
#     i = idx.int_val()
#     if 0 <= i < len(self._str):
#         return Character(ord(self._str[i]))
#     affirm(False, u"Index out of Range")
#
# @extend(proto._nth_not_found, String)
# def _nth_not_found(self, idx, not_found):
#     assert isinstance(self, String)
#     i = idx.int_val()
#     if 0 <= i < len(self._str):
#         return Character(ord(self._str[i]))
#     return not_found
#
# @extend(proto._eq, String)
# def _eq(self, v):
#     assert isinstance(self, String)
#     if not isinstance(v, String):
#         return false
#     return true if self._str == v._str else false
#
class Character(Object):
    _type = Type(u"pixie.stdlib.Character")
    _immutable_fields_ = ["_char_val"]

    def type(self):
        return Character._type

    def __init__(self, i):
        assert isinstance(i, int)
        self._char_val = i

    def char_val(self):
        return self._char_val


    def to_str(self):
        assert isinstance(self, Character)
        return rt.wrap(u"" + unichr(self.char_val()))

    def to_repr(self):
        assert isinstance(self, Character)
        cv = self.char_val()
        if cv < 128:
            return rt.wrap(u"\\"+unicode(chr(cv)))
        hexv = rt.name(rt.bit_str(rt.wrap(self.char_val()), rt.wrap(4)))
        return rt.wrap(u"\\u" + u"0" * (4 - len(hexv)) + hexv)

class CharCache(object):
    def __init__(self):
        self._char_cache = {}
        self._rev = 0

    @jit.elidable_promote()
    def intern_inner(self, ival, rev):
        return self._char_cache.get(ival, None)

    def intern(self, ival):
        v = self.intern_inner(ival, self._rev)
        if not v:
            v = Character(ival)
            self._char_cache[ival] = v
            self._rev += 1

        return v


char_cache = CharCache()

@as_var("char")
def char(val):
    affirm(isinstance(val, Integer), u"First argument must be an Integer")
    return char_cache.intern(val.int_val())


# @wrap_fn
# def write_char(obj):
#     assert isinstance(obj, Character)
#     return rt.wrap(obj._char_val)
#
# @wrap_fn
# def read_char(obj):
#     return Character(obj.int_val())
#
# add_marshall_handlers(Character._type, write_char, read_char)
#
# @extend(proto._str, Character)
# def _str(self):
#     assert isinstance(self, Character)
#     return rt.wrap(u"" + unichr(self.char_val()))
#
# @extend(proto._repr, Character)
# def _repr(self):
#     assert isinstance(self, Character)
#     cv = self.char_val()
#     if cv < 128:
#         return rt.wrap(u"\\"+unicode(chr(cv)))
#     hexv = rt.name(rt.bit_str(rt.wrap(self.char_val()), rt.wrap(4)))
#     return rt.wrap(u"\\u" + u"0" * (4 - len(hexv)) + hexv)
#
# @extend(proto._eq, Character)
# def _eq(self, obj):
#     assert isinstance(self, Character)
#     if self is obj:
#         return true
#     if not isinstance(obj, Character):
#         return false
#     return true if self.char_val() == obj.char_val() else false
#
# @extend(proto._hash, Character)
# def _hash(self):
#     return rt.wrap(intmask(util.hash_int(r_uint(self.char_val()))))
#
# @as_var("char")
# def char(val):
#     affirm(isinstance(val, Integer), u"First argument must be an Integer")
#     return Character(val.int_val())
#
# @extend(_add, Character._type, Integer._type)
# def _add(a, b):
#     assert isinstance(a, Character) and isinstance(b, Integer)
#     return rt._add(rt.wrap(a.char_val()), b)
#
# @extend(_add, Character._type, Character._type)
# def _add(a, b):
#     assert isinstance(a, Character) and isinstance(b, Character)
#     return Character(a.char_val() + b.char_val())
#
#
# @extend(proto._name, String)
# def _name(self):
#     return self
#
# @extend(proto._namespace, String)
# def _namespace(self):
#     return nil
#
# @extend(proto._hash, String)
# def _hash(self):
#     assert isinstance(self, String)
#     return rt.wrap(intmask(util.hash_unencoded_chars(self._str)))
