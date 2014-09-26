from pixie.vm.object import Object, Type
from pixie.vm.primitives import nil, true, false
from rpython.rlib.jit import elidable, promote
from pixie.vm.numbers import Integer
from rpython.rlib.rarithmetic import r_uint

class CustomType(Type):
    __immutable_fields__ = ["slots"]
    def __init__(self, name, slots_s):
        Type.__init__(self, name)
        slots = {}

        idx = 0
        while slots_s is not nil:
            slots[slots_s.first()] = len(slots)
            slots_s = slots_s.next()

        self._slots = slots

    @elidable
    def get_slot_idx(self, nm):
        return self._slots[nm]

class CustomTypeInstance(Object):
    __immutable_fields__ = ["_type"]
    def __init__(self, type):
        assert isinstance(type, CustomType)
        self._type = type
        self._fields = [None] * len(type._slots)

    def set_field(self, name, val):
        idx = promote(self._type.get_slot_idx(name))
        self._fields[idx] = val
        return self

    def get_field(self, name):
        idx = promote(self._type.get_slot_idx(name))
        return self._fields[idx]

    def set_field_by_idx(self, idx, val):
        assert isinstance(idx, r_uint)
        self._fields[idx] = val
        return self




