from pixie.vm.code import as_var
import pixie.vm.object as object
import pixie.vm.numbers as numbers
from pixie.vm.code import BaseCode
from pixie.vm.primitives import true, false, nil
from pixie.vm.symbol import Symbol
from pixie.vm.custom_types import CustomType, CustomTypeInstance
from pixie.vm.keyword import Keyword
from rpython.rlib.jit import unroll_safe


@as_var("type")
def type(self, args):
    return args[0].type()


# @as_var("set-effect!")
# def set_effect(self, frame, argc):
#     assert argc == 3
#     v = frame.pop()
#     c = frame.pop()
#     assert isinstance(c, BaseCode)
#     c.set_is_effect(v)
#     return c

@as_var("+")
@unroll_safe
def plus(self, args):
    acc = numbers.Integer(0)
    for x in range(len(args)):
        acc = numbers.add(acc, args[x])
    return acc

#
# @as_var("make-type")
# def make_type(self, frame, argc):
#     fields = frame.pop()
#     name = frame.pop()
#
#     assert isinstance(name, Symbol)
#
#     return CustomType(name, fields)
#
# @as_var("new")
# def new_(self, frame, argc):
#     assert argc >= 2
#     tp = frame.nth(argc - 2)
#     assert isinstance(tp, CustomType)
#     new_inst = CustomTypeInstance(tp)
#
#     x = 0
#     while x < (argc - 2):
#         new_inst.set_field_by_idx((argc - 3) - x, frame.pop())
#
#         x += 1
#
#     frame.pop()
#
#     return new_inst
#
#
# @as_var("get-field")
# def get_field(self, frame, argc):
#     assert argc == 3
#
#     field_name = frame.pop()
#     inst = frame.pop()
#
#     assert isinstance(field_name, Keyword)
#     assert isinstance(inst, CustomTypeInstance)
#
#     return inst.get_field(field_name)