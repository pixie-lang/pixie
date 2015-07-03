from pixie.vm2.object import Object, Type, affirm, runtime_error
import rpython.rlib.jit as jit
from pixie.vm2.primitives import nil
from rpython.rlib.rarithmetic import r_uint
from pixie.vm2.code import as_var
from pixie.vm2.numbers import Integer, Float
from pixie.vm2.keyword import Keyword, keyword
from pixie.vm2.array import Array
import pixie.vm2.rt as rt

MAX_FIELDS = 32


def make_ctor_fn(type_name, field_names):
    """Constructs a function that will contsruct a Custom type with the given type name
       and field names. The resulting function should be called with a list of Objects."""

    slots = {}
    for idx, val in enumerate(field_names):
        slots[keyword(val)] = idx

    type = CustomType(type_name, slots)

    def ctor(itms):
        return new_inst(type, itms)

    return ctor


class CustomType(Type):
    _immutable_fields_ = ["_slots", "_rev?"]
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

    def custom_type_name(self):
        return self._name

class CustomTypeInstance(Object):
    _immutable_fields_ = ["_type"]
    def __init__(self, type):
        affirm(isinstance(type, CustomType), u"Can't create a instance of a non custom type")
        self._custom_type = type

    def type(self):
        return self._custom_type

    def set_field(self, name, val):
        idx = self._custom_type.get_slot_idx(name)
        assert isinstance(name, Keyword)
        if idx == -1:
            runtime_error(u"Invalid field named " + name._str + u" on type " + self._custom_type.custom_type_name(),
                          u"pixie.stdlib/InvalidFieldException")

        old_val = self.get_field_by_idx(idx)
        if isinstance(old_val, AbstractMutableCell):
            old_val.set_mutable_cell_value(self._custom_type, self, name, idx, val)
        else:
            self._custom_type.set_mutable(name)
            self.set_field_by_idx(idx, val)
        return self

    @jit.elidable_promote()
    def _get_field_immutable(self, idx, rev):
        return self.get_field_by_idx(idx)

    def get_field_immutable(self, idx):
        tp = self._custom_type
        assert isinstance(tp, CustomType)
        return self._get_field_immutable(idx, tp._rev)

    def get_field(self, name, not_found):
        idx = self._custom_type.get_slot_idx(name)
        assert isinstance(name, Keyword)
        if idx == -1:
            return not_found

        if self._custom_type.is_mutable(name):
            value = self.get_field_by_idx(idx)
        else:
            value = self.get_field_immutable(idx)

        if isinstance(value, AbstractMutableCell):
            return value.get_mutable_cell_value()
        else:
            return value


create_type_prefix = """
def new_inst(tp, fields):
    l = len(fields)
    if l >= {max_c}:
        runtime_error(u"Too many fields for type", u"pixie.stdlib/TooManyFields")
"""

clause_template = """
    elif l == {c}:
        return CustomType{c}(tp, fields)
"""

def gen_ct_code():
    acc = create_type_prefix.format(max_c=MAX_FIELDS + 1)
    for x in range(MAX_FIELDS + 1):
        acc += clause_template.format(c=x)

    #print acc
    return acc

exec gen_ct_code()


type_template = """
class CustomType{c}(CustomTypeInstance):
    def __init__(self, tp, fields):
        CustomTypeInstance.__init__(self, tp)
        {self_fields_list} = fields

    def get_field_by_idx(self, idx):
        if idx >= {max}:
            return None
"""

get_field_by_idx_template = """
        elif idx == {c}:
            return self._custom_field{c}
"""

set_field_prefix_template = """
    def set_field_by_idx(self, idx, val):
        if idx >= {max}:
            return
"""

set_field_by_idx_template = """
        elif idx == {c}:
            self._custom_field{c} = val
"""

get_list_template = """
    def get_list(self):
        return {d}

"""

def gen_ct_class_code():
    acc = ""
    for x in range(MAX_FIELDS + 1):
        if x == 0:
            self_fields_list = "_null_"
        elif x == 1:
            self_fields_list = "self._custom_field0,"
        else:
            self_fields_list = ",".join(map(lambda x: "self._custom_field" + str(x), range(x)))
        acc += type_template.format(c=x, self_fields_list=self_fields_list, max=x)
        for y in range(x):
            acc += get_field_by_idx_template.format(c=y)

        acc += set_field_prefix_template.format(max=x)

        for y in range(x):
            acc += set_field_by_idx_template.format(c=y)

        acc += get_list_template.format(d="[" + ", ".join(map(lambda x: "self._custom_field" + str(x), range(x))) + "]")


    #print acc
    return acc

exec gen_ct_class_code()


@as_var("create-type")
def create_type(type_name, fields):
    affirm(isinstance(type_name, Keyword), u"Type name must be a keyword")
    affirm(isinstance(fields, Array), u"Type names must be in an array")
    assert isinstance(fields, Array)
    acc = {}

    for i, val in enumerate(fields._list):
        affirm(isinstance(val, Keyword), u"Field names must be keywords")
        acc[val] = i

    from pixie.vm2.string import String
    assert isinstance(type_name, Keyword)
    return CustomType(type_name._str, acc)

@as_var("new")
@jit.unroll_safe
def _new__args(args):
    affirm(len(args) >= 1, u"new takes at least one parameter")
    tp = args[0]
    affirm(isinstance(tp, CustomType), u"Can only create a new instance of a custom type")
    cnt = len(args) - 1
    affirm(cnt - 1 != tp.get_num_slots(), u"Wrong number of initializer fields to custom type")
    arr = [None] * cnt
    for x in range(cnt):
        val = args[x + 1]
        if isinstance(val, Integer):
            val = IntegerMutableCell(val.int_val())
        elif isinstance(val, Float):
            val = FloatMutableCell(val.float_val())
            
        arr[x] = val
    return new_inst(tp, arr)

@as_var("set-field!")
def set_field(inst, field, val):
    affirm(isinstance(inst, CustomTypeInstance), u"Can only set fields on CustomType instances")
    affirm(isinstance(field, Keyword), u"Field must be a keyword")
    inst.set_field(field, val)
    return inst

@as_var("get-field")
def get_field__args(args):
    if len(args) == 2:
        inst, field = args
        not_found = nil
    elif len(args) == 3:
        inst, field, not_found = args
    else:
        runtime_error(u"Get Field requires one or two args")
        return nil

    affirm(isinstance(inst, CustomTypeInstance), u"Can only get fields on CustomType instances")
    affirm(isinstance(field, Keyword), u"Field must be a keyword")
    return inst.get_field(field, not_found)


class AbstractMutableCell(Object):
    _type = Type(u"pixie.stdlib.AbstractMutableCell")
    def type(self):
        return self._type

    def set_mutable_cell_value(self, ct, fields, nm, idx, value):
        pass

    def get_mutable_cell_value(self):
        pass

class IntegerMutableCell(AbstractMutableCell):
    def __init__(self, int_val):
        self._mutable_integer_val = int_val

    def set_mutable_cell_value(self, ct, fields, nm, idx, value):
        if not isinstance(value, Integer):
            ct.set_mutable(nm)
            if isinstance(value, Float):
                fields.set_field_by_idx(idx, FloatMutableCell(value.float_val()))
            else:
                fields.set_field_by_idx(idx, value)
        else:
            self._mutable_integer_val = value.int_val()

    def get_mutable_cell_value(self):
        return rt.wrap(self._mutable_integer_val)

class FloatMutableCell(AbstractMutableCell):
    def __init__(self, float_val):
        self._mutable_float_val = float_val

    def set_mutable_cell_value(self, ct, fields, nm, idx, value):
        if not isinstance(value, Float):
            ct.set_mutable(nm)
            if isinstance(value, Integer):
                fields.set_field_by_idx(idx, IntegerMutableCell(value.int_val()))
            else:
                fields.set_field_by_idx(idx, value)
        else:
            self._mutable_float_val = value.float_val()

    def get_mutable_cell_value(self):
        return rt.wrap(self._mutable_float_val)