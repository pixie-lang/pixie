py_object = object
import pixie.vm2.object as object
from pixie.vm2.object import affirm, runtime_error
from pixie.vm2.primitives import nil, false
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.listsort import TimSort
from rpython.rlib.jit import elidable_promote, promote
from rpython.rlib.objectmodel import we_are_translated
import rpython.rlib.jit as jit
import pixie.vm2.rt as rt


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
             "LOOP_RECUR",
             "ARG",
             "PUSH_SELF",
             "POP_UP_N",
             "MAKE_MULTI_ARITY",
             "MAKE_VARIADIC",
             "YIELD",
             "PUSH_NS"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)


@jit.unroll_safe
def resize_list(lst, new_size):
    """'Resizes' a list, via reallocation and copy"""
    affirm(len(lst) < new_size, u"New list must be larger than old list")
    new_list = [None] * new_size
    i = r_uint(0)
    while i < len(lst):
        new_list[i] = lst[i]
        i += 1
    return new_list


@jit.unroll_safe
def list_copy(from_lst, from_loc, to_list, to_loc, count):
    from_loc = r_uint(from_loc)
    to_loc = r_uint(to_loc)
    count = r_uint(count)

    i = r_uint(0)
    while i < count:
        to_list[to_loc + i] = from_lst[from_loc + i]
        i += 1
    return to_list


@jit.unroll_safe
def slice_to_end(from_list, start_pos):
    start_pos = r_uint(start_pos)
    items_to_copy = len(from_list) - start_pos
    new_lst = [None] * items_to_copy
    list_copy(from_list, start_pos, new_lst, 0, items_to_copy)
    return new_lst


@jit.unroll_safe
def slice_from_start(from_list, count, extra=r_uint(0)):
    new_lst = [None] * (count + extra)
    list_copy(from_list, 0, new_lst, 0, count)
    return new_lst


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
    _immutable_fields_ = ["_meta", "_name"]
    def __init__(self):
        from pixie.vm2.string import String
        assert isinstance(self, BaseCode)
        self._name = u"unknown"
        self._is_macro = False
        self._meta = nil

    def meta(self):
        return self._meta

    def with_meta(self, meta):
        assert false, "not implemented"

    def name(self):
        return self._name

    def set_macro(self):
        self._is_macro = True

    def is_macro(self):
        assert isinstance(self, BaseCode)
        return self._is_macro

    def get_consts(self):
        raise NotImplementedError()

    def get_bytecode(self):
        raise NotImplementedError()

    @elidable_promote()
    def stack_size(self):
        return 0

    def invoke_with(self, args, this_fn):
        return self.invoke(args)

def join_last(words, sep):
    """
    Joins by commas and uses 'sep' on last word. 
    
    Eg. join_last(['dog', 'cat', 'rat'] , 'and') = 'dog, cat and rat'
    """ 
    if len(words) == 1:
        return words[0]
    else:
        if len(words) == 2:
            s = words[0] + u" " + sep + u" " + words[1]
        else:
            s = u", ".join(words[0:-1])
            s += u" " + sep + u" " + words[-1]
        return s

