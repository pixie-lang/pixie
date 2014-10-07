# -*- coding: utf-8 -*-
from pixie.vm.object import Object, Type
from pixie.vm.code import BaseCode, PolymorphicFn, wrap_fn, as_var, defprotocol, extend, Protocol
from types import MethodType
from pixie.vm.primitives import true, false, nil
import pixie.vm.numbers as numbers
import rpython.rlib.jit as jit
import rpython.rlib.rstacklet as rstacklet


defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

defprotocol("pixie.stdlib", "ICounted", ["-count"])

defprotocol("pixie.stdlib", "IIndexed", ["-nth"])

defprotocol("pixie.stdlib", "IPersistentCollection", ["-conj"])

defprotocol("pixie.stdlib", "IObject", ["-hash", "-eq", "-str", "-repr"])

def default_str(x):
    from pixie.vm.string import String

    return String(u"<inst " + x.type()._name + u">")

_str.set_default_fn(wrap_fn(default_str))
_repr.set_default_fn(wrap_fn(default_str))

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
    return numbers.zero_int


_count_driver = jit.JitDriver(name="pixie.stdlib.count",
                              greens=["tp"],
                              reds="auto")
@as_var("count")
def count(x):
    acc = 0
    while True:
        _count_driver.jit_merge_point(tp=rt.type(x))
        if ICounted.satisfies(rt.type(x)):
           return rt._add(numbers.Integer(acc), rt._count(x))
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


@as_var("str")
def str(a):
    return rt._str(a)

@as_var("print")
def _print(a):
    print rt._str(a)._str
    return nil

@as_var("instance?")
def _instance(o, proto):
    assert isinstance(proto, Protocol), "proto must be a Protocol"

    return true if proto.satisfies(o.type()) else false


import pixie.vm.rt as rt


