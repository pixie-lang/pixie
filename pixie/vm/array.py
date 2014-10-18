import pixie.vm.rt as rt
import pixie.vm.object as object
from pixie.vm.code import extend, as_var
from pixie.vm.numbers import Integer
from pixie.vm.primitives import nil
import pixie.vm.protocols as proto
import rpython.rlib.jit as jit

UNROLL_IF_SMALLER_THAN = 8

class Array(object.Object):
    _type = object.Type(u"pixie.stdlib.Array")
    __immutable_fields__ = ["_list[*]"]
    def type(self):
        return Array._type

    def __init__(self, lst):
        self._list = lst

    @jit.unroll_safe
    def reduce_small(self, f, init):
        for x in range(len(self._list)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, self._list[x]])
        return init


    def reduce_large(self, f, init):
        for x in range(len(self._list)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, self._list[x]])
        return init






@extend(proto._count, Array)
def _count(self):
    return rt.wrap(len(self._list))

@extend(proto._nth, Array)
def _nth(self, idx):
    return self._list[idx.int_val()]

@extend(proto._reduce, Array)
def reduce(self, f, init):
    if len(self._list) > UNROLL_IF_SMALLER_THAN:
        return self.reduce_large(f, init)
    return self.reduce_small(f, init)


def array(lst):
    assert isinstance(lst, list)
    return Array(lst)

