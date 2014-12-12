import pixie.vm.rt as rt
from pixie.vm.object import Object, Type, affirm
from pixie.vm.code import extend, as_var
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer, _add
import pixie.vm.stdlib as proto
import pixie.vm.util as util
from rpython.rlib.rarithmetic import intmask, r_uint

class String(Object):
    _type = Type(u"pixie.stdlib.String")

    def type(self):
        return String._type

    def __init__(self, s):
        #assert isinstance(s, unicode)
        self._str = s


@extend(proto._str, String)
def _str(x):
    return x

@extend(proto._repr, String)
def _repr(self):
    res = u""
    for c in self._str:
        if c == "\"":
            res += u"\\\""
        elif c == "\n":
            res += u"\\n"
        elif c == "\t":
            res += u"\\t"
        elif c == "\b":
            res += u"\\b"
        elif c == "\f":
            res += u"\\f"
        elif c == "\r":
            res += u"\\r"
        else:
            res += c
    return rt.wrap(u"\"" + res + u"\"")

@extend(proto._count, String)
def _count(self):
    return rt.wrap(len(self._str))

@extend(proto._nth, String)
def _nth(self, idx):
    i = idx.int_val()
    if 0 <= i < len(self._str):
        return Character(ord(self._str[i]))
    raise IndexError()

@extend(proto._eq, String)
def _eq(self, v):
    if not isinstance(v, String):
        return false
    return true if self._str == v._str else false

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



@extend(proto._str, Character)
def _str(self):
    assert isinstance(self, Character)
    cv = self.char_val()
    if cv < 128:
        return rt.wrap(u"\\"+unicode(chr(cv)))
    return rt.wrap(u"\\u"+unicode(str(cv)))

@extend(proto._repr, Character)
def _repr(self):
    assert isinstance(self, Character)
    cv = self.char_val()
    if cv < 128:
        return rt.wrap(u"\\"+unicode(chr(cv)))
    return rt.wrap(u"\\u"+unicode(str(cv)))

@extend(proto._eq, Character)
def _eq(self, obj):
    assert isinstance(self, Character)
    if self is obj:
        return true
    if not isinstance(obj, Character):
        return false
    return true if self.char_val() == obj.char_val() else false

@extend(proto._hash, Character)
def _hash(self):
    return rt.wrap(intmask(util.hash_int(r_uint(self.char_val()))))

@as_var("char")
def char(val):
    affirm(isinstance(val, Integer), u"First argument must be an Integer")
    return Character(val.int_val())

@extend(_add, Character._type, Integer._type)
def _add(a, b):
    assert isinstance(a, Character) and isinstance(b, Integer)
    return rt._add(rt.wrap(a.char_val()), b)

@extend(_add, Character._type, Character._type)
def _add(a, b):
    assert isinstance(a, Character) and isinstance(b, Character)
    return Character(a.char_val() + b.char_val())


@extend(proto._name, String)
def _name(self):
    return self

@extend(proto._namespace, String)
def _namespace(self):
    return nil

@extend(proto._hash, String)
def _hash(self):
    return rt.wrap(intmask(util.hash_unencoded_chars(self._str)))
