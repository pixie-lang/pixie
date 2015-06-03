import pixie.vm2.rt as rt
from pixie.vm2.code import as_var, Var, list_copy, NativeFn
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

