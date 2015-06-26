import pixie.vm2.object as object
from pixie.vm2.primitives import nil, true, false
from pixie.vm2.code import extend, as_var
from pixie.vm2.string import String
import pixie.vm2.rt as rt
#import pixie.vm2.util as util
from rpython.rlib.rarithmetic import intmask, r_uint


class Symbol(object.Object):
    _type = object.Type(u"pixie.stdlib.Symbol")
    def __init__(self, s, meta=nil):
        #assert isinstance(s, unicode)
        self._str = s
        self._w_name = None
        self._w_ns = None
        self._hash = r_uint(0)
        self._meta = meta

    def type(self):
        return Symbol._type

    def init_names(self):
        if self._w_name is None:
            s = self._str.split(u"/")
            if len(s) == 2:
                self._w_ns = rt.wrap(s[0])
                self._w_name = rt.wrap(s[1])
            elif len(s) == 1:
                self._w_name = rt.wrap(s[0])
                self._w_ns = nil
            else:
                self._w_ns = rt.wrap(s[0])
                self._w_name = rt.wrap(u"/".join(s[1:]))

    def with_meta(self, meta):
        return Symbol(self._str, meta)

    def meta(self):
        return self._meta

    def get_name(self):
        self.init_names()
        return rt.unwrap_string(self._w_name)

    def get_ns(self):
        self.init_names()
        return rt.unwrap_string(self._w_ns)


    def to_str(self):
        return self._str

    def to_repr(self):
        return self._str

    def store_hash(self, hash):
        self._hash = hash

    def get_hash(self):
        return self._hash

def symbol(s):
    return Symbol(s)
#
# @extend(proto._eq, Symbol)
# def _eq(self, other):
#     assert isinstance(self, Symbol)
#     if not isinstance(other, Symbol):
#         return false
#     return true if self._str == other._str else false
#
# @extend(proto._str, Symbol)
# def _str(self):
#     assert isinstance(self, Symbol)
#     return rt.wrap(self._str)
#
# @extend(proto._name, Symbol)
# def _name(self):
#     assert isinstance(self, Symbol)
#     self.init_names()
#     return self._w_name
#
# @extend(proto._namespace, Symbol)
# def _namespace(self):
#     assert isinstance(self, Symbol)
#     self.init_names()
#     return self._w_ns
#
# @extend(proto._hash, Symbol)
# def _hash(self):
#     assert isinstance(self, Symbol)
#     if self._hash == 0:
#         self._hash = util.hash_unencoded_chars(self._str)
#     return rt.wrap(intmask(self._hash))
#
@as_var("symbol")
def _symbol(s):
    if not isinstance(s, String):
        from pixie.vm.object import runtime_error
        runtime_error(u"Symbol name must be a string")
    return symbol(s.get_name())
#
#
#
# @extend(proto._meta, Symbol)
# def _meta(self):
#     assert isinstance(self, Symbol)
#     return self.meta()
#
# @extend(proto._with_meta, Symbol)
# def _with_meta(self, meta):
#     assert isinstance(self, Symbol)
#     return self.with_meta(meta)