class MultiArityFn(BaseCode):
    _type = object.Type(u"pixie.stdlib.MultiArityFn")

    _immutable_fields_ = ["_arities[*]", "_required_arity", "_rest_fn", "_name"]

    def type(self):
        return MultiArityFn._type

    def __init__(self, name, arities, required_arity=0, rest_fn=None, meta=nil):
        BaseCode.__init__(self)
        self._name = name
        self._arities = arities
        self._required_arity = required_arity
        self._rest_fn = rest_fn
        self._meta = meta

    def with_meta(self, meta):
        return MultiArityFn(self._name, self._arities, self._required_arity, self._rest_fn, meta)

    @elidable_promote()
    def _get_fn(self, arity):
        f = self._arities.get(arity, None)
        if f is not None:
            return f
        if self._rest_fn is not None and arity >= self._required_arity:
            return self._rest_fn

        return None

    @jit.unroll_safe
    def get_fn(self, arity):
        fn = self._get_fn(arity)
        if fn:
            return fn

        acc = []
        sorted = TimSort(self.get_arities())
        sorted.sort()
        for x in sorted.list:
            acc.append(unicode(str(x)))

        if self._rest_fn:
            acc.append(unicode(str(self._rest_fn.required_arity())) + u"+")

        runtime_error(u"Wrong number of arguments " + unicode(str(arity)) + u" for function '" + unicode(self._name) + u"'. Expected " + join_last(acc, u"or"),
                      u"pixie.stdlib/InvalidArityException")




    def get_arities(self):
        return self._arities.keys()

    def invoke_k(self, args, stack):
        return self.invoke_k_with(args, stack, self)

    def invoke_k_with(self, args, stack, self_fn):
        return self.get_fn(len(args)).invoke_k_with(args, stack, self_fn)


class NativeFn(BaseCode):
    """Wrapper for a native function"""
    _type = object.Type(u"pixie.stdlib.NativeFn")

    def __init__(self, doc=None):
        BaseCode.__init__(self)

    def type(self):
        return NativeFn._type

    def invoke(self, args):
        return self.inner_invoke(args)

    def invoke_k(self, args, stack):
        return self.invoke(args), stack

    def inner_invoke(self, args):
        raise NotImplementedError()

    def invoke_with(self, args, this_fn):
        return self.invoke(args)


class Code(BaseCode):
    """Interpreted code block. Contains consts and """
    _type = object.Type(u"pixie.stdlib.Code")
    _immutable_fields_ = ["_arity", "_consts[*]", "_bytecode", "_stack_size", "_meta"]

    def type(self):
        return Code._type

    def __init__(self, name, arity, bytecode, consts, stack_size, debug_points, meta=nil):
        BaseCode.__init__(self)
        self._arity = arity
        self._bytecode = bytecode
        self._consts = consts
        self._name = name
        self._stack_size = stack_size
        self._debug_points = debug_points
        self._meta = meta

    def with_meta(self, meta):
        return Code(self._name, self._arity, self._bytecode, self._consts, self._stack_size, self._debug_points, meta=meta)

    def get_debug_points(self):
        return self._debug_points

    def invoke(self, args):
        if len(args) == self.get_arity():
            return self.invoke_with(args, self)
        else:
            runtime_error(u"Invalid number of arguments " + unicode(str(len(args))) 
                          + u" for function '" + unicode(str(self._name)) + u"'. Expected "
                          + unicode(str(self.get_arity())),
                          u":pixie.stdlib/InvalidArityException")

    def invoke_with(self, args, this_fn):
        return interpret(self, args, self_obj=this_fn)


    @elidable_promote()
    def get_arity(self):
        return self._arity
            
    @elidable_promote()
    def get_consts(self):
        return self._consts

    @elidable_promote()
    def get_bytecode(self):
        return self._bytecode

    @elidable_promote()
    def stack_size(self):
        return self._stack_size

    @elidable_promote()
    def get_base_code(self):
        return self


class VariadicCode(BaseCode):
    _immutable_fields_ = ["_required_arity", "_code", "_meta"]
    _type = object.Type(u"pixie.stdlib.VariadicCode")

    def type(self):
        return VariadicCode._type

    def __init__(self, code, required_arity, meta=nil):
        BaseCode.__init__(self)
        self._required_arity = r_uint(required_arity)
        self._code = code
        self._meta = meta

    def with_meta(self, meta):
        return VariadicCode(self._code, self._required_arity, meta)
    
    def name(self):
        return None
    
    def required_arity(self):
        return self._required_arity

    def invoke_k(self, args, stack):
        return self.invoke_k_with(args, stack, self)

    def invoke_k_with(self, args, stack, this_fn):
        from pixie.vm2.array import Array
        argc = len(args)
        if self._required_arity == 0:
            return self._code.invoke_k([Array(args)], stack)
        if argc == self._required_arity:
            new_args = resize_list(args, len(args) + 1)
            new_args[len(args)] = Array([])
            return self._code.invoke_k_with(new_args, stack, this_fn)
        elif argc > self._required_arity:
            start = slice_from_start(args, self._required_arity, 1)
            rest = slice_to_end(args, self._required_arity)
            start[self._required_arity] = Array(rest)
            return self._code.invoke_k_with(start, stack, this_fn)
        affirm(False, u"Got " + unicode(str(argc)) + u" arg(s) need at least " + unicode(str(self._required_arity)))
        return None, stack


