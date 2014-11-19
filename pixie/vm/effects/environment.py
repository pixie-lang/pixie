from pixie.vm.effects.effects import ContinuationThunk, Effect, ArgList, Thunk, Answer, ExceptionEffect, OpaqueResource, answer_k
from pixie.vm.primitives import nil
from rpython.rlib.jit import promote, JitDriver



jitdriver = JitDriver(greens=["ast"], reds=["locals", "thunk", "globals"])



class EnvironmentEffect(Effect):
    _immutable_ = True
    """
    defines an effect that needs to interact with the global env
    """
    pass

class Resolve(EnvironmentEffect):
    _immutable_ = True
    def __init__(self, ns, nm):
        self._w_ns = ns
        self._w_nm = nm

    def without_k(self):
        return Resolve(self._w_ns, self._w_nm)

    def execute_effect(self, env):
        ns = env._namespaces.get(self._w_ns, None)
        if ns is None:
            return ContinuationThunk(self._k, promote(None))

        val = ns.get(self._w_nm, None)

        return ContinuationThunk(self._k, promote(val))

def resolve_Ef(ns, nm):
    eff =  Resolve(ns, nm)
    eff._k = answer_k
    return eff

class Declare(EnvironmentEffect):
    _immutable_ = True
    def __init__(self, ns, nm, val):
        self._w_ns = ns
        self._w_nm = nm
        self._w_val = val

    def without_k(self):
        return Declare(self._w_ns, self._w_nm, self._w_val)

    def execute_effect(self, env):
        ns = env._namespaces.get(self._w_ns, None)
        if ns is None:
            ns = {}
            env._namespaces[self._w_ns] = ns

        ns[self._w_nm] = self._w_val

        return ContinuationThunk(self._k, nil)

class FindPolymorphicOverride(EnvironmentEffect):
    _immutable_ = True
    def __init__(self, nm, tp):
        self._w_nm = nm
        self._w_tp = tp

    def without_k(self):
        return FindPolymorphicOverride(self._w_nm, self._w_tp)

    def execute_effect(self, env):
        pfn = env._protos.get(self._w_nm, None)
        if pfn is None:
            return ContinuationThunk(self._k, promote(None))

        return ContinuationThunk(self._k, pfn.get(self._w_tp, None))

class FindDoublePolymorphicOverride(EnvironmentEffect):
    _immutable_ = True
    def __init__(self, nm, tp1, tp2):
        self._w_nm = nm
        self._w_tp1 = tp1
        self._w_tp2 = tp2

    def without_k(self):
        return FindDoublePolymorphicOverride(self._w_nm, self._w_tp1, self._w_tp2)

    def execute_effect(self, env):
        pfn = env._double_protos.get(self._w_nm, None)
        if pfn is None:
            return ContinuationThunk(self._k, promote(None))

        tp1s = pfn.get(self._w_tp1, None)

        if tp1s is None:
            return ContinuationThunk(self._k, promote(None))

        return ContinuationThunk(self._k, tp1s.get(self._w_tp2, None))

class Environment(object):
    """
    Defines a mutable global environment. Can only be accessed via effects
    """
    def __init__(self, ns, protos, double_protos):
        self._namespaces = ns
        self._protos = protos
        self._double_protos = double_protos




def run_with_state(fn, env, arg=None):
    if arg:
        t = fn.invoke_Ef(ArgList([arg]))
    else:
        t = fn.invoke_Ef(ArgList())

    return run_thunk_with_state(t, env)

def run_thunk_with_state(t, env):
    while True:
        if isinstance(t, Thunk):
            (ast, locals) = t.get_loc()
            if ast is not None:
                jitdriver.jit_merge_point(ast=ast, globals=env, locals=locals, thunk=t)
            t = t.execute_thunk()

        elif isinstance(t, Answer):
            return t

        elif isinstance(t, EnvironmentEffect):
            t = t.execute_effect(env)

        #elif isinstance(t, ExceptionEffect):
        #    assert False

        elif isinstance(t, OpaqueResource):
            result = t.execute_resource()
            t = t._k.step(result)

        else:
            assert False, t



_builtin_defs = {}
_builtin_protos = {}
_builtin_double_protos = {}


default_env = Environment(_builtin_defs, _builtin_protos, _builtin_double_protos)

def make_default_env():
    return Environment(_builtin_defs, _builtin_protos, _builtin_double_protos)

def add_builtin(ns, nm, val):
    """NOT_RPYTHON"""
    ns_d = _builtin_defs.get(ns, None)
    if ns_d is None:
        ns_d = {}
        _builtin_defs[ns] = ns_d

    ns_d[nm] = val

def extend_builtin(nm, tp, fn):
    """NOT_RPYTHON"""
    extends = _builtin_protos.get(nm, None)
    if extends is None:
        extends = {}
        _builtin_protos[nm] = extends

    extends[tp] = fn

    return fn

def extend_builtin2(nm, tp, tp2, fn):
    """NOT_RPYTHON"""
    extends = _builtin_double_protos.get(nm, None)
    if extends is None:
        extends = {}
        _builtin_double_protos[nm] = extends

    extends2 = extends.get(tp, None)
    if extends2 is None:
        extends2 = {}
        extends[tp] = extends2

    extends2[tp2] = fn

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
    from pixie.vm.keyword import keyword
    stdlib = keyword(u"pixie.stdlib")
    _builtin_defs[stdlib][keyword(unicode(to))] = _builtin_defs[stdlib][keyword(unicode(frm))]