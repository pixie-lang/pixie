from pixie.vm.effects.effects import ContinuationThunk, Effect, ArgList, Thunk, Answer, answer_k, Handler, handle_with, \
                                    Object, Type, raise_Ef, _type_registry
from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.effects.effect_transform import cps
from pixie.vm.primitives import nil, true, false
from rpython.rlib.jit import promote, JitDriver
import rpython.rlib.jit as jit
from pixie.vm.keyword import keyword
from pixie.vm.persistent_instance_hash_map import EMPTY as EMPTY_MAP

"""
Environments are immutable, and have the following format:

{:defs {:pixie.stdlib {:-count ProtocolFn(protocol=:pixie.stdlib.ICounted, fn-name=:pixie.stdlib.-count)
                       :-nth ProtocolFn(protocol=:pixie.stdlib.IIndexed, fn_name=:pixie.stdlib.-nth)}}
 :proto-fns {:pixie.stdlib.-count {<type pixie.stdlib.PersistentVector> fn
                                   :default fn
                                   :protocol :pixie.stdlib.ICounted}}
 :protocols {:pixie.stdlib.ICounted {:types {<type pixie.stdlib.PersistentVector> <type pixie.stdlib.PersistentVector>
                                     :fns {:pixie.stdlib.-nth :pixie.stdlib.-nth}}}}

"""
KW_DEFS = keyword(u"defs")
KW_PROTO_FNS = keyword(u"proto-fns")
KW_DOUBLE_PROTO_FNS = keyword(u"double-proto-fns")
KW_DEFAULT = keyword(u"default")
KW_FNS = keyword(u"fns")

KW_TYPES = keyword(u"types")

KW_DOUBLE_PROTOS = keyword(u"double-protos")
KW_RUNNING = keyword(u"running?")
KW_PROTOCOLS = keyword(u"protocols")
KW_TYPES = keyword(u"types")
KW_MEMBERS = keyword(u"members")
KW_PROTOCOL = keyword(u"protocol")


defeffect("pixie.stdlib.Resolve", "Resolve", ["namespace", "name"])
defeffect("pixie.stdlib.Declare", "Declare", ["namespace", "name", "val"])
defeffect("pixie.stdlib.Satisfies?", "Satisfies", ["name", "tp"])
defeffect("pixie.stdlib.FindPolymorphicOverride", "FindPolymorphicOverride", ["name", "tp"])
defeffect("pixie.stdlib.FindDoublePolymorphicOverride", "FindDoublePolymorphicOverride", ["name", "tp1", "tp2"])
defeffect("pixie.stdlib.Exception", "ExceptionEffect", ["kw", "msg"])
defeffect("pixie.stdlib.OpaqueIO", "OpaqueIO", ["effect"])


ExceptionEffect.__repr__ = lambda self: str(self._w_kw.__repr__()) + " : " + str(self._w_msg.str())

