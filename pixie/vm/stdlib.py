# -*- coding: utf-8 -*-
from pixie.vm.object import Object, Type, _type_registry, WrappedException, RuntimeException, affirm, InterpreterCodeInfo, istypeinstance
from pixie.vm.code import BaseCode, PolymorphicFn, wrap_fn, as_var, defprotocol, extend, Protocol, Var, \
                          resize_list, list_copy, returns, get_var_if_defined, intern_var
import pixie.vm.code as code
from types import MethodType
from pixie.vm.primitives import true, false, nil
import pixie.vm.numbers as numbers
import rpython.rlib.jit as jit
from rpython.rlib.rarithmetic import r_uint
from pixie.vm.interpreter import ShallowContinuation
from rpython.rlib.objectmodel import we_are_translated

defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

defprotocol("pixie.stdlib", "ICounted", ["-count"])

defprotocol("pixie.stdlib", "IIndexed", ["-nth"])

defprotocol("pixie.stdlib", "IPersistentCollection", ["-conj", "-disj"])

defprotocol("pixie.stdlib", "IEmpty", ["-empty"])

defprotocol("pixie.stdlib", "IObject", ["-hash", "-eq", "-str", "-repr"])
_eq.set_default_fn(wrap_fn(lambda a, b: false))

defprotocol("pixie.stdlib", "IReduce", ["-reduce"])

defprotocol("pixie.stdlib", "IDeref", ["-deref"])

defprotocol("pixie.stdlib", "IReset", ["-reset!"])

defprotocol("pixie.stdlib", "INamed", ["-namespace", "-name"])

defprotocol("pixie.stdlib", "IAssociative", ["-assoc", "-contains-key", "-dissoc"])

defprotocol("pixie.stdlib", "ILookup", ["-val-at"])

defprotocol("pixie.stdlib", "IMapEntry", ["-key", "-val"])

defprotocol("pixie.stdlib", "IStack", ["-push", "-pop"])

defprotocol("pixie.stdlib", "IFn", ["-invoke"])

IVector = as_var("pixie.stdlib", "IVector")(Protocol(u"IVector"))

IMap = as_var("pixie.stdlib", "IMap")(Protocol(u"IMap"))

defprotocol("pixie.stdlib", "IMeta", ["-with-meta", "-meta"])

defprotocol("pixie.stdlib", "ITransient", ["-persistent!"])
defprotocol("pixie.stdlib", "IToTransient", ["-transient"])

defprotocol("pixie.stdlib", "ITransientCollection", ["-conj!"])

defprotocol("pixie.stdlib", "IIterable", ["-iterator"])
defprotocol("pixie.stdlib", "IIterator", ["-current", "-at-end?", "-move-next!"])

@as_var("pixie.stdlib.internal", "-defprotocol")
def _defprotocol(name, methods):
    from pixie.vm.compiler import NS_VAR
    from pixie.vm.persistent_vector import PersistentVector
    from pixie.vm.symbol import Symbol
    affirm(isinstance(name, Symbol), u"protocol name must be a symbol")
    affirm(isinstance(methods, PersistentVector), u"protocol methods must be a vector of symbols")
    method_list = []
    for i in range(0, rt.count(methods)):
        method_sym = rt.nth(methods, rt.wrap(i))
        affirm(isinstance(method_sym, Symbol), u"protocol methods must be a vector of symbols")
        method_list.append(rt.name(method_sym))

    proto =  Protocol(rt.name(name))
    ns = rt.name(NS_VAR.deref())
    intern_var(ns, rt.name(name)).set_root(proto)
    for method in method_list:
        method = unicode(method)
        poly = PolymorphicFn(method,  proto)
        intern_var(ns, method).set_root(poly)

    return name

def __make_code_overrides(x):
    @extend(_meta, x._type)
    def __meta(self):
        assert isinstance(self, x)
        return self.meta()

    @extend(_with_meta, x._type)
    def __meta(self, meta):
        assert isinstance(self, x)
        return self.with_meta(meta)

for x in (code.Code, code.Closure, code.VariadicCode, code.MultiArityFn):
    __make_code_overrides(x)



def default_str(x):
    from pixie.vm.string import String

    return rt.wrap(u"<inst " + x.type()._name + u">")

_str.set_default_fn(wrap_fn(default_str))
_repr.set_default_fn(wrap_fn(default_str))

_meta.set_default_fn(wrap_fn(lambda x: nil))

#_first = PolymorphicFn("-first")
#_next = PolymorphicFn("-next")

@as_var("first")
def first(x):
    if rt.satisfies_QMARK_(ISeq, x):
        return rt._first(x)

    seq = rt.seq(x)
    if seq is nil:
        return nil
    return rt._first(seq)

