from pixie.vm.object import Object, Type
from pixie.vm.code import BaseCode, PolymorphicFn, wrap_fn, as_var, defprotocol
from types import MethodType



defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

#_first = PolymorphicFn("-first")
#_next = PolymorphicFn("-next")

@as_var("pixie.stdlib", "first")
def first(x):
    return _first.invoke([x])

@as_var("pixie.stdlib", "next")
def next(x):
    return _next.invoke([x])



