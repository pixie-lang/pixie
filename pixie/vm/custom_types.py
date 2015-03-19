from pixie.vm.object import Object, Type, affirm, runtime_error
import rpython.rlib.jit as jit
from rpython.rlib.rarithmetic import r_uint
from pixie.vm.code import as_var
from pixie.vm.keyword import Keyword
import pixie.vm.rt as rt

class CustomType(Type):
    __immutable_fields__ = ["_slots", "_rev?"]
    def __init__(self, name, slots):
        Type.__init__(self, name)

        self._slots = slots
        self._mutable_slots = {}
        self._rev = 0

    @jit.elidable_promote()
    def get_slot_idx(self, nm):
        return self._slots.get(nm, -1)

    def set_mutable(self, nm):
        if not self.is_mutable(nm):
            self._rev += 1
            self._mutable_slots[nm] = nm


    @jit.elidable_promote()
    def _is_mutable(self, nm, rev):
        return nm in self._mutable_slots

    def is_mutable(self, nm):
        return self._is_mutable(nm, self._rev)

    @jit.elidable_promote()
    def get_num_slots(self):
        return len(self._slots)

class CustomTypeInstance(Object):
    __immutable_fields__ = ["_type"]
    def __init__(self, type, fields):
        affirm(isinstance(type, CustomType), u"Can't create a instance of a non custom type")
        self._custom_type = type
        self._fields = fields

    def type(self):
        return self._custom_type

    def set_field(self, name, val):
        self._custom_type.set_mutable(name)
        idx = self._custom_type.get_slot_idx(name)
        if idx == -1:
            runtime_error(u"Invalid field named " + rt.name(rt.str(name)) + u" on type " + rt.name(rt.str(self.type())))

        self._fields[idx] = val
        return self

    @jit.elidable_promote()
    def get_field_immutable(self, idx):
        return self._fields[idx]


    def get_field(self, name):
        idx = self._custom_type.get_slot_idx(name)
        if idx == -1:
            runtime_error(u"Invalid field named " + rt.name(rt.str(name)) + u" on type " + rt.name(rt.str(self.type())))

        if self._custom_type.is_mutable(name):
            return self._fields[idx]
        else:
            return self.get_field_immutable(idx)

    def set_field_by_idx(self, idx, val):
        affirm(isinstance(idx, r_uint), u"idx must be a r_uint")
        self._fields[idx] = val
        return self


@as_var("create-type")
def create_type(type_name, fields):
    affirm(isinstance(type_name, Keyword), u"Type name must be a keyword")

    field_count = rt.count(fields)
    acc = {}
    for i in range(rt.count(fields)):
        val = rt.nth(fields, rt.wrap(i))
        affirm(isinstance(val, Keyword), u"Field names must be keywords")
        acc[val] = i


    return CustomType(rt.name(type_name), acc)

@as_var("new")
def _new__args(args):
    affirm(len(args) >= 1, u"new takes at least one parameter")
    tp = args[0]
    affirm(isinstance(tp, CustomType), u"Can only create a new instance of a custom type")
    cnt = len(args) - 1
    affirm(cnt - 1 != tp.get_num_slots(), u"Wrong number of initializer fields to custom type")
    arr = [None] * cnt
    for x in range(cnt):
        arr[x] = args[x + 1]
    return CustomTypeInstance(tp, arr)

@as_var("set-field!")
def set_field(inst, field, val):
    affirm(isinstance(inst, CustomTypeInstance), u"Can only set fields on CustomType instances")
    affirm(isinstance(field, Keyword), u"Field must be a keyword")
    inst.set_field(field, val)
    return inst

@as_var("get-field")
def get_field(inst, field):
    affirm(isinstance(inst, CustomTypeInstance), u"Can only get fields on CustomType instances")
    affirm(isinstance(field, Keyword), u"Field must be a keyword")
    return inst.get_field(field)

