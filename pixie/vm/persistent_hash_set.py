py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.persistent_hash_map as persistent_hash_map
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint, intmask
import rpython.rlib.jit as jit
import pixie.vm.rt as rt

class PersistentHashSet(object.Object):
    _type = object.Type(u"pixie.stdlib.PersistentHashSet")

    def type(self):
        return PersistentHashSet._type

    def __init__(self, m):
        self._map = m

    def conj(self, v):
        return PersistentHashSet(self._map.assoc(v, v))

EMPTY = PersistentHashSet(persistent_hash_map.EMPTY)

@as_var("set")
def _create(coll):
    ret = EMPTY
    coll = rt._seq(coll)
    while coll is not nil:
        ret = ret.conj(rt._first(coll))
        coll = rt._seq(rt._next(coll))
    return ret

@extend(proto._count, PersistentHashSet)
def _count(self):
    assert isinstance(self, PersistentHashSet)
    return rt._count(self._map)

@extend(proto._contains_key, PersistentHashSet)
def _contains_key(self, key):
    assert isinstance(self, PersistentHashSet)
    return rt._contains_key(self._map, key)

@extend(proto._eq, PersistentHashSet)
def _eq(self, obj):
    assert isinstance(self, PersistentHashSet)
    if self is obj:
        return true
    if not isinstance(obj, PersistentHashSet):
        return false
    if self._map._cnt != obj._map._cnt:
        return false

    seq = rt.seq(obj)
    while seq is not nil:
        if rt._contains_key(self, rt.first(seq)) is false:
            return false
        seq = rt.next(seq)
    return true

@extend(proto._conj, PersistentHashSet)
def _conj(self, v):
    assert isinstance(self, PersistentHashSet)
    return self.conj(v)

@extend(proto._reduce, PersistentHashSet)
def _reduce(self, f, init):
    assert isinstance(self, PersistentHashSet)
    return rt._reduce(rt.keys(self._map), f, init)
