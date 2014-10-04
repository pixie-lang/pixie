py_object = object
import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.jit import elidable, elidable_promote, promote


BYTECODES = ["LOAD_CONST",
             "ADD",
             "EQ",
             "INVOKE",
             "TAIL_CALL",
             "DUP_NTH",
             "RETURN",
             "COND_BR",
             "JMP",
             "CLOSED_OVER",
             "MAKE_CLOSURE",
             "SET_VAR",
             "POP",
             "DEREF_VAR",
             "INSTALL",
             "RECUR",
             "ARG",
             "PUSH_SELF",
             "POP_UP_N"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)

# class TailCall(object.Object):
#     _type = object.Type("TailCall")
#     __immutable_fields_ = ["_f", "_args"]
#     def __init__(self, f, args):
#         self._f = f
#         self._args = args
#
#     def run(self):
#         return self._f._invoke(self._args)


class BaseCode(object.Object):
    def __init__(self):
        pass

    def _invoke(self, args):
        raise NotImplementedError()

    def get_consts(self):
        raise NotImplementedError()

    def get_bytecode(self):
        raise NotImplementedError()

    def stack_size(self):
        return 0

    def invoke(self, args):
        result = self._invoke(args)
        return result




class NativeFn(BaseCode):
    """Wrapper for a native function"""
    _type = object.Type(u"NativeFn")

    def __init__(self):
        BaseCode.__init__(self)

    def type(self):
        return NativeFn._type

    def _invoke(self, args):
        return self.inner_invoke(args)

    def inner_invoke(self, args):
        raise NotImplementedError()


class Code(BaseCode):
    """Interpreted code block. Contains consts and """
    _type = object.Type(u"Code")
    __immutable_fields__ = ["_consts[*]", "_bytecode"]

    def type(self):
        return Code._type

    def __init__(self, name, bytecode, consts, stack_size):
        BaseCode.__init__(self)
        self._bytecode = bytecode
        self._consts = consts
        self._name = name
        self._stack_size = stack_size

    def _invoke(self, args):
        return interpret(self, args)

    def get_consts(self):
        return self._consts

    def get_bytecode(self):
        return self._bytecode

    def stack_size(self):
        return self._stack_size

class Closure(Code):
    _type = object.Type(u"Closure")
    __immutable_fields__ = ["_closed_overs[*]", "_code"]
    def type(self):
        return Closure._type

    def __init__(self, code, closed_overs):
        BaseCode.__init__(self)
        self._code = code
        self._closed_overs = closed_overs

    def _invoke(self, args):
        return interpret(self, args)

    def get_closed_over(self, idx):
        return self._closed_overs[idx]

    def get_consts(self):
        return self._code.get_consts()

    def get_bytecode(self):
        return self._code.get_bytecode()

    def stack_size(self):
        return self._code._stack_size

class Undefined(object.Object):
    _type = object.Type(u"Undefined")

    def type(self):
        return Undefined._type

undefined = Undefined()

class Var(BaseCode):
    _type = object.Type(u"Var")
    _immutable_fields_ = ["_rev?"]

    def type(self):
        return Var._type

    def __init__(self, name):
        self._name = name
        self._rev = 0
        self._root = undefined

    def set_root(self, o):
        self._rev += 1
        self._root = o
        return self

    @elidable
    def get_root(self, rev):
        return self._root


    def deref(self):
        rev = promote(self._rev)
        val = self.get_root(rev)
        assert val is not undefined
        return val

    def _invoke(self, args):
        return self.deref().invoke(args)


class Namespace(py_object):
    def __init__(self, name):
        self._registry = {}
        self._name = name

    def intern_or_make(self, name):
        assert isinstance(name, unicode)
        v = self._registry.get(name, None)
        if v is None:
            v = Var(name).set_root(nil)
            self._registry[name] = v
        return v

    def get(self, name, default):
        return self._registry.get(name, default)

class NamespaceRegistry(py_object):
    def __init__(self):
        self._registry = {}

    def find_or_make(self, name):
        assert isinstance(name, unicode), name + " is not unicode"
        v = self._registry.get(name, None)
        if v is None:
            v = Namespace(name)
            self._registry[name] = v
        return v


    def get(self, name, default):
        return self._registry.get(name, default)

_ns_registry = NamespaceRegistry()

def intern_var(ns, name=None):
    if name is None:
        name = ns
        ns = u""

    return _ns_registry.find_or_make(ns).intern_or_make(name)

def get_var_if_defined(ns, name):
    w_ns = _ns_registry.get(ns, None)
    if w_ns is None:
        return None
    return w_ns.get(name, None)




class DefaultProtocolFn(NativeFn):
    def __init__(self, pfn):
        self._pfn = pfn

    def _invoke(self, args):
        from pixie.vm.string import String
        tp = args[0].type()._name
        raise Exception(u"No override for " + tp + u" on " + self._pfn._name + u" in protocol " + self._pfn._protocol._name)


