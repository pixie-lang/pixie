# -*- coding: utf-8 -*-
from pixie.vm.object import Object, Type, _type_registry, WrappedException, RuntimeException
from pixie.vm.code import BaseCode, PolymorphicFn, wrap_fn, as_var, defprotocol, extend, Protocol, Var, \
                          resize_list, list_copy
from types import MethodType
from pixie.vm.primitives import true, false, nil
import pixie.vm.numbers as numbers
import rpython.rlib.jit as jit
import rpython.rlib.rstacklet as rstacklet
from rpython.rlib.rarithmetic import r_uint


defprotocol("pixie.stdlib", "ISeq", ["-first", "-next"])
defprotocol("pixie.stdlib", "ISeqable", ["-seq"])

defprotocol("pixie.stdlib", "ICounted", ["-count"])

defprotocol("pixie.stdlib", "IIndexed", ["-nth"])

defprotocol("pixie.stdlib", "IPersistentCollection", ["-conj"])

defprotocol("pixie.stdlib", "IObject", ["-hash", "-eq", "-str", "-repr"])
_eq.set_default_fn(wrap_fn(lambda a, b: false))

defprotocol("pixie.stdlib", "IReduce", ["-reduce"])

defprotocol("pixie.stdlib", "IDeref", ["-deref"])

defprotocol("pixie.stdlib", "IReset", ["-reset!"])

defprotocol("pixie.stdlib", "INamed", ["-namespace", "-name"])

IVector = as_var("pixie.stdlib", "IVector")(Protocol(u"IVector"))

def default_str(x):
    from pixie.vm.string import String

    return String(u"<inst " + x.type()._name + u">")

_str.set_default_fn(wrap_fn(default_str))
_repr.set_default_fn(wrap_fn(default_str))

#_first = PolymorphicFn("-first")
#_next = PolymorphicFn("-next")

@as_var("first")
def first(x):
    return rt._first(x)

@as_var("next")
def next(x):
    return rt.seq(rt._next(x))

@as_var("seq")
def seq(x):
    return rt._seq(x)

@as_var("seq?")
def seq_QMARK_(x):
    return rt.instance_QMARK_(x, rt.ISeq.deref())


@as_var("type")
def type(x):
    return x.type()

@extend(_str, Type)
def _str(tp):
    import pixie.vm.string as string
    return string.String(u"<type " + tp._name + u">")


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

@as_var("hash")
def _hash(x):
    return rt._hash(x)


_count_driver = jit.JitDriver(name="pixie.stdlib.count",
                              greens=["tp"],
                              reds="auto")
@as_var("count")
def count(x):
    acc = 0
    while True:
        _count_driver.jit_merge_point(tp=rt.type(x))
        if ICounted.satisfies(rt.type(x)):
           return rt._add(numbers.Integer(acc), rt._count(x))
        acc += 1
        x = rt.next(rt.seq(x))


@as_var("+")
def add(a, b):
    return rt._add(a, b)

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
    return String(u"".join(acc))

@as_var("apply")
@jit.unroll_safe
def apply__args(args):
    last_itm = args[len(args) - 1]
    if rt.instance_QMARK_(last_itm, rt.IIndexed.deref()) is false or \
        rt.instance_QMARK_(last_itm, rt.ICounted.deref()) is false:
        raise ValueError("Last item to apply must be bost IIndexed and ICounted")

    fn = args[0]
    argc = r_uint(len(args) - 2)
    out_args = [None] * (argc + r_uint(rt.count(last_itm).int_val()))

    list_copy(args, 1, out_args, 0, argc)

    for x in range(rt.count(last_itm).int_val()):
        out_args[argc + x] = rt.nth(last_itm, numbers.Integer(x))

    return fn.invoke(out_args)


@as_var("print")
def _print(a):
    print rt._str(a)._str
    return nil

@as_var("instance?")
def _instance(o, proto):
    assert isinstance(proto, Protocol), "proto must be a Protocol"

    return true if proto.satisfies(o.type()) else false


import pixie.vm.rt as rt


@as_var("load_file")
def load_file(filename):
    import pixie.vm.reader as reader
    import pixie.vm.compiler as compiler
    f = open(str(filename._str))
    data = f.read()
    f.close()
    rdr = reader.StringReader(unicode(data))
    result = nil
    while True:
        form = reader.read(rdr, False)
        if form is reader.eof:
            return result

        result = compiler.compile(form).invoke([])

@as_var("extend")
def extend(proto_fn, tp, fn):
    assert isinstance(proto_fn, PolymorphicFn), "First argument to extend should be a PolymorphicFn"
    assert isinstance(tp, Type), "Second argument to extend must be a Type"
    assert isinstance(fn, BaseCode), "Last argument to extend must be a function"
    proto_fn.extend(tp, fn)
    return nil

@as_var("type-by-name")
def type_by_name(nm):
    import pixie.vm.string as string
    assert isinstance(nm, string.String)
    return _type_registry.get_by_name(nm._str, nil)

@as_var("deref")
def deref(x):
    return rt._deref(x)

@as_var("identical?")
def identical(a, b):
    return true if a is b else false

@as_var("vector?")
def vector_QMARK_(a):
    return rt.instance_QMARK_(a, rt.IVector.deref())


@as_var("eq")
def eq(a, b):
    if a is b:
        return true
    else:
        return rt._eq(a, b)

@as_var("set-macro!")
def set_macro(f):
    assert isinstance(f, BaseCode)
    f.set_macro()
    return f

@as_var("name")
def name(s):
    return rt._name(s)

@as_var("namespace")
def namespace(s):
    return rt._namespace(s)

@as_var("-try-catch")
def _try_catch(main_fn, ex, catch_fn, final):
    try:
        return main_fn.invoke([])
    except Exception as ex:
        if not isinstance(Exception, WrappedException):
            ex = RuntimeException(ex.message)
            return catch_fn.invoke([ex])
        else:
            return catch_fn.invoke([ex._ex])
    finally:
        final.invoke([])

@as_var("throw")
def _trow(ex):
    if isinstance(ex, RuntimeException):
        raise WrappedException(ex)
    raise WrappedException(RuntimeException(ex))