class Closure(BaseCode):
    _type = object.Type(u"pixie.stdlib.Closure")
    _immutable_fields_ = ["_closed_overs[*]", "_code", "_meta"]
    
    def type(self):
        return Closure._type

    def __init__(self, code, closed_overs, meta=nil):
        BaseCode.__init__(self)
        affirm(isinstance(code, Code), u"Code argument to Closure must be an instance of Code")
        self._code = code
        self._closed_overs = closed_overs
        self._meta = meta

    def with_meta(self, meta):
        return Closure(self._code, self._closed_overs, meta)

    
    def name(self):
        return None

    def invoke(self, args):
        return self.invoke_with(args, self)

    def invoke_with(self, args, self_fn):
        return interpret(self, args, self_obj=self_fn)

    def get_closed_over(self, idx):
        return self._closed_overs[idx]

    def get_consts(self):
        return self._code.get_consts()

    def get_bytecode(self):
        return self._code.get_bytecode()

    def stack_size(self):
        return self._code.stack_size()

    def get_closed_overs(self):
        return self._closed_overs

    def get_base_code(self):
        return self._code.get_base_code()

    def get_debug_points(self):
        return self._code.get_debug_points()


class Undefined(object.Object):
    _type = object.Type(u"pixie.stdlib.Undefined")

    def type(self):
        return Undefined._type

undefined = Undefined()


class DynamicVars(py_object):
    def __init__(self):
        self._vars = [{}]

    def push_binding_frame(self):
        self._vars = rt.cons(rt.first(self._vars), self._vars)

    def pop_binding_frame(self):
        self._vars = rt.next(self._vars)

    def current_frame(self):
        return rt.first(self._vars)

    def get_current_frames(self):
        return self._vars

    def set_current_frames(self, vars):
        self._vars = vars

    def get_var_value(self, var, not_found):
        return rt._val_at(self.current_frame(), var, not_found)

    def set_var_value(self, var, val):
        cur_frame = self.current_frame()
        self.pop_binding_frame()
        self._vars = rt.cons(rt._assoc(cur_frame, var, val), self._vars)




class Var(BaseCode):
    _type = object.Type(u"pixie.stdlib.Var")
    _immutable_fields_ = ["_rev?"]

    def type(self):
        return Var._type

    def __init__(self, ns, name):
        BaseCode.__init__(self)
        self._ns = ns
        self._name = name
        self._rev = 0
        self._root = undefined
        self._dynamic = False

    def set_root(self, o):
        affirm(o is not None, u"Invalid var set")
        self._rev += 1
        self._root = o
        return self

    def set_value(self, val):
        affirm(self._dynamic, u"Can't set the value of a non-dynamic var")
        _dynamic_vars.set_var_value(self, val)
        return self

    def set_dynamic(self):
        self._dynamic = True
        self._rev += 1


    def get_dynamic_value(self):
        return _dynamic_vars.get_var_value(self, self._root)



    @elidable_promote()
    def _is_dynamic(self, rev):
        return self._dynamic

    def is_dynamic(self):
        return self._is_dynamic(self._rev)

    @elidable_promote()
    def get_root(self, rev):
        return self._root

    def deref(self):
        if self.is_dynamic():
            if we_are_translated():
                return self.get_dynamic_value()
            else:
                ## NOT RPYTHON
                if globals().has_key("_dynamic_vars"):
                    return self.get_dynamic_value()
                else:
                    return self.get_root(self._rev)
        else:
            val = self.get_root(self._rev)
            if val is undefined:
                pass
            affirm(val is not undefined, u"Var " + self._ns + u"/" + self._name + u" is undefined")
            return val

    def is_defined(self):
        return self._root is not undefined

    def invoke_with(self, args, this_fn):
        return self.invoke(args)

    def invoke_k(self, args, stack):
        return self.deref().invoke_k(args, stack)

