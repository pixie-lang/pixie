from pixie.vm.effects.effects import Object, Type
from pixie.vm.numbers import Integer
from pixie.vm.code import extend

class String(Object):
    _type = Type(u"pixie.stdlib.String")

    def type(self):
        return String._type

    def __init__(self, s):
        #assert isinstance(s, unicode)
        self._str = s

@extend("pixie.stdlib.-count", String)
def _count(self):
    return Integer(len(self._str))

#
# @extend(proto._str, String)
# def _str(x):
#     return x
#
# @extend(proto._repr, String)
# def _repr(self):
#     return rt.wrap(u"\"" + self._str + u"\"")
#
#
# @extend(proto._count, String)
# def _count(self):
#     return rt.wrap(len(self._str))
#
# @extend(proto._nth, String)
# def _nth(self, idx):
#     i = idx.int_val()
#     if 0 <= i < len(self._str):
#         return Character(ord(self._str[i]))
#     raise IndexError()
#
# @extend(proto._eq, String)
# def _eq(self, v):
#     if not isinstance(v, String):
#         return false
#     return true if self._str == v._str else false
#
# class Character(Object):
#     _type = Type(u"pixie.stdlib.Character")
#     _immutable_fields_ = ["_char_val"]
#
#     def type(self):
#         return Character._type
#
#     def __init__(self, i):
#         assert isinstance(i, int)
#         self._char_val = i
#
#     def char_val(self):
#         return self._char_val
#
#
#
# @extend(proto._str, Character)
# def _str(self):
#     assert isinstance(self, Character)
#     cv = self.char_val()
#     if cv < 128:
#         return rt.wrap(u"\\"+unicode(chr(cv)))
#     return rt.wrap(u"\\u"+unicode(str(cv)))
#
# @extend(proto._repr, Character)
# def _repr(self):
#     assert isinstance(self, Character)
#     cv = self.char_val()
#     if cv < 128:
#         return rt.wrap(u"\\"+unicode(chr(cv)))
#     return rt.wrap(u"\\u"+unicode(str(cv)))
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
#     return rt.wrap(intmask(util.hash_unencoded_chars(self._str)))
