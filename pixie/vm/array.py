import pixie.vm.rt as rt
from pixie.vm.effects.effects import Object, Type
from pixie.vm.primitives import nil
from pixie.vm.code import extend
import pixie.vm.stdlib as proto
import rpython.rlib.jit as jit
from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rarithmetic import build_int

UNROLL_IF_SMALLER_THAN = 8

class Array(Object):
    _type = Type(u"pixie.stdlib.Array")
    __immutable_fields__ = ["_list[*]"]
    def type(self):
        return Array._type

    def __init__(self, lst):
        self._list = lst

    def list(self):
        return self._list

    # @jit.unroll_safe
    # def reduce_small(self, f, init):
    #     for x in range(len(self._list)):
    #         if rt.reduced_QMARK_(init):
    #             return rt.deref(init)
    #         init = f.invoke([init, self._list[x]])
    #     return init
    #
    #
    # def reduce_large(self, f, init):
    #     for x in range(len(self._list)):
    #         if rt.reduced_QMARK_(init):
    #             return rt.deref(init)
    #         init = f.invoke([init, self._list[x]])
    #     return init

@extend("pixie.stdlib.-count", Array)
def _count(self):
    return rt.wrap(len(self.list()))

@extend("pixie.stdlib.-nth", Array)
def _nth(self, idx):
    ival = idx.int_val()
    if ival < len(self.list()):
        return self.list()[ival]
    else:
        return nil


def array(lst):
    return Array(lst)