class bindings(py_object):
    def __init__(self, *args):
        self._args = list(args)

    def __enter__(self):
        _dynamic_vars.push_binding_frame()
        for x in range(0, len(self._args), 2):
            self._args[x].set_value(self._args[x + 1])

    def __exit__(self, exc_type, exc_val, exc_tb):
        _dynamic_vars.pop_binding_frame()


class Refer(py_object):
    def __init__(self, ns, refer_syms={}, refer_all=False):
        self._namespace = ns
        self._refer_syms = refer_syms
        self._refer_all = refer_all
        self._excludes = {}

    def refer_all(self):
        self._refer_all = True

    def add_var_alias(self, old, new):
        assert isinstance(old, unicode)
        assert isinstance(new, unicode)

        self._refer_syms[new] = old

    def add_var_exclude(self, old):
        self._excludes[old] = old

    def find_var(self, name):
        if self._refer_all and name not in self._excludes:
            return self._namespace.resolve_in_ns(name, False)
        else:
            other = self._refer_syms.get(name, None)
            if other:
                return self._namespace.resolve_in_ns(other, False)
            return None


class Namespace(object.Object):
    _type = object.Type(u"pixie.stdlib.Namespace")

    def type(self):
        return Namespace._type

    def __init__(self, name):
        self._registry = {}
        self._name = name
        self._refers = {}
        self._var_cache = {}
        self._rev = 0

    def reset_cache(self):
        self._var_cache.clear()
        self._rev += 1

    def intern_or_make(self, name):
        assert name is not None
        self.reset_cache()
        affirm(isinstance(name, unicode), u"Var names must be unicode")
        v = self._registry.get(name, None)
        if v is None:
            v = Var(self._name, name)
            self._registry[name] = v
        return v

    def add_refer(self, ns, as_nm=None, refer_all=False):
        assert isinstance(ns, Namespace)
        self.reset_cache()

        if as_nm is not None:
            assert isinstance(as_nm, unicode)

        if as_nm is None:
            as_nm = ns._name

        self._refers[as_nm] = Refer(ns, refer_all=refer_all)

    def get_refer(self, nm):
        assert isinstance(nm, unicode)

        return self._refers.get(nm, None)

    def add_refer_symbol(self, sym, var):
        assert isinstance(self, Namespace)
        self.reset_cache()

        name = rt.name(sym)
        prev_binding = self._registry.get(name, None)
        if prev_binding is not None:
            print rt.name(rt.str(rt.wrap(u"Warning: "), sym, rt.wrap(u" already refers to "), prev_binding))

        self._registry[name] = var
        return var

    def include_stdlib(self):
        stdlib = ns_registry.find_or_make(u"pixie.stdlib")
        self.add_refer(stdlib, refer_all=True)
        self.reset_cache()


    def resolve(self, s, use_refers=True):
        import pixie.vm2.symbol as symbol
        affirm(isinstance(s, symbol.Symbol), u"Must resolve symbols")
        ns = s.get_ns()
        name = s.get_name()

        if ns is not None:
            refer = self._refers.get(ns, None)
            resolved_ns = None
            if refer is not None:
                resolved_ns = refer._namespace
            if resolved_ns is None:
                resolved_ns = ns_registry.get(ns, None)
            if resolved_ns is None:
                affirm(False, u"Unable to resolve namespace: " + ns + u" inside namespace " + self._name)
        else:
            resolved_ns = self

        assert isinstance(resolved_ns, Namespace)

        return resolved_ns.resolve_in_ns(name, use_refers=use_refers)

    def resolve_in_ns_ex(self, ns, name, use_refers=True):
        return self._resolve_in_ns_ex(ns, name, self._rev, use_refers)

    @jit.elidable_promote()
    def _resolve_in_ns_ex(self, ns, name, rev, use_refers):
        if ns is None:
            return self._resolve_in_ns(name, use_refers, rev)
        else:
            refer = self._refers.get(ns, None)
            if refer is not None:
                return refer._namespace._resolve_in_ns(name, use_refers, rev)
            else:
                resolved_ns = ns_registry.get(ns, None)
                if resolved_ns is None:
                    return None
                return resolved_ns.resolve_in_ns(name, False)

    def resolve_in_ns(self, name, use_refers=True):
        return self._resolve_in_ns(name, use_refers, self._rev)


    @jit.elidable_promote()
    def _resolve_in_ns(self, name, use_refers, rev):
        var = self._var_cache.get(name, None)
        if var is None:
            var = self._registry.get(name, None)
            if var is None and use_refers:
                for refer_nm in self._refers:
                    refer = self._refers[refer_nm]
                    var = refer.find_var(name)
                    if var is not None:
                        break

            if var is not None:
                self._var_cache[name] = var

        return var

    def get(self, name, default):
        return self._registry.get(name, default)


