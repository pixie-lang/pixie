from pixie.vm.effects.effects import Object, Type
from pixie.vm.numbers import Integer
from pixie.vm.primitives import nil, true, false
from pixie.vm.code import extend
import pixie.vm.rt as rt
from rpython.rlib.rarithmetic import intmask, r_uint
from pixie.vm.util import hash_unencoded_chars, hash_int


class String(Object):
    _immutable_ = True
    _immutable_fields_ = ["_str"]
    _type = Type(u"pixie.stdlib.String")

    def type(self):
        return String._type

    def __init__(self, s):
        assert isinstance(s, unicode)
        self._str = s

    def str(self):
        return self._str

class Character(Object):
    _immutable_ = True
    _immutable_fields_ = ["_str"]
    _type = Type(u"pixie.stdlib.Character")

    def type(self):
        return Character._type

    def __init__(self, i):
        assert isinstance(i, int)
        self._char_val = i

    def char_val(self):
        return self._char_val

    def __repr__(self):
        return "\\" + chr(self._char_val)

prebuilts = [None] * 256
for x in range(len(prebuilts)):
    prebuilts[x] = Character(x)

def wrap_char(x):
    if x < 256:
        return prebuilts[x]
    return Character(x)



@extend("pixie.stdlib.-count", String)
def _count(self):
    return Integer(len(self.str()))


@extend("pixie.stdlib.-str", String)
def _str(x):
    return x

@extend("pixie.stdlib.-repr", String)
def _repr(self):
    return String(u"\"" + self.str() + u"\"")

@extend("pixie.stdlib.-nth", String)
def _nth(self, idx):
    i = idx.int_val()
    if 0 <= i < len(self.str()):
        return Character(ord(self.str()[i]))
    return nil
    #raise IndexError()

@extend("pixie.stdlib.-eq", String)
def _eq(self, v):
    if not isinstance(v, String):
        return false
    return true if self.str() == v.str() else false

@extend("pixie.stdlib.-name", String)
def _name(self):
    return self

@extend("pixie.stdlib.-namespace", String)
def _namespace(_):
    return nil

@extend("pixie.stdlib.-hash", String)
def _hash(self):
    return rt.wrap(intmask(hash_unencoded_chars(self.str())))




@extend("pixie.stdlib.-str", Character)
def _str(self):
    cv = self.char_val()
    if cv < 128:
        return rt.wrap(u"\\"+unicode(chr(cv)))
    return rt.wrap(u"\\u"+unicode(str(cv)))

@extend("pixie.stdlib.-repr", Character)
def _repr(self):
    cv = self.char_val()
    if cv < 128:
        return rt.wrap(u"\\"+unicode(chr(cv)))
    return rt.wrap(u"\\u"+unicode(str(cv)))

@extend("pixie.stdlib.-eq", Character)
def _eq(self, obj):
    if self is obj:
        return true
    if not isinstance(obj, Character):
        return false
    return true if self.char_val() == obj.char_val() else false

@extend("pixie.stdlib.-hash", Character)
def _hash(self):
    return rt.wrap(intmask(hash_int(r_uint(self.char_val()))))

