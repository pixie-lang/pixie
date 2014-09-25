from loki_vm.vm.object import Object, Type
from loki_vm.vm.primitives import nil, true, false


class Keyword(Object):
    _type = Type("Keyword")

    def __init__(self, name):
        self._name = name


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

