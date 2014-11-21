# -*- coding: utf-8 -*-
from pixie.vm.primitives import true, false, nil
from pixie.vm.code import defprotocol, as_global, wrap_fn
from pixie.vm.effects.effects import OpaqueIOFn, raise_Ef, answer_k, Object, Type, Handler, Answer, handle_with, \
    ContinuationThunk, InvokeThunk

from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.effects.environment import link_builtins, throw_Ef, OpaqueIO
from pixie.vm.keyword import keyword
from pixie.vm.string import String


defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

defprotocol("pixie.stdlib", "ICounted", ["-count"])

defprotocol("pixie.stdlib", "IIndexed", ["-nth"])

defprotocol("pixie.stdlib", "IPersistentCollection", ["-conj", "-disj"])

defprotocol("pixie.stdlib", "IEmpty", ["-empty"])

defprotocol("pixie.stdlib", "IObject", ["-hash", "-eq", "-str", "-repr"])
#_eq.set_default_fn(wrap_fn(lambda a, b: false))

defprotocol("pixie.stdlib", "IReduce", ["-reduce"])

defprotocol("pixie.stdlib", "IDeref", ["-deref"])

defprotocol("pixie.stdlib", "IReset", ["-reset!"])

defprotocol("pixie.stdlib", "INamed", ["-namespace", "-name"])

defprotocol("pixie.stdlib", "IAssociative", ["-assoc", "-contains-key", "-dissoc"])

defprotocol("pixie.stdlib", "ILookup", ["-val-at"])

defprotocol("pixie.stdlib", "IMapEntry", ["-key", "-val"])

defprotocol("pixie.stdlib", "IStack", ["-push", "-pop"])

defprotocol("pixie.stdlib", "IFn", ["-invoke"])

#IVector = as_var("pixie.stdlib", "IVector")(Protocol(u"IVector"))

#IMap = as_var("pixie.stdlib", "IMap")(Protocol(u"IMap"))

defprotocol("pixie.stdlib", "IMeta", ["-with-meta", "-meta"])

defprotocol("pixie.stdlib", "ITransient", ["-persistent!"])
defprotocol("pixie.stdlib", "IToTransient", ["-transient"])

defprotocol("pixie.stdlib", "ITransientCollection", ["-conj!"])

defprotocol("pixie.stdlib", "IIterable", ["-iterator"])
defprotocol("pixie.stdlib", "IIterator", ["-current", "-at-end?", "-move-next!"])

link_builtins("-count", "count")
link_builtins("-first", "first")
link_builtins("-next", "next")


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