import rpython.rlib.jit as jit

class Object(object):
    _immutable_fields_ = ["_str"]
    """
    Base class of all Pixie Object
    """
    def _invoke_Ef(self, args):
        """
        Everything is technically invokable, may throw an exception though
        """

    def invoke_Ef(self, args):
        assert isinstance(args, ArgList)
        result = self._invoke_Ef(args)
        assert not isinstance(result, Object) and result is not None, [type(result), self]
        return result

class ArgList(object):
    _immutable_ = True
    _immutable_fields_ = "_args_w[*]"
    def __init__(self, args=[]):
        self._args_w = args

    @jit.unroll_safe
    def append(self, arg):
        old_args = self._args_w
        new_args = [None] * (len(old_args) + 1)
        x = 0
        while x < len(old_args):
            new_args[x] = old_args[x]
            x += 1

        new_args[len(old_args)] = arg
        return ArgList(new_args)

    def get_arg(self, idx):
        return self._args_w[idx]

    def arg_count(self):
        return len(self._args_w)

    def list(self):
        return self._args_w

_type_registry = {}

class Type(Object):
    _immutable_fields_ = ["_name", "_parent"]
    def __init__(self, name, parent = None):
        assert isinstance(name, unicode), u"Type names must be unicode"
        self._name = name
        self._parent = parent
        _type_registry[name] = self

    def type(self):
        return Type._type

    def __repr__(self):
        return "<type " + str(self._name) + ">"

    def __str__(self):
        return self.__repr__()

Type._type = Type(u"Type")

class EffectObject(object):
    """
    Base class for all objects in the effect system. Not a Object so that the rtyper will catch
    at least some typing errors for us
    """
    _immutable_=True

class Effect(EffectObject):
    """
    Base class for any effects
    """
    _immutable_ = True
    pass

    def without_k(self):
        """
        Should clone this object except for the ._k attr
        """
        raise NotImplementedError()

    def raise_Ef(self):
        return self



class OpaqueIOFn(Object):
    """
    Base class for an effect that mutates some resource.
    """
    _type = Type(u"pixie.stdlib.OpaqueIOFn")

    def type(self):
        return OpaqueIOFn._type

    def execute_opaque_io(self):
        raise NotImplementedError()

class Answer(EffectObject):
    """
    If an effect function wants to return an actual value, it should be wrapped in an Answer.
    """
    _immutable_=True
    def __init__(self, w_val):
        assert not isinstance(w_val, EffectObject), w_val
        self._w_val = w_val

    def val(self):
        return self._w_val

class Continuation(Object):
    """
    Defines a computation that should be continued after a given effect has executed.
    """
    _immutable_= True
    _type = Type(u"pixie.stdlib.Continuation")

    def type(self):
        return Continuation._type

    def _step(self, x):
        """
        Continue execution, x is the value returned by the effect.
        """
        raise NotImplementedError()

    def step(self, x):
        assert isinstance(x, Object) or x is None, x
        result = self._step(x)
        assert isinstance(result, EffectObject), [type(result), type(self)]
        return result


class AnswerContinuation(Continuation):
    _immutable_ = True
    def __index__(self):
        pass

    def _step(self, x):
        return answer(x)

answer_k = AnswerContinuation()


class Handler(EffectObject):
    """
    Base class for all handlers.
    """
    _immutable_=True
    def handle(self, effect, k):
        """
        Handle the given affect, calling k when done. Return None if this effect is unhandled with this
        handler. This will cause the effect to bubble up to other handlers.
        """
        raise NotImplementedError()

class Thunk(EffectObject):
    """
    A trampoline. Returning a Thunk will cause control to bubble up to the top of the interpreter before
    being executed.
    """
    _immutable_=True
    def execute_thunk(self):
        raise NotImplementedError()

    def get_loc(self):
        return (None, None)



def answer(x):
    """
    Construct an answer that returns x
    """
    return Answer(x)

def raise_Ef(x, k):
    """
    Used inside @cps transformed functions, recognized by @cps, and the k is automatically supplied. Cannot be called
    in return position. Use thusly

    @cps
    def foo_(x):
      if not x:
        effect = SomeEffect(x)
        result = raise_(effect)  ## @cps provides k to raise_ here

      else:
        result = Integer(42)

      return result

    """

    return x.assoc(KW_K, k)

def handle_with(handler, effect, k=answer_k):
    """
    Installs a handler into the effect stack so that both k and effect are handed to handler after effect has executed.
    """
    assert isinstance(effect, EffectObject), str(effect)
    if isinstance(effect, Thunk):
        return CallEffectFn(handler, effect, k)
    else:
        ret = handler.handle(effect, k)
        if ret is None:
            return effect.assoc(KW_K, HandledEffectExecutingContinuation(handler, effect, k))
        else:
            return ret

class ContinuationThunk(Thunk):
    """
    An Thunk that simply calls k with the provided value.
    """
    _immutable_ = True
    def __init__(self, k, val):
        self._k = k
        self._val = val

    def execute_thunk(self):
        return self._k.step(self._val)

class HandledEffectExecutingContinuation(Continuation):
    """
    Extracts the continuation from the effect and creates a continuation that passes the value to the effect continuation.
    The result of calling the effect is then handles with handler before continuing with k. In essence this converts a
    handler, effect and continuation into a single continuation.
    """
    _immutable_ = True
    def __init__(self, handler, effect, k):
        self._k = k
        self._effect_k = effect.get(KW_K)
        self._handler = handler

    def _step(self, val):
        return handle_with(self._handler, ContinuationThunk(self._effect_k, val), self._k)


class ConstantValContinuation(Continuation):
    """
    Creates a Continuation that always receives a constant value
    """
    def __init__(self, val, k):
        self._w_val = val
        self._w_k = k

    def _step(self, _):
        return self._w_k(self._w_val)


def handle(effect, k):
    return handle_with(default_handler, effect, k)

class CallEffectFn(Thunk):
    """
    Assumes effect is a thunk, calls it then handles it continuing with k.
    """
    _immutable_ = True
    def __init__(self, handler, effect, k):
        self._handler = handler
        self._k = k
        self._effect = effect

    def execute_thunk(self):
        thval = self._effect.execute_thunk()
        assert isinstance(thval, EffectObject), [type(thval), type(self._effect)]
        return handle_with(self._handler, thval, self._k)

    def get_loc(self):
        return self._effect.get_loc()


class HandleRecFn(Handler):
    """
    Internal class for handling recursive effects.
    """
    _immutable_ = True
    def __init__(self, handler, k):
        self._handler = handler
        self._k = k

    def handle_rec(self, arg):
        return handle_with(self._handler, arg, self._k)

## End Handle With

## Default Handler

class DefaultHandler(Handler):
    """
    Defines a handler that calls the continuation when the effect is an Answer
    """
    _immutable_ = True
    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return DefaultHandlerFn(k, effect.val())

default_handler = DefaultHandler()

class DefaultHandlerFn(Thunk):
    """
    Internal Thunk for default_handler
    """
    _immutable_ = True
    def __init__(self, k, val):
        assert isinstance(k, Continuation)
        self._val = val
        self._k = k

    def execute_thunk(self):
        return self._k.step(self._val)

    def get_loc(self):
        return (None, None)

class ConstantValueContinuation(Continuation):
    """
    Creates a Continuation that always returns a value
    """
    def __init__(self, val):
        self._w_val = val

    def _step(self, _):
        return Answer(self._w_val)



## End Default Handler
