from pixie.vm.effects.effects import ContinuationThunk, Effect, ArgList, Thunk, Answer, answer_k, Handler, handle_with
from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.primitives import nil, true
from rpython.rlib.jit import promote, JitDriver
import rpython.rlib.jit as jit
from pixie.vm.keyword import keyword
from pixie.vm.persistent_instance_hash_map import EMPTY as EMPTY_MAP


def get_printable_location(ast):
    return str(ast)

jitdriver = JitDriver(greens=["ast"], reds=["locals", "thunk", "globals"],
                      #virtualizables=["locals"],
                      get_printable_location=get_printable_location)



class EnvironmentEffect(Effect):
    _immutable_ = True
    """
    defines an effect that needs to interact with the global env
    """
    pass

@jit.elidable_promote()
def resolve_in_env(env, ns, nm):
    return env.get_in([KW_DEF, ns, nm])

# class Resolve(EnvironmentEffect):
#     _immutable_ = True
#     def __init__(self, ns, nm):
#         self._w_ns = ns
#         self._w_nm = nm
#
#     def without_k(self):
#         return Resolve(self._w_ns, self._w_nm)
#
#     def execute_effect(self, env):
#         val = resolve_in_env(env, self._w_ns, self._w_nm)
#         return ContinuationThunk(self._k, val), env

defeffect("pixie.stdlib.Resolve", "Resolve", ["namespace", "name"])
defeffect("pixie.stdlib.Declare", "Declare", ["namespace", "name", "val"])
defeffect("pixie.stdlib.FindPolymorphicOverride", "FindPolymorphicOverride", ["name", "tp"])
defeffect("pixie.stdlib.FindDoublePolymorphicOverride", "FindDoublePolymorphicOverride", ["name", "tp1", "tp2"])
defeffect("pixie.stdlib.Exception", "ExceptionEffect", ["kw", "msg"])
defeffect("pixie.stdlib.OpaqueIO", "OpaqueIO", ["effect"])

ExceptionEffect.__repr__ = lambda self: str(self._w_kw.__repr__()) + " : " + str(self._w_msg.str())

def throw_Ef(kw, msg):
    from pixie.vm.string import String
    return ExceptionEffect(kw, String(msg))


def resolve_Ef(ns, nm):
    eff = Resolve(ns, nm, answer_k)
    return eff

def declare_Ef(ns, nm, val):
    return Declare(ns, nm, val)

class EnvironmentHandler(Handler):
    _immutable_ = True
    def __init__(self, env):
        self._w_env = env

    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return effect
        if isinstance(effect, Effect):
            tp = effect.type()
            if tp is Resolve._type:
                val = resolve_in_env(self._w_env, effect.get(KW_NAMESPACE), effect.get(KW_NAME))
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val), answer_k)
            elif tp is Declare._type:
                val = effect.get(KW_VAL)
                env = self._w_env.assoc_in([KW_DEF, effect.get(KW_NAMESPACE), effect.get(KW_NAME)], val)
                return handle_with(EnvironmentHandler(env), ContinuationThunk(effect.get(KW_K), val), answer_k)
            elif tp is FindPolymorphicOverride._type:
                val = self._w_env.get_in([KW_PROTOS, effect.get(KW_NAME), effect.get(KW_TP)])
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val), answer_k)
            elif tp is FindDoublePolymorphicOverride._type:
                val = self._w_env.get_in([KW_DOUBLE_PROTOS, effect.get(KW_NAME), effect.get(KW_TP1), effect.get(KW_TP2)])
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val), answer_k)
        return None


def run_with_state(fn, env, arg=None):
    if arg:
        t = fn.invoke_Ef(ArgList([arg]))
    else:
        t = fn.invoke_Ef(ArgList())

    return run_thunk_with_state(t, env)

def run_thunk_with_state(t, env):
    t = handle_with(EnvironmentHandler(env), t, answer_k)
    while True:
        if isinstance(t, Thunk):
            (ast, locals) = t.get_loc()
            if ast is not None:
                jitdriver.jit_merge_point(ast=ast, globals=env, locals=locals, thunk=t)
            t = t.execute_thunk()

        elif isinstance(t, Answer):
            return t

        #elif isinstance(t, EnvironmentEffect):
        #    t, env = t.execute_effect(env)

        #elif isinstance(t, ExceptionEffect):
        #    assert False

        elif isinstance(t, OpaqueIO):
            effect = t.get(KW_EFFECT)
            result = effect.execute_opaque_io()
            t = t.get(KW_K).step(result)

        else:
            assert False, t

KW_DEF = keyword(u"def")
KW_PROTOS = keyword(u"protos")
KW_DOUBLE_PROTOS = keyword(u"double-protos")
KW_RUNNING = keyword(u"running?")

default_env = EMPTY_MAP

def make_default_env():
    return default_env.assoc(KW_RUNNING, true)

def add_builtin(ns, nm, val):
    """NOT_RPYTHON"""
    global default_env
    default_env = default_env.assoc_in([KW_DEF, ns, nm], val)
    return val

def extend_builtin(nm, tp, fn):
    """NOT_RPYTHON"""
    global default_env
    default_env = default_env.assoc_in([KW_PROTOS, nm, tp], fn)

    return fn

def extend_builtin2(nm, tp1, tp2, fn):
    """NOT_RPYTHON"""
    global default_env
    default_env = default_env.assoc_in([KW_DOUBLE_PROTOS, nm, tp1, tp2], fn)
    return fn

def as_var(ns, name=None):
    """NOT_RPYTHON
    Creates a decorator that will add the supplied value to the list of builtins under the given ns and name
    defaults pixie.stdlib if ns is not specified"""

    from pixie.vm.keyword import keyword

    if name is None:
        name = ns
        ns = "pixie.stdlib"

    name = keyword(name if isinstance(name, unicode) else unicode(name))
    ns = keyword(ns if isinstance(ns, unicode) else unicode(ns))

    def with_fn(fn):
        fn.__real_name__ = name
        #if not isinstance(fn, object.Object):
        #    fn = wrap_fn(fn)
        add_builtin(ns, name, fn)
        return fn

    return with_fn

def link_builtins(frm, to):
    global default_env
    from pixie.vm.keyword import keyword
    stdlib = keyword(u"pixie.stdlib")
    val = default_env.get_in([KW_DEF, stdlib, keyword(frm)])
    default_env = default_env.assoc_in([KW_DEF, stdlib, keyword(to)], val)