class NamespaceRegistry(py_object):
    def __init__(self):
        self._registry = {}

    def find_or_make(self, name):
        #affirm(isinstance(name, unicode), u"Namespace names must be unicode")
        v = self._registry.get(name, None)
        if v is None:
            v = Namespace(name)
            self._registry[name] = v
            v.include_stdlib()
        return v

    def get(self, name, default):
        return self._registry.get(name, default)

ns_registry = NamespaceRegistry()


def intern_var(ns, name=None):
    if name is None:
        name = ns
        ns = u""

    return ns_registry.find_or_make(ns).intern_or_make(name)


def get_var_if_defined(ns, name, els=None):
    w_ns = ns_registry.get(ns, None)
    if w_ns is None:
        return els
    return w_ns.get(name, els)


class DefaultProtocolFn(NativeFn):
    def __init__(self, pfn):
        BaseCode.__init__(self)
        self._pfn = pfn

    def invoke(self, args):
        tp = args[0].type()
        assert isinstance(tp, object.Type)
        pfn = self._pfn
        if isinstance(pfn, PolymorphicFn):
            protocol = pfn._protocol
        elif isinstance(pfn, DoublePolymorphicFn):
            protocol = pfn._protocol
        else:
            assert False
        assert isinstance(protocol, Protocol)
        affirm(False, u"No override for " + tp._name + u" on " + self._pfn._name + u" in protocol " + protocol._name)


class Protocol(object.Object):
    _type = object.Type(u"pixie.stdlib.Protocol")

    _immutable_fields_ = ["_rev?"]

    def type(self):
        return Protocol._type

    def __init__(self, name):
        self._name = name
        self._polyfns = {}
        self._satisfies = {}
        self._rev = 0

    def add_method(self, pfn):
        self._polyfns[pfn] = pfn

    def add_satisfies(self, tp):
        self._satisfies[tp] = tp
        self._rev += 1

    @elidable_promote()
    def _get_satisfies(self, tp, rev):
        return tp in self._satisfies

    def satisfies(self, tp):
        return self._get_satisfies(tp, self._rev)


