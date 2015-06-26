import pixie.vm2.rt as rt
from pixie.vm2.code import as_var, Var, list_copy, NativeFn
from pixie.vm2.numbers import SizeT
from pixie.vm2.object import affirm, Type, runtime_error
from pixie.vm2.primitives import nil, true, false
import pixie.vm2.code as code
import pixie.vm2.array as array
from rpython.rlib.rarithmetic import r_uint
import pixie.vm2.interpreter as interpreter
import rpython.rlib.jit as jit

@as_var("set-var-root!")
def _set_var_root(v, r):
    assert isinstance(v, Var)
    v.set_root(r)
    return v

@as_var("satisfy")
def satisfy(protocol, tp):
    affirm(isinstance(protocol, code.Protocol), u"First argument must be a protocol")
    affirm(isinstance(tp, Type), u"Second argument must be a type")
    protocol.add_satisfies(tp)
    return protocol

@as_var("pixie.stdlib.internal", "-defprotocol")
def _defprotocol(name, methods):
    from pixie.vm2.string import String
    from pixie.vm2.symbol import Symbol
    affirm(isinstance(name, String), u"protocol name must be a symbol")
    affirm(isinstance(methods, array.Array), u"protocol methods must be an array of symbols")
    assert isinstance(methods, array.Array)
    method_list = []
    for method_sym in methods._list:
        affirm(isinstance(method_sym, String), u"protocol methods must be a vector of symbols")
        assert isinstance(method_sym, String)
        method_list.append(method_sym._str)

    assert isinstance(name, String)
    proto = code.Protocol(name._str)
    name_sym = Symbol(name._str)
    code.intern_var(name_sym.get_ns(), name_sym.get_name()).set_root(proto)
    for method in method_list:
        method = unicode(method)
        poly = code.PolymorphicFn(method,  proto)
        code.intern_var(name_sym.get_ns(), method).set_root(poly)

    return name


@as_var("polymorphic-fn")
def polymorphic_fn(name, protocol):
    from pixie.vm2.string import String
    affirm(isinstance(name, String), u"polymorphic functions must have string names")
    affirm(isinstance(protocol, code.Protocol), u"must be a protocol")
    assert isinstance(name, String)
    return code.PolymorphicFn(name._str, protocol)


@as_var("protocol")
def protocol(name):
    from pixie.vm2.string import String
    affirm(isinstance(name, String), u"Protocol names must be strings")
    assert isinstance(name, String)
    return code.Protocol(name._str)

@as_var("extend")
def _extend(proto_fn, tp, fn):
    if isinstance(proto_fn, interpreter.EffectFunction):
        proto_fn = proto_fn._inner_fn

    if not isinstance(proto_fn, code.PolymorphicFn):
        runtime_error(u"Fist argument to extend should be a PolymorphicFn not a " + proto_fn.type().name())

    affirm(isinstance(tp, Type) or isinstance(tp, code.Protocol), u"Second argument to extend must be a Type or Protocol")
    proto_fn.extend(tp, fn)
    return nil

@as_var("variadic-fn")
def _variadic_fn(required_arity, fn):
    arity = required_arity.int_val()
    return code.VariadicCode(required_arity=arity, code=fn)

@as_var("-effect-fn")
def _variadic_fn(inner_fn):

    return interpreter.EffectFunction(inner_fn)

as_var("-with-handler")(interpreter.WithHandler())

@as_var("multi-arity-fn")
def _multi_arity_fn__args(args):
    from pixie.vm2.string import String
    nm = args[0]
    affirm(isinstance(nm, String), u"Function name must be string")
    assert isinstance(nm, String)
    arities = {}

    required_arity = 0
    rest_fn = None

    idx = 1
    while idx + 1 < len(args):
        arity = args[idx].int_val()
        if arity < 0:
            required_arity = -arity
            rest_fn = args[idx + 1]
        else:
            arities[arity] = args[idx + 1]
        idx += 2

    return code.MultiArityFn(nm._str, arities, required_arity, rest_fn)

class Apply(NativeFn):
    @jit.unroll_safe
    def invoke_k(self, args, stack):
        from pixie.vm2.array import Array
        last_itm = args[len(args) - 1]
        affirm(isinstance(last_itm, Array), u"Final argument in -apply must be an array")
        assert isinstance(last_itm, Array)
        fn = args[0]
        argc = r_uint(len(args) - 2)
        out_args = [None] * (argc + len(last_itm._list))

        list_copy(args, 1, out_args, 0, argc)

        for x in range(len(last_itm._list)):
            out_args[argc + x] = last_itm._list[x]

        return fn.invoke_k(out_args, stack)

as_var("-apply")(Apply())


@as_var("-satisfies?")
def _satisfies(proto, o):
    affirm(isinstance(proto, code.Protocol), u"proto must be a Protocol")

    return true if proto.satisfies(o.type()) else false


@as_var("-instance?")
def _instance(c, o):
    from pixie.vm2.object import istypeinstance
    affirm(isinstance(c, Type), u"c must be a type")

    return true if istypeinstance(o.type(), c) else false


@as_var("-internal-get-field")
def _get_field(inst, k):
    return inst.get_field(k)

@as_var("identical?")
def identical(a, b):
    return true if a is b else false

@as_var("-internal-to-str")
def _internal_to_str(x):
    return rt.wrap(x.to_str())

