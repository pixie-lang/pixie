import pixie.vm.rt as rt
from pixie.vm.object import Object, Type
from pixie.vm.code import extend, as_var
from pixie.vm.primitives import nil
import pixie.vm.protocols as proto
import pixie.vm.numbers as numbers
import pixie.vm.util as util

class String(Object):
    _type = Type(u"pixie.stdlib.String")

    def type(self):
        return String._type

    def __init__(self, s):
        assert isinstance(s, unicode)
        self._str = s


@extend(proto._str, String)
def _str(x):
    return x

@extend(proto._repr, String)
def _repr(self):
    return String(u"\"" + self._str + u"\"")


@extend(proto._count, String)
def _count(self):
    return numbers.Integer(len(self._str))

@extend(proto._nth, String)
def _nth(self, idx):
    i = idx.int_val()
    if 0 <= i < len(self._str):
        return Character(ord(self._str[i]))
    raise IndexError()


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
    cv = self.char_val()
    if cv < 128:
        return String(u"\\"+unicode(chr(cv)))
    return String(u"\\u"+unicode(str(cv)))

@extend(proto._repr, Character)
def _repr(self):
    cv = self.char_val()
    if cv < 128:
        return String(u"\\"+unicode(chr(cv)))
    return String(u"\\u"+unicode(str(cv)))


@extend(proto._name, String)
def _name(self):
    return self

@extend(proto._namespace, String)
def _namespace(self):
    return nil

@extend(proto._hash, String)
def _hash(self):
    return numbers.Integer(util.hash_unencoded_chars(self._str))