class PolymorphicFn(BaseCode):
    _type = object.Type(u"pixie.stdlib.PolymorphicFn")

    def type(self):
        return PolymorphicFn._type

    _immutable_fields_ = ["_rev?"]

    def __init__(self, name, protocol):
        BaseCode.__init__(self)
        self._name = name
        self._dict = {}
        # stored separately to allow ordered extending (e.g. more general protocols later)
        self._protos = []
        self._rev = 0
        self._protocol = protocol
        self._default_fn = DefaultProtocolFn(self)
        self._fn_cache = {}
        protocol.add_method(self)

    def extend(self, tp, fn):
        self._dict[tp] = fn
        if isinstance(tp, Protocol):
            self._protos.append(tp)
        self._rev += 1
        self._fn_cache = {}
        self._protocol.add_satisfies(tp)

    def _find_parent_fn(self, tp):
        ## Search the entire object tree to find the function to execute
        assert isinstance(tp, object.Type)

        find_tp = tp
        while True:
            result = self._dict.get(find_tp, None)
            if result is not None:
                return result

            for proto in self._protos:
                if proto.satisfies(find_tp):
                    return self._dict[proto]

            find_tp = find_tp._parent
            if find_tp is None:
                break

        return self._default_fn

    def set_default_fn(self, fn):
        self._default_fn = fn
        self._rev += 1
        self._fn_cache = {}

    @elidable_promote()
    def get_protocol_fn(self, tp, rev):
        fn = self._fn_cache.get(tp, None)
        if fn is None:
            fn = self._find_parent_fn(tp)
            self._fn_cache[tp] = fn

        return promote(fn)

    def invoke_k(self, args, stack):
        affirm(len(args) >= 1, u"Wrong number of args")
        a = args[0].type()
        fn = self.get_protocol_fn(a, self._rev)
        return fn.invoke_k(args, stack)


class DoublePolymorphicFn(BaseCode):
    """A function that is polymorphic on the first two arguments"""
    _type = object.Type(u"pixie.stdlib.DoublePolymorphicFn")

    def type(self):
        return DefaultProtocolFn._type

    _immutable_fields_ = ["_rev?"]

    def __init__(self, name, protocol):
        BaseCode.__init__(self)
        self._name = name
        self._dict = {}
        self._rev = 0
        self._protocol = protocol
        self._default_fn = DefaultProtocolFn(self)
        protocol.add_method(self)

    def extend2(self, tp1, tp2, fn):
        d1 = self._dict.get(tp1, None)
        if d1 is None:
            d1 = {}
            self._dict[tp1] = d1
        d1[tp2] = fn
        self._rev += 1
        self._protocol.add_satisfies(tp1)

    def set_default_fn(self, fn):
        self._default_fn = fn
        self._rev += 1

    @elidable_promote()
    def get_fn(self, tp1, tp2, _rev):
        d1 = self._dict.get(tp1, None)
        if d1 is None:
            return self._default_fn
        fn = d1.get(tp2, self._default_fn)
        return promote(fn)

    def invoke_k(self, args, stack):
        affirm(len(args) >= 2, u"DoublePolymorphicFunctions take at least two args")
        a = args[0].type()
        b = args[1].type()
        fn = self.get_fn(a, b, self._rev)
        return fn.invoke_k(args, stack)

def munge(s):
    return s.replace("-", "_").replace("?", "_QMARK_").replace("!", "_BANG_")


import inspect


def defprotocol(ns, name, methods):
    """Define a protocol in the given namespace with the given name and methods, vars will
       be created in the namespace for the protocol and methods. This function will dump
       variables for the created protocols/methods in the globals() where this function is called."""
    ns = unicode(ns)
    name = unicode(name)
    methods = map(unicode, methods)
    gbls = inspect.currentframe().f_back.f_globals
    proto = Protocol(name)
    intern_var(ns, name).set_root(proto)
    gbls[munge(name)] = proto
    for method in methods:
        poly = PolymorphicFn(method, proto)
        intern_var(ns, method).set_root(poly)
        gbls[munge(method)] = poly


