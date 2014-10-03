from pixie.vm.object import Object, Type
from pixie.vm.code import BaseCode, PolymorphicFn, wrap_fn, as_var, defprotocol, extend
from types import MethodType
from pixie.vm.primitives import true, false, nil
from pixie.vm.numbers import Integer, zero_int, _add
import rpython.rlib.jit as jit
import rpython.rlib.rstacklet as rstacklet


defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

defprotocol("pixie.stdlib", "ICounted", ["-count"])

defprotocol("pixie.stdlib", "IIndexed", ["-nth"])

defprotocol("pixie.stdlib", "IPersistentCollection", ["-conj"])

#_first = PolymorphicFn("-first")
#_next = PolymorphicFn("-next")

@as_var("first")
def first(x):
    return rt._first(x)

@as_var("next")
def next(x):
    return rt._next(x)

@as_var("seq")
def seq(x):
    return rt._seq(x)


@as_var("type")
def type(x):
    return x.type()


@extend(_first, nil._type)
def _first(_):
    return nil

@extend(_next, nil._type)
def _next(_):
    return nil

@extend(_seq, nil._type)
def _seq(_):
    return nil

@extend(_count, nil._type)
def _count(_):
    return zero_int


_count_driver = jit.JitDriver(name="pixie.stdlib.count",
                              greens=["tp"],
                              reds="auto")
@as_var("count")
def count(x):
    acc = 0
    while True:
        _count_driver.jit_merge_point(tp=rt.type(x))
        if ICounted.satisfies(rt.type(x)):
           return rt._add(Integer(acc), rt._count(x))
        acc += 1
        x = rt.next(rt.seq(x))


@as_var("+")
def add(a, b):
    return rt._add(a, b)

@as_var("conj")
def conj(a, b):
    return rt._conj(a, b)

@as_var("nth")
def nth(a, b):
    return rt._nth(a, b)



import pixie.vm.rt as rt
