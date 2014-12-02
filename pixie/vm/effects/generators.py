from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.effects.effects import handle_with, Handler, Object, Type, Answer, ContinuationThunk, InvokeThunk, Effect
from pixie.vm.code import as_global, wrap_fn, extend
from pixie.vm.primitives import nil
from pixie.vm.keyword import keyword
import pixie.vm.rt as rt

defeffect("pixie.stdlib.YieldEffect", "YieldEffect", ["val"])

def yield_Ef(val):
    return YieldEffect(val)

class Generator(Object):
    _type = Type(u"pixie.stdlib.Generator")
    def __init__(self, val, k):
        self._w_val = val
        self._w_k = k

    def val(self):
        return self._w_val

    def k(self):
        return self._w_k

    def invoke_Ef(self, args):
        if args.arg_count() == 0:
            return handle_with(generator_handler,
                               ContinuationThunk(self._w_k, nil))
        elif args.arg_count() == 1:
            return handle_with(generator_handler,
                               ContinuationThunk(self._w_k, args.get_arg(0)))



class GeneratorHandler(Handler):
    def __init__(self):
        pass

    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return effect
        if isinstance(effect, Effect) and effect.type() is YieldEffect._type:
            return ContinuationThunk(k, Generator(effect.get(KW_VAL), effect.get(KW_K)))

generator_handler = GeneratorHandler()

@as_global("pixie.stdlib", "-generator", transform=False)
def _generator(fn):
    return handle_with(generator_handler,
                       InvokeThunk(fn))

@as_global("pixie.stdlib", "generator?", transform=True)
def _generator_(x):
    return rt.wrap(isinstance(x, Generator))

@extend("pixie.stdlib.-deref", Generator)
def _deref(gen):
    return gen.val()

