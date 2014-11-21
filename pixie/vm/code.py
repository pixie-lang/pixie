py_object = object
import pixie.vm.object as object
from pixie.vm.effects.effect_transform import cps

from pixie.vm.effects.effects import Object, Type, raise_Ef
from pixie.vm.effects.environment import FindPolymorphicOverride, extend_builtin, extend_builtin2, add_builtin, \
                                         FindDoublePolymorphicOverride, ExceptionEffect

def munge(s):
     return s.replace("-", "_").replace("?", "_QMARK_").replace("!", "_BANG_")


class NativeFn(Object):
    _type = Type(u"pixie.stdlib.NativeFn")

    def invoke_Ef(self, args):
        raise NotImplementedError()

## PYTHON FLAGS
CO_VARARGS = 0x4
def wrap_fn(transform=True):
    def with_fn(fn):
        if transform:

            fn = cps(fn)

        """Converts a native Python function into a pixie function."""
        def as_native_fn(f):
            return type("W"+fn.__name__, (NativeFn,), {"invoke_Ef": f})()

        def as_variadic_fn(f):
            return type("W"+fn.__name__[:len("__args")], (NativeFn,), {"invoke_Ef": f})()

        code = fn.func_code
        if fn.__name__.endswith("__args"):
            return as_variadic_fn(lambda self, args: fn(args))

        fn_name = unicode(getattr(fn, "__real_name__", fn.__name__))

        if code.co_flags & CO_VARARGS:
            raise Exception("Variadic functions not supported by wrap")
        else:
            argc = code.co_argcount
            if argc == 0:
                def wrapped_fn(self, args):
                    #affirm(len(args) == 0, u"Expected 0 arguments to " + fn_name)
                    try:
                        return fn()
                    except object.WrappedException as ex:
                        ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                        raise
                return as_native_fn(wrapped_fn)

            if argc == 1:
                def wrapped_fn(self, args):
                    #affirm(len(args) == 1, u"Expected 1 arguments to " + fn_name)
                    try:
                        return fn(args.get_arg(0))
                    except object.WrappedException as ex:
                        ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                        raise
                return as_native_fn(wrapped_fn)

            if argc == 2:
                def wrapped_fn(self, args):
                    #affirm(len(args) == 2, u"Expected 2 arguments to " + fn_name)
                    try:
                        return fn(args.get_arg(0), args.get_arg(1))
                    except object.WrappedException as ex:
                        ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                        raise
                return as_native_fn(wrapped_fn)
            if argc == 3:
                def wrapped_fn(self, args):
                    #affirm(len(args) == 3, u"Expected 3 arguments to " + fn_name)

                    try:
                        return fn(args.get_arg(0), args.get_arg(1), args.get_arg(2))
                    except object.WrappedException as ex:
                        ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                        raise
                return as_native_fn(wrapped_fn)

            if argc == 4:
                def wrapped_fn(self, args):
                    #affirm(len(args) == 4, u"Expected 4 arguments to " + fn_name)

                    try:
                        return fn(args.get_arg(0), args.get_arg(1), args.get_arg(2), args.get_arg(3))
                    except object.WrappedException as ex:
                        ex._ex._trace.append(object.NativeCodeInfo(fn_name))
                        raise
                return as_native_fn(wrapped_fn)

            assert False, "implement more"

    return with_fn



class PolymorphicFn(Object):
    _type = Type(u"pixie.stdlib.PolymorphicFn")

    def __init__(self, name):
        self._w_name = name

    @cps
    def invoke_Ef(self, args):
        if args.arg_count() == 0:
            pass
            # TODO throw exception effect

        tp = args.get_arg(0).type()
        eff = FindPolymorphicOverride(self._w_name, tp)
        result = raise_Ef(eff)

        if result is None:
            from pixie.vm.keyword import keyword
            from pixie.vm.string import String
            eff = ExceptionEffect(keyword(u"NO-OVERRIDE"), String(u""))
            raise_Ef(eff)

        return result.invoke_Ef(args)

class DoublePolymorphicFn(Object):
    _type = Type(u"pixie.stdlib.DoublePolymorphicFn")

    def __init__(self, name):
        self._w_name = name

    @cps
    def invoke_Ef(self, args):
        if args.arg_count() <= 1:
            pass
            # TODO throw exception effect

        tp1 = args.get_arg(0).type()
        tp2 = args.get_arg(1).type()
        eff = FindDoublePolymorphicOverride(self._w_name, tp1, tp2)
        result = raise_Ef(eff)

        if result is None:
            from pixie.vm.keyword import keyword
            from pixie.vm.string import String
            eff = ExceptionEffect(keyword(u"NO-OVERRIDE"), String(u""))
            raise_Ef(eff)

        return result.invoke_Ef(args)


def extend(pfn, tp1, tp2=None):
    """Extends a protocol to the given Type (not python type), with the decorated function
       wraps the decorated function"""

    from pixie.vm.keyword import keyword

    pfn = keyword(unicode(pfn))

    if isinstance(tp1, type):
        tp1 = tp1._type

    def extend_inner(fn):
        if tp2 is None:
            extend_builtin(pfn, tp1, wrap_fn()(fn))
        else:
            extend_builtin2(pfn, tp1, tp2, wrap_fn()(fn))


def as_global(ns, nm):
    from pixie.vm.keyword import keyword
    def with_f(val):
        add_builtin(keyword(ns), keyword(nm), val)
        return val
    return with_f

import inspect
def defprotocol(ns, name, methods):
    """Define a protocol in the given namespace with the given name and methods, vars will
       be created in the namespace for the protocol and methods. This function will dump
       variables for the created protocols/methods in the globals() where this function is called."""

    from pixie.vm.keyword import keyword
    from pixie.vm.rt import munge

    ns = unicode(ns)
    name = unicode(name)
    methods = map(unicode, methods)
    gbls = inspect.currentframe().f_back.f_globals
    #proto =  Protocol(name)
    #intern_var(ns, name).set_root(proto)
    #gbls[munge(name)] = proto

    for method in methods:
        pkw = keyword(ns+"."+method)
        poly = PolymorphicFn(pkw)
        add_builtin(keyword(ns), keyword(method), poly)
        gbls[munge(method)] = poly
