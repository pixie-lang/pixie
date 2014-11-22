# -*- coding: utf-8 -*-
from pixie.vm.primitives import true, false, nil
from pixie.vm.code import defprotocol, as_global, wrap_fn
from pixie.vm.effects.effects import OpaqueIOFn, raise_Ef, answer_k, Object, Type, Handler, Answer, handle_with, \
    ContinuationThunk, InvokeThunk

from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.effects.environment import link_builtins, throw_Ef, OpaqueIO
from pixie.vm.keyword import keyword
from pixie.vm.string import String
import pixie.vm.rt as rt

import pixie.vm.interfaces

class PrintFn(OpaqueIOFn):
    def __init__(self, str):
        self._str = str

    def execute_opaque_io(self):
        print self._str
        return nil


VALUE_ERROR = keyword(u"VALUE-ERROR")
@as_global("pixie.stdlib", "-print")
@wrap_fn(transform=False)
def print_Ef(s):
    if not isinstance(s, String):
        return throw_Ef(VALUE_ERROR, u"Internal print only accepts strings")
    return OpaqueIO(PrintFn(s.str()))

### Ref

defeffect("pixie.stdlib.Ref", "RefSwap", ["ref", "val"])
defeffect("pixie.stdlib.Ref", "RefGet", ["ref"])

class Ref(Object):
    _type = Type(u"pixie.stdlib.Ref")

    def type(self):
        return Ref._type

    def __init__(self):
        pass


class RefHandler(Handler):
    _immutable_ = True
    def __init__(self, ref, val):
        self._w_ref = ref
        self._w_value = val

    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return effect
        if isinstance(effect, RefSwap) and effect.get(KW_REF) is self._w_ref:
            return handle_with(RefHandler(self._w_ref, effect.get(KW_VAL)),
                               ContinuationThunk(effect.get(KW_K), effect.get(KW_VAL)))
        if isinstance(effect, RefGet) and effect.get(KW_REF) is self._w_ref:
            return handle_with(self,
                               ContinuationThunk(effect.get(KW_K), self._w_value))

@as_global("pixie.stdlib", "-with-ref")
@wrap_fn(transform=False)
def _with_ref(val, fn):
    id = Ref()
    return handle_with(RefHandler(id, val),
                       InvokeThunk(fn, id))

@as_global("pixie.stdlib", "swap-ref")
@wrap_fn(transform=False)
def _swap_ref(ref, val):
    return RefSwap(ref, val)

@as_global("pixie.stdlib", "get-ref")
@wrap_fn(transform=False)
def _swap_ref(ref):
    return RefGet(ref)

@as_global("pixie.stdlib", "eq")
@wrap_fn()
def eq(a, b):
    if a is b:
        return true
    return rt._eq_Ef(a, b)