@as_var("next")
def next(x):
    if rt.satisfies_QMARK_(ISeq, x):
        return rt.seq(rt._next(x))
    seq = rt.seq(x)
    if seq is nil:
        return nil
    else:
        return rt.seq(rt._next(seq))

@as_var("seq")
def seq(x):
    return rt._seq(x)

@as_var("seq?")
def seq_QMARK_(x):
    return true if rt.satisfies_QMARK_(rt.ISeq.deref(), x) else false

@as_var("-seq-eq")
def _seq_eq(a, b):
    if a is b:
        return true
    if not (rt.satisfies_QMARK_(rt.ISeqable.deref(), b) or rt.satisfies_QMARK_(rt.ISeq.deref(), b)):
        return false

    a = rt.seq(a)
    b = rt.seq(b)
    while a is not nil:
        if b is nil or not rt.eq(rt.first(a), rt.first(b)):
            return false
        a = rt.next(a)
        b = rt.next(b)
    return true if b is nil else false

@as_var("type")
def type(x):
    return x.type()

@extend(_str, Type)
def _str(tp):
    import pixie.vm.string as string
    return string.rt.wrap(u"<type " + tp._name + u">")

@extend(_repr, Type)
def _repr(tp):
    import pixie.vm.string as string
    return string.rt.wrap(tp._name)

@extend(_first, nil._type)
def _first(_):
    return nil

@extend(_next, nil._type)
def _next(_):
    return nil

@extend(_seq, nil._type)
def _seq(_):
    return nil

@extend(_count, nil._type)
def _count(_):
    return numbers.zero_int

@extend(_assoc, nil._type)
def __assoc(_, k, v):
    return rt.hashmap(k, v)

@extend(_reduce, nil._type)
def __reduce(self, f, init):
    return init

@extend(_val_at, nil._type)
def __val_at(x, k, not_found):
    return not_found

@extend(_name, Var)
def __name(self):
    assert isinstance(self, Var)
    return rt.wrap(self._name)

@extend(_namespace, Var)
def __name(self):
    assert isinstance(self, Var)
    return rt.wrap(self._ns)

@extend(_deref, Var)
def __deref(self):
    assert isinstance(self, Var)
    return self.deref()

@extend(_name, code.Namespace)
def __name(self):
    assert isinstance(self, code.Namespace)
    return rt.wrap(self._name)

@extend(_namespace, code.Namespace)
def __name(_):
    return nil

@extend(_current, ShallowContinuation)
def _current(self):
    assert isinstance(self, ShallowContinuation)
    return self._val

@extend(_at_end_QMARK_, ShallowContinuation)
def _(self):
    assert isinstance(self, ShallowContinuation)
    return true if self.is_finished() else false

@extend(_move_next_BANG_, ShallowContinuation)
def _(self):
    assert isinstance(self, ShallowContinuation)
    self.invoke([nil])
    return self

@returns(r_uint)
@as_var("hash")
def __hash(x):
    return rt._hash(x)



_count_driver = jit.JitDriver(name="pixie.stdlib.count",
                              greens=["tp"],
                              reds="auto")
@returns(r_uint)
@as_var("count")
def count(x):
    acc = 0
    if ICounted.satisfies(rt.type(x)):
        return rt._count(x)
    while True:
        _count_driver.jit_merge_point(tp=rt.type(x))
        if ICounted.satisfies(rt.type(x)):
           return rt._add(rt.wrap(acc), rt._count(x))
        acc += 1
        x = rt.next(rt.seq(x))


@as_var("+")
def add(a, b):
    return rt._add(a, b)

@as_var("meta")
def __meta(a):
    return rt._meta(a)

@as_var("with-meta")
def __with_meta(a, b):
    return rt._with_meta(a, b)

@returns(bool)
@as_var("has-meta?")
def __has_meta(a):
    return true if rt.satisfies_QMARK_(rt.IMeta.deref(), a) else false

@as_var("conj")
def conj(a, b):
    return rt._conj(a, b)

@as_var("nth")
def nth(a, b):
    return rt._nth(a, b)


@as_var("str")
def str__args(args):
    from pixie.vm.string import String
    acc = []
    for x in args:
        acc.append(rt._str(x)._str)
    return rt.wrap(u"".join(acc))

@as_var("apply")
@jit.unroll_safe
def apply__args(args):
    last_itm = args[len(args) - 1]
    if not (rt.satisfies_QMARK_(rt.IIndexed.deref(), last_itm) and
            rt.satisfies_QMARK_(rt.ICounted.deref(), last_itm)):
        last_itm = rt.vec(last_itm)

    fn = args[0]
    argc = r_uint(len(args) - 2)
    out_args = [None] * (argc + r_uint(rt.count(last_itm)))

    list_copy(args, 1, out_args, 0, argc)

    for x in range(rt.count(last_itm)):
        out_args[argc + x] = rt.nth(last_itm, rt.wrap(x))

    return fn.invoke(out_args)