class EnvOps(object):

    @staticmethod
    def declare(env, w_ns, w_nm, val):
        return env.assoc_in([KW_DEFS, w_ns, w_nm], val)

    @staticmethod
    def resolve(env, w_ns, w_nm):
        result = env.get_in([KW_DEFS, w_ns, w_nm])
        if result is None:
            tp = _type_registry.get(w_nm.str())
            if tp is not None:
                return tp
        else:
            return result

    @staticmethod
    def make_proto_fn(env, w_ns, w_protocol, w_method_name):
        protocol_kw = keyword(w_ns.str() + u"." + w_protocol.str())
        ns_method_kw = keyword(w_ns.str() + u"." + w_method_name.str())

        pfn = PolymorphicFn(protocol_kw, ns_method_kw)

        env = EnvOps.declare(env, w_ns, w_method_name, pfn)
        env = env.assoc_in([KW_PROTO_FNS, ns_method_kw, KW_PROTOCOL], protocol_kw)
        env = env.assoc_in([KW_PROTOCOLS, protocol_kw, KW_FNS, ns_method_kw], ns_method_kw)
        return env

    @staticmethod
    def make_double_proto_fn(env, w_ns, w_protocol, w_method_name):
        protocol_kw = keyword(w_ns.str() + u"." + w_protocol.str())
        ns_method_kw = keyword(w_ns.str() + u"." + w_method_name.str())

        pfn = DoublePolymorphicFn(protocol_kw, ns_method_kw)

        env = EnvOps.declare(env, w_ns, w_method_name, pfn)
        env = env.assoc_in([KW_DOUBLE_PROTO_FNS, ns_method_kw, KW_PROTOCOL], protocol_kw)
        env = env.assoc_in([KW_PROTOCOLS, protocol_kw, KW_FNS, ns_method_kw], ns_method_kw)
        return env

    @staticmethod
    def extend(env, w_pfn_name, tp, fn):
        protocol = env.get_in([KW_PROTO_FNS, w_pfn_name, KW_PROTOCOL])
        assert protocol is not None, w_pfn_name
        env = env.assoc_in([KW_PROTOCOLS, protocol, KW_TYPES, tp], tp)
        return env.assoc_in([KW_PROTO_FNS, w_pfn_name, tp], fn)

    @staticmethod
    def extend2(env, w_pfn_name, tp1, tp2, fn):
        protocol = env.get_in([KW_DOUBLE_PROTO_FNS, w_pfn_name, KW_PROTOCOL])
        assert protocol is not None, w_pfn_name
        env = env.assoc_in([KW_PROTOCOLS, protocol, KW_TYPES, tp1], tp2)
        return env.assoc_in([KW_DOUBLE_PROTO_FNS, w_pfn_name, tp1, tp2], fn)

    @staticmethod
    def set_default_method(env, w_pfn_name, fn):
        return EnvOps.extend(env, w_pfn_name, KW_DEFAULT, fn)

    @staticmethod
    def set_default_method2(env, w_pfn_name, fn):
        return env.assoc_in([KW_DOUBLE_PROTO_FNS, w_pfn_name, KW_DEFAULT], fn)

    @staticmethod
    def lookup_pfn_method(env, w_pfn_kw, tp):
        fns = env.get_in([KW_PROTO_FNS, w_pfn_kw])
        fn = fns.val_at(tp, None)
        if fn is None:
            fn = fns.val_at(KW_DEFAULT, None)
        return fn

    @staticmethod
    def is_satisfied(env, w_protocol, tp):
        return env.get_in([KW_PROTOCOLS, w_protocol, KW_TYPES, tp]) is not None

    @staticmethod
    def mark_satisfies(env, w_protocol, tp):
        return env.assoc_in([KW_PROTOCOLS, w_protocol, KW_TYPES, tp], tp)

    @staticmethod
    def copy_val(env, w_protocol, frm, to):
        resolved = EnvOps.resolve(env, w_protocol, frm)
        return EnvOps.declare(env, w_protocol, to, resolved)


def mod_builtins(fn, *args):
    global default_env
    default_env = fn(default_env, *args)



def get_printable_location(ast):
    return str(ast)

jitdriver = JitDriver(greens=["ast"], reds=["locals", "thunk", "globals"],
                      virtualizables=["locals"],
                      get_printable_location=get_printable_location)

def raise_polymorphic_arity_exception_Ef():
    from pixie.vm.keyword import keyword
    from pixie.vm.string import String
    return ExceptionEffect(keyword(u"ARITY-ERROR"), String(u"Expected at least 1 arg to polymorphic function"))


def raise_override_error_Ef(name, tp):
    from pixie.vm.keyword import keyword
    from pixie.vm.string import String
    return ExceptionEffect(keyword(u"NO-OVERRIDE"), String(name.str()))