def assert_type(x, tp):
    affirm(isinstance(x, tp), u"Fatal Error, this should never happen")
    return x


## PYTHON FLAGS
CO_VARARGS = 0x4


def wrap_fn(fn, tp=object.Object):
    """Converts a native Python function into a pixie function."""
    import pixie.vm2.rt as rt

    docstring = unicode(fn.__doc__) if fn.__doc__ else u""
    def as_native_fn(f):
        return type("W" + fn.__name__, (NativeFn,), {"inner_invoke": f, "_doc": docstring})()

    def as_variadic_fn(f):
        return type("W" + fn.__name__[:len("__args")], (NativeFn,), {"inner_invoke": f, "_doc": docstring})()

    code = fn.func_code
    if fn.__name__.endswith("__args"):
        return as_variadic_fn(lambda self, args: rt.wrap(fn(args)))

    fn_name = unicode(getattr(fn, "__real_name__", fn.__name__))

    if code.co_flags & CO_VARARGS:
        raise Exception("Variadic functions not supported by wrap")
    else:
        argc = code.co_argcount
        if argc == 0:
            def wrapped_fn(self, args):
                affirm(len(args) == 0, u"Expected 0 arguments to " + fn_name)
                try:
                    return rt.wrap(fn())
                except object.WrappedException as ex:
                    #ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                    raise
            return as_native_fn(wrapped_fn)

        if argc == 1:
            def wrapped_fn(self, args):
                affirm(len(args) == 1, u"Expected 1 arguments to " + fn_name)
                try:
                    return rt.wrap(fn(args[0]))
                except object.WrappedException as ex:
                    #ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                    raise
            return as_native_fn(wrapped_fn)

        if argc == 2:
            def wrapped_fn(self, args):
                affirm(len(args) == 2, u"Expected 2 arguments to " + fn_name)
                try:
                    return rt.wrap(fn(args[0], args[1]))
                except object.WrappedException as ex:
                    #ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                    raise
            return as_native_fn(wrapped_fn)
        if argc == 3:
            def wrapped_fn(self, args):
                affirm(len(args) == 3, u"Expected 3 arguments to " + fn_name)

                try:
                    return rt.wrap(fn(args[0], args[1], args[2]))
                except object.WrappedException as ex:
                    #ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                    raise
            return as_native_fn(wrapped_fn)

        if argc == 4:
            def wrapped_fn(self, args):
                affirm(len(args) == 4, u"Expected 4 arguments to " + fn_name)

                try:
                    return rt.wrap(fn(args[0], args[1], args[2], args[3]))
                except object.WrappedException as ex:
                    #ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                    raise
            return as_native_fn(wrapped_fn)

        assert False, "implement more"


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

init_ctx = []

def extend_var(ns_name, var_name, tp1):
    if isinstance(tp1, type):
        assert_tp = tp1
        tp1 = tp1._type
    else:
        assert_tp = object.Object

    var = intern_var(unicode(ns_name), unicode(var_name))

    def extend_inner(fn):
        init_ctx.append((var, tp1, wrap_fn(fn, assert_tp)))

        return var

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
        fn.__real_name__ = name
        if not isinstance(fn, object.Object):
            fn = wrap_fn(fn)
        var.set_root(fn)
        return fn
    return with_fn


def returns(type):
    """Tags a var as for unwrapping in rt. When rt imports this var it will be automatically converted to this type"""
    def with_fn(fn):
        fn._returns = type
        return fn
    return with_fn



class bindings(py_object):
    def __init__(self, *args):
        self._args = list(args)

    def __enter__(self):
        _dynamic_vars.push_binding_frame()
        for x in range(0, len(self._args), 2):
            self._args[x].set_value(self._args[x + 1])

    def __exit__(self, exc_type, exc_val, exc_tb):
        _dynamic_vars.pop_binding_frame()


def init():
    pass
    #globals()["_dynamic_vars"] = DynamicVars()