#@as_var("print")
#def _print(a):
#    print rt._str(a)._str
#    return nil

@returns(bool)
@as_var("instance?")
def _instance(c, o):
    affirm(isinstance(c, Type), u"c must be a type")

    return true if istypeinstance(o, c) else false

@returns(bool)
@as_var("satisfies?")
def _satisfies(proto, o):
    affirm(isinstance(proto, Protocol), u"proto must be a Protocol")

    return true if proto.satisfies(o.type()) else false


import pixie.vm.rt as rt


@as_var("read-string")
def _read_string(s):
    import pixie.vm.reader as reader
    return reader.read(reader.StringReader(unicode(rt.name(s))), True)

# XXX seems broken under jit.
@as_var("eval")
def eval(form):
    from pixie.vm.compiler import compile
    from pixie.vm.interpreter import interpret
    val = interpret(compile(form))
    return val

@as_var("load-ns")
def load_ns(filename):
    import pixie.vm.string as string
    import pixie.vm.symbol as symbol
    import os.path as path

    if isinstance(filename, symbol.Symbol):
        affirm(rt.namespace(filename) is None, u"load-file takes a un-namespaced symbol")
        filename_str = rt.name(filename).replace(u".", u"/") + u".pxi"

        loaded_ns = code._ns_registry.get(rt.name(filename), None)
        if loaded_ns is not None:
            return loaded_ns
    else:
        affirm(isinstance(filename, string.String), u"Filename must be string")
        filename_str = rt.name(filename)

    paths = rt.deref(rt.deref(rt.load_paths))
    f = None
    for x in range(rt.count(paths)):
        path_x = rt.nth(paths, rt.wrap(x))
        affirm(isinstance(path_x, string.String), u"Contents of load-paths must be strings")
        full_path = path.join(str(rt.name(path_x)), str(filename_str))
        if path.isfile(full_path):
            f = full_path
            break

    if f is None:
        affirm(False, u"File '" + rt.name(filename) + u"' does not exist in any directory found in load-paths")
    else:
        rt.load_file(rt.wrap(f))
    return nil

@as_var("load-file")
def load_file(filename):
    from pixie.vm.string import String
    import pixie.vm.reader as reader
    import os.path as path

    affirm(isinstance(filename, String), u"filename must be a string")
    filename = str(rt.name(filename))
    affirm(path.isfile(filename), unicode(filename) + u" does not exist")

    f = open(filename)
    data = f.read()
    f.close()

    if data.startswith("#!"):
        newline_pos = data.find("\n")
        if newline_pos > 0:
            data = data[newline_pos:]

    rt.load_reader(reader.MetaDataReader(reader.StringReader(unicode(data)), unicode(filename)))
    return nil

@as_var("load-reader")
def load_reader(rdr):
    import pixie.vm.reader as reader
    import pixie.vm.compiler as compiler

    with compiler.with_ns(u"user"):
        while True:
            form = reader.read(rdr, False)
            if form is reader.eof:
                return nil
            compiler.compile(form).invoke([])
    return nil

@as_var("the-ns")
def the_ns(ns_name):
    affirm(rt.namespace(ns_name) is None, u"the-ns takes a un-namespaced symbol")

    return code._ns_registry.get(rt.name(ns_name), nil)

@as_var("ns-map")
def ns_map(ns):
    from pixie.vm.symbol import Symbol

    affirm(isinstance(ns, code.Namespace) or isinstance(ns, Symbol), u"ns must be a symbol or a namespace")

    if isinstance(ns, Symbol):
        ns = rt.the_ns(ns)
        if ns is nil:
            return nil

    m = rt.hashmap()
    for name in ns._registry:
        var = ns._registry.get(name, nil)
        m = rt.assoc(m, rt.symbol(rt.wrap(name)), var)

    return m

@as_var("refer-ns")
def refer(ns, refer, alias):
    from pixie.vm.symbol import Symbol

    affirm(isinstance(ns, code.Namespace), u"First argument must be a namespace")
    affirm(isinstance(refer, code.Namespace), u"Second argument must be a namespace")
    affirm(isinstance(alias, Symbol), u"Third argument must be a symbol")

    ns.add_refer(refer, rt.name(alias))
    return nil

@as_var("refer-symbol")
def refer_symbol(ns, sym, var):
    from pixie.vm.symbol import Symbol

    affirm(isinstance(ns, code.Namespace), u"First argument must be a namespace")
    affirm(isinstance(sym, Symbol) and rt.namespace(sym) is None, u"Second argument must be a non-namespaced symbol")
    affirm(isinstance(var, code.Var), u"Third argument must be a var")

    ns.add_refer_symbol(sym, var)
    return nil