class PolymorphicFn(Object):
    _type = Type(u"pixie.stdlib.PolymorphicFn")

    def type(self):
        return PolymorphicFn._type

    def __init__(self, protocol, name):
        self._w_protocol = protocol
        self._w_name = name

    @cps
    def _invoke_Ef(self, args):
        if args.arg_count() == 0:
            raise_polymorphic_arity_exception_Ef()
            return

        tp = args.get_arg(0).type()
        result = FindPolymorphicOverride(self._w_name, tp).raise_Ef()

        if result is None:
            raise_override_error_Ef(self._w_name, tp)
            return

        return result.invoke_Ef(args)


class DoublePolymorphicFn(Object):
    _type = Type(u"pixie.stdlib.DoublePolymorphicFn")

    def __init__(self, protocol, name):
        self._w_protocol = protocol
        self._w_name = name

    @cps
    def _invoke_Ef(self, args):
        if args.arg_count() <= 1:
            return raise_polymorphic_arity_exception_Ef()

        tp1 = args.get_arg(0).type()
        tp2 = args.get_arg(1).type()
        result = FindDoublePolymorphicOverride(self._w_name, tp1, tp2).raise_Ef()

        if result is None:
            return raise_override_error_Ef(self._w_name, self._type)


        return result.invoke_Ef(args)

class EnvironmentEffect(Effect):
    _immutable_ = True
    """
    defines an effect that needs to interact with the global env
    """
    pass

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
            env = self._w_env
            tp = effect.type()
            if tp is Resolve._type:
                val = EnvOps.resolve(self._w_env, effect.get(KW_NAMESPACE), effect.get(KW_NAME))
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val), answer_k)
            elif tp is Declare._type:
                env = EnvOps.declare(env, effect.get(KW_NAMESPACE), effect.get(KW_NAME), effect.get(KW_VAL))
                return handle_with(EnvironmentHandler(env), ContinuationThunk(effect.get(KW_K), nil), answer_k)
            elif tp is FindPolymorphicOverride._type:
                val = EnvOps.lookup_pfn_method(env, effect.get(KW_NAME), effect.get(KW_TP))
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val), answer_k)
            elif tp is FindDoublePolymorphicOverride._type:
                val = self._w_env.get_in([KW_DOUBLE_PROTO_FNS, effect.get(KW_NAME), effect.get(KW_TP1), effect.get(KW_TP2)])
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val), answer_k)
            elif tp is Satisfies._type:
                val = true if EnvOps.is_satisfied(env, effect.get(KW_NAME), effect.get(KW_TP)) else false
                return handle_with(EnvironmentHandler(self._w_env), ContinuationThunk(effect.get(KW_K), val))

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

class WithDynamicVars(Handler):
    def __init__(self, state):
        self._w_state = state

    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return effect
        if isinstance(effect, Effect):
            tp = effect.type()
            if tp is Resolve._type:
                val = self._w_state.get_in([effect.get(KW_NAMESPACE), effect.get(KW_NAME)])
                if val is not None:
                    return handle_with(WithDynamicVars(self._w_state),
                                       ContinuationThunk(effect.get(KW_K), val))
            if tp is Declare._type:
                val = self._w_state.get_in([effect.get(KW_NAMESPACE), effect.get(KW_NAME)])
                if val is not None:
                    state = self._w_state.assoc_in([effect.get(KW_NAMESPACE), effect.get(KW_NAME)], effect.get(KW_VAL))
                    return handle_with(WithDynamicVars(state),
                                       ContinuationThunk(effect.get(KW_K), effect.get(KW_VAL)))





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

def add_protocol_fn(env, protocol, protofn):
    return env.assoc_in([KW_PROTOS, protofn, KW_PROTOCOL], protocol)

def extend_protocol_fn(env, protofn, tp):
    protocol = env.get_in([KW_PROTOS, protofn, KW_PROTOCOL])
    env = env.assoc_in([KW_PROTOCOLS, protocol, KW_TYPES, tp], tp)
    return env


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