from pixie.vm.object import Object, Type
from pixie.vm.primitives import nil, true, false
import rpython.rlib.jit as jit
from pixie.vm.numbers import Integer
from rpython.rlib.rarithmetic import r_uint
from pixie.vm.code import as_var
from pixie.vm.symbol import Symbol
from pixie.vm.string import String
from pixie.vm.keyword import Keyword
import pixie.vm.rt as rt

class CustomType(Type):
    __immutable_fields__ = ["_slots"]
    def __init__(self, name, slots):
        Type.__init__(self, name)

        self._slots = slots

    @jit.elidable_promote()
    def get_slot_idx(self, nm):
        return self._slots[nm]

    @jit.elidable_promote()
    def get_num_slots(self):
        return len(self._slots)

class CustomTypeInstance(Object):
    __immutable_fields__ = ["_type"]
    def __init__(self, type):
        assert isinstance(type, CustomType)
        self._type = type
        self._fields = [None] * self._type.get_num_slots()

    def type(self):
        return self._type

    def set_field(self, name, val):
        idx = self._type.get_slot_idx(name)
        self._fields[idx] = val
        return self

    def get_field(self, name):
        idx = self._type.get_slot_idx(name)
        return self._fields[idx]

    def set_field_by_idx(self, idx, val):
        assert isinstance(idx, r_uint)
        self._fields[idx] = val
        return self


@as_var("create-type")
def create_type(type_name, fields):
    assert isinstance(type_name, Keyword), "Type name must be a keyword"

    field_count = rt.count(fields).int_val()
    acc = {}
    for i in range(rt.count(fields).int_val()):
        val = rt.nth(fields, Integer(i))
        assert isinstance(val, Keyword), "Field names must be keywords"
        acc[val] = i


    return CustomType(type_name._name, acc)

@as_var("new")
def _new(tp):
    assert isinstance(tp, CustomType), "Can only create a new instance of a custom type"
    return CustomTypeInstance(tp)

@as_var("set-field!")
def set_field(inst, field, val):
    assert isinstance(inst, CustomTypeInstance), "Can only set fields on CustomType instances"
    assert isinstance(field, Keyword), "Field must be a keyword"
    inst.set_field(field, val)
    return inst

@as_var("get-field")
def get_field(inst, field):
    assert isinstance(inst, CustomTypeInstance), "Can only get fields on CustomType instances"
    assert isinstance(field, Keyword), "Field must be a keyword"
    return inst.get_field(field)