@as_var("extend")
def _extend(proto_fn, tp, fn):
    affirm(isinstance(proto_fn, PolymorphicFn), u"First argument to extend should be a PolymorphicFn")
    affirm(isinstance(tp, Type) or isinstance(tp, Protocol), u"Second argument to extend must be a Type or Protocol")
    affirm(isinstance(fn, BaseCode), u"Last argument to extend must be a function")
    proto_fn.extend(tp, fn)
    return nil

@as_var("satisfy")
def satisfy(protocol, tp):
    affirm(isinstance(protocol, code.Protocol), u"First argument must be a protocol")
    affirm(isinstance(tp, Type), u"Second argument must be a type")
    protocol.add_satisfies(tp)
    return protocol

@as_var("type-by-name")
def type_by_name(nm):
    import pixie.vm.string as string
    affirm(isinstance(nm, string.String), u"type name must be string")
    return _type_registry.get_by_name(nm._str, nil)



@as_var("deref")
def deref(x):
    return rt._deref(x)

@as_var("identical?")
def identical(a, b):
    return true if a is b else false

@as_var("vector?")
def vector_QMARK_(a):
    return true if rt.satisfies_QMARK_(rt.IVector.deref(), a) else false

@returns(bool)
@as_var("eq")
def eq(a, b):
    if a is b:
        return true
    else:
        return rt._eq(a, b)

@as_var("set-macro!")
def set_macro(f):
    affirm(isinstance(f, BaseCode), u"Only code objects can be macros")
    f.set_macro()
    return f

@returns(bool)
@as_var("macro?")
def macro_QMARK_(f):
    return true if isinstance(f, BaseCode) and f.is_macro() else false

@returns(unicode)
@as_var("name")
def name(s):
    return rt._name(s)

@returns(unicode)
@as_var("namespace")
def namespace(s):
    return rt._namespace(s)

@as_var("-try-catch")
def _try_catch(main_fn, catch_fn, final):
    try:
        return main_fn.invoke([])
    except Exception as ex:
        if not isinstance(ex, WrappedException):
            from pixie.vm.string import String
            if isinstance(ex, Exception):
                ex = RuntimeException(rt.wrap(u"Some error"))
                if not we_are_translated():
                    print "Error", ex
            else:
                ex = RuntimeException(nil)
            return catch_fn.invoke([ex])
        else:
            return catch_fn.invoke([ex._ex])
    finally:
        if final is not nil:
            final.invoke([])

@as_var("throw")
def _throw(ex):
    if isinstance(ex, RuntimeException):
        raise WrappedException(ex)
    raise WrappedException(RuntimeException(ex))

@as_var("resolve-in")
def _var(ns, nm):
    affirm(isinstance(ns, code.Namespace), u"First argument to resolve-in must be a namespace")
    var = ns.resolve(nm)
    return var if var is not None else nil

@as_var("set-dynamic!")
def set_dynamic(var):
    affirm(isinstance(var, Var), u"set-dynamic! expects a var as an argument")
    var.set_dynamic()
    return var

@as_var("set!")
def set(var, val):
    affirm(isinstance(var, Var), u"Can only set the dynamic value of a var")
    var.set_value(val)
    return var

@as_var("push-binding-frame!")
def push_binding_frame():
    code._dynamic_vars.push_binding_frame()
    return nil

@as_var("pop-binding-frame!")
def pop_binding_frame():
    code._dynamic_vars.pop_binding_frame()
    return nil

# @as_var("elidable-fn")
# def elidable_fn(fn):
#     return code.ElidableFn(fn)

@as_var("promote")
def promote(i):
    return i.promote()

def invoke_other(obj, args):
    from pixie.vm.array import array
    return rt.apply(_invoke, obj, array(args))

@as_var("interpreter_code_info")
def _ici(meta):
    import pixie.vm.reader as reader
    line = rt._val_at(meta, reader.LINE_KW, nil)
    line_number = rt._val_at(meta, reader.LINE_NUMBER_KW, nil)
    col_number = rt._val_at(meta, reader.COLUMN_NUMBER_KW, nil)
    file = rt._val_at(meta, reader.FILE_KW, nil)

    return InterpreterCodeInfo(line,
                               line_number.int_val() if line_number is not nil else 0,
                               col_number.int_val() if col_number is not nil else 0,
                               rt.name(file) if file is not nil else u"<unknown")

@wrap_fn
def merge_fn(acc, x):
    return rt._assoc(acc, rt._key(x), rt._val(x))


@as_var("merge")
@jit.unroll_safe
def _merge__args(args):
    affirm(len(args) > 0, u"Merge takes at least one arg")
    acc = args[0]
    for x in range(1, len(args)):
        acc = rt._reduce(args[x], merge_fn, acc)
    return acc



@extend(_str, RuntimeException)
def _str(self):
    assert isinstance(self, RuntimeException)
    return rt.wrap(self.__repr__())
