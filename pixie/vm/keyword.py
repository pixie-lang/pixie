from pixie.vm.object import Object, Type, affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.string import String
import pixie.vm.protocols as proto
from pixie.vm.code import extend, as_var
import pixie.vm.rt as rt

class Keyword(Object):
    _type = Type(u"pixie.stdlib.Keyword")

    def __init__(self, name):
        self._str = name
        self._w_name = None
        self._w_ns = None

    def type(self):
        return Keyword._type

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


class KeywordCache(object):
    def __init__(self):
        self._cache = {}

    def intern(self, nm):
        kw = self._cache.get(nm, None)

        if kw is None:
            kw = Keyword(nm)
            self._cache[nm] = kw

        return kw

_kw_cache = KeywordCache()

def keyword(nm):
    return _kw_cache.intern(nm)


@extend(proto._name, Keyword)
def _name(self):
    self.init_names()
    return self._w_name

@extend(proto._namespace, Keyword)
def _namespace(self):
    self.init_names()
    return self._w_ns

@as_var("keyword")
def _keyword(s):
    affirm(isinstance(s, String), u"Symbol name must be a string")
    return keyword(s._str)