class Protocol(object.Object):
    _type = object.Type(u"Protocol")

    def __init__(self, name):
        self._name = name
        self._polyfns = {}
        self._satisfies = {}


    def add_method(self, pfn):
        self._polyfns[pfn] = pfn

    def add_satisfies(self, tp):
        self._satisfies[tp] = tp

    def satisfies(self, tp):
        return tp in self._satisfies


class PolymorphicFn(BaseCode):
    _type = object.Type(u"PolymorphicFn")

    __immutable_fields__ = ["_rev?"]
    def __init__(self, name, protocol):
        self._name = name
        self._dict = {}
        self._rev = 0
        self._protocol = protocol
        self._default_fn = DefaultProtocolFn(self)
        protocol.add_method(self)

    def extend(self, tp, fn):
        self._dict[tp] = fn
        self._rev += 1
        self._protocol.add_satisfies(tp)

    def set_default_fn(self, fn):
        self._default_fn = fn
        self._rev += 1

    def _invoke(self, args):
        a = args[0].type()
        fn = self._dict.get(a, self._default_fn)
        return fn.invoke(args)

class DoublePolymorphicFn(BaseCode):
    """A function that is polymorphic on the first two arguments"""
    _type = object.Type(u"DoublePolymorphicFn")

    __immutable_fields__ = ["_rev?"]
    def __init__(self, name, protocol):
        BaseCode.__init__(self)
        self._name = name
        self._dict = {}
        self._rev = 0
        self._protocol = protocol
        protocol.add_method(self)

    def extend2(self, tp1, tp2, fn):
        d1 = self._dict.get(tp1, None)
        if d1 is None:
            d1 = {}
            self._dict[tp1] = d1
        d1[tp2] = fn
        self._rev += 1
        self._protocol.add_satisfies(tp1)


    @elidable
    def get_fn(self, tp1, tp2, _rev):
        d1 = self._dict.get(tp1, None)
        assert d1
        fn = d1.get(tp2, None)
        return promote(fn)

    def _invoke(self, args):
        assert len(args) >= 2
        a = args[0].type()
        b = args[1].type()
        fn = self.get_fn(a, b, self._rev)
        return fn.invoke(args)

def munge(s):
    return s.replace("-", "_")

import inspect
def defprotocol(ns, name, methods):
    """Define a protocol in the given namespace with the given name and methods, vars will
       be created in the namespace for the protocol and methods. This function will dump
       variables for the created protocols/methods in the globals() where this function is called."""
    ns = unicode(ns)
    name = unicode(name)
    methods = map(unicode, methods)
    gbls = inspect.currentframe().f_back.f_globals
    proto =  Protocol(name)
    intern_var(ns, name).set_root(proto)
    gbls[munge(name)] = proto
    for method in methods:
        poly = PolymorphicFn(method,  proto)
        intern_var(ns, method).set_root(poly)
        gbls[munge(method)] = poly


## PYTHON FLAGS
CO_VARARGS = 0x4
def wrap_fn(fn, tp=object.Object):
    """Converts a native Python function into a pixie function."""
    def as_native_fn(f):
        return type("W"+fn.__name__, (NativeFn,), {"inner_invoke": f})()

    def as_variadic_fn(f):
        return type("W"+fn.__name__[:len("__args")], (NativeFn,), {"inner_invoke": f})()

    code = fn.func_code
    if fn.__name__.endswith("__args"):
        return as_variadic_fn(lambda self, args: fn(args))

    if code.co_flags & CO_VARARGS:
        raise Exception("Variadic functions not supported by wrap")
    else:
        argc = code.co_argcount
        if argc == 0:
            return as_native_fn(lambda self, args: fn())
        if argc == 1:
            return as_native_fn(lambda self, args: fn(args[0]))
        if argc == 2:
            return as_native_fn(lambda self, args: fn(args[0], args[1]))
        if argc == 3:
            return as_native_fn(lambda self, args: fn(args[0], args[1]))


def extend(pfn, tp1, tp2=None):
    """Extends a protocol to the given Type (not python type), with the decorated function
       wraps the decorated function"""
    if isinstance(tp1, type):
        assert_tp = tp1
        tp1 = tp1._type
    else:
        assert_tp = object.Object

    def extend_inner(fn):
        if tp2 is None:
            pfn.extend(tp1, wrap_fn(fn, assert_tp))
        else:
            pfn.extend2(tp1, tp2, wrap_fn(fn, assert_tp))

        return pfn

    return extend_inner



def as_var(ns, name=None):
    """Locates a var with the given name (defaulting to the namespace pixie.stdlib), sets
       the root to the decorated function. If the function is not an instance of BaseCode it will
       be wrapped. """
    if name is None:
        name = ns
        ns = "pixie.stdlib"

    name = name if isinstance(name, unicode) else unicode(name)
    ns = ns if isinstance(ns, unicode) else unicode(ns)

    var = intern_var(ns, name)
    def with_fn(fn):
        if not isinstance(fn, object.Object):
            fn = wrap_fn(fn)
        var.set_root(fn)
        return fn
    return with_fn