@as_var("-internal-to-repr")
def _internal_to_repr(x):
    return rt.wrap(x.to_repr())

@as_var("-internal-get-ns")
def _internal_get_ns(x):
    return rt.wrap(x.get_ns())

@as_var("-internal-get-name")
def _internal_get_name(x):
    return rt.wrap(x.get_name())

@as_var("-internal-get-hash")
def _internal_get_name(x):
    return rt.wrap(x.get_hash())


@as_var("-internal-store-hash")
def _internal_store_hash(x, h):
    x.store_hash(h.r_uint_val())
    return nil

@as_var("-internal-int")
def _internal_int(x):
    return rt.wrap(x.int_val())

@as_var("-blocking-println")
def _blocking_println(x):
    print rt.unwrap_string(x)
    return x


@as_var("-string-builder")
def _string_builder():
    from pixie.vm2.string_builder import StringBuilder
    return StringBuilder()

@as_var("-add-to-string-builder")
def _add_to_string_builder(sb, x):
    from pixie.vm2.string import String
    if isinstance(x, String):
        sb.add_str(x._str)
        return sb
    else:
        runtime_error(u"Expected string or char", u"pixie.stdlib.IllegalArgumentException")

@as_var("-finish-string-builder")
def _finish_string_builder(sb):
    return rt.wrap(sb.to_str())

@as_var("size-t")
def size_t(i):
    return SizeT(i.r_uint_val())


@as_var("type")
def type(x):
    return x.type()


@as_var("the-ns")
def the_ns(ns_name):
    affirm(ns_name.get_ns() is None, u"the-ns takes a un-namespaced symbol")

    return code.ns_registry.get(ns_name.get_name(), nil)


@as_var("load-ns")
def load_ns(filename):
    import pixie.vm2.string as string
    import pixie.vm2.symbol as symbol
    import os.path as path

    if isinstance(filename, symbol.Symbol):
        affirm(filename.get_ns() is None, u"load-file takes a un-namespaced symbol")
        filename_str = filename.get_name().replace(u".", u"/") + u".pxi"

        loaded_ns = code.ns_registry.get(filename.get_name(), None)
        if loaded_ns is not None:
            return loaded_ns
    else:
        affirm(isinstance(filename, string.String), u"Filename must be string")
        filename_str = filename.get_name

    # paths = rt.deref(rt.deref(rt.load_paths))
    # f = None
    # for x in range(rt.count(paths)):
    #     path_x = rt.nth(paths, rt.wrap(x))
    #     affirm(isinstance(path_x, string.String), u"Contents of load-paths must be strings")
    #     full_path = path.join(str(rt.name(path_x)), str(filename_str))
    #     if path.isfile(full_path):
    #         f = full_path
    #         break
    #
    # if f is None:
    #     affirm(False, u"File '" + rt.name(filename) + u"' does not exist in any directory found in load-paths")
    # else:
    #     rt.load_file(rt.wrap(f))
    return nil


### NS Helpers

@as_var("-add-refer")
def refer_syms(in_ns_nm, other_ns_nm, as_nm):
    from pixie.vm2.keyword import Keyword
    from pixie.vm2.code import ns_registry

    in_ns = ns_registry.get(in_ns_nm.get_name(), None)
    affirm(in_ns is not None, u"Can't locate namespace " + in_ns_nm.get_name())
    other_ns = ns_registry.get(other_ns_nm.get_name(), None)
    affirm(other_ns is not None, u"Can't locate namespace " + in_ns_nm.get_name())

    in_ns.add_refer(other_ns, as_nm.get_name())

@as_var("-refer-all")
def refer_all(in_ns_nm, other_ns_sym):
    from pixie.vm2.keyword import Keyword
    from pixie.vm2.code import ns_registry

    in_ns = ns_registry.get(in_ns_nm.get_name(), None)
    affirm(in_ns is not None, u"Can't locate namespace " + in_ns_nm.get_name())

    in_ns.get_refer(other_ns_sym.get_name()).refer_all()


@as_var("-refer-var")
def refer_all(in_ns_nm, other_ns_sym, old, new):
    from pixie.vm2.keyword import Keyword
    from pixie.vm2.code import ns_registry

    in_ns = ns_registry.get(in_ns_nm.get_name(), None)
    affirm(in_ns is not None, u"Can't locate namespace " + in_ns_nm.get_name())

    in_ns.get_refer(other_ns_sym.get_name()).add_var_alias(old.get_name(), new.get_name())


@as_var("-in-ns")
def in_ns(ns_name):
    ns = code.ns_registry.find_or_make(ns_name.get_name())
    ns.include_stdlib()

    return nil

@as_var("-run-external-extends")
def run_external_extends():
    for var, tp, f in code.init_ctx:
        var.deref().extend(tp, f)


@as_var("set-dynamic!")
def set_dynamic(var):
    affirm(isinstance(var, Var), u"set-dynamic! expects a var as an argument")
    var.set_dynamic()
    return var


@as_var("resolve-in")
def _var(ns, nm):
    if not isinstance(ns, code.Namespace):
        ns = code.ns_registry.find_or_make(ns.get_name())

    var = ns.resolve_in_ns_ex(nm.get_ns(), nm.get_name())
    return var if var is not None else nil