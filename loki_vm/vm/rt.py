from loki_vm.vm.code import as_var
import loki_vm.vm.object as object
import loki_vm.vm.numbers as numbers
from loki_vm.vm.code import BaseCode
from loki_vm.vm.primitives import true, false, nil
from loki_vm.vm.symbol import Symbol
from loki_vm.vm.custom_types import CustomType, CustomTypeInstance
from loki_vm.vm.keyword import Keyword


@as_var("type")
def type(frame, _):
    return frame.pop().type()


@as_var("set-effect!")
def set_effect(frame, argc):
    assert argc == 3
    v = frame.pop()
    c = frame.pop()
    assert isinstance(c, BaseCode)
    c.set_is_effect(v)
    return c

@as_var("+")
def plus(frame, argc):
    acc = numbers.Integer(0)
    assert argc > 1
    for x in range(argc - 1):
        acc = numbers.add(acc, frame.pop())
    return acc


@as_var("make-type")
def make_type(frame, argc):
    fields = frame.pop()
    name = frame.pop()

    assert isinstance(name, Symbol)

    return CustomType(name, fields)

@as_var("new")
def new_(frame, argc):
    tp = frame.nth(argc - 2)
    assert isinstance(tp, CustomType)
    new_inst = CustomTypeInstance(tp)

    x = 0
    while x < (argc - 2):
        new_inst.set_field_by_idx((argc - 3) - x, frame.pop())

        x += 1

    frame.pop()

    return new_inst


@as_var("get-field")
def get_field(frame, argc):
    assert argc == 3

    field_name = frame.pop()
    inst = frame.pop()

    assert isinstance(field_name, Keyword)
    assert isinstance(inst, CustomTypeInstance)

    return inst.get_field(field_name)