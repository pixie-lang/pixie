__config__ = None
py_list = list
import pixie.vm.code as code
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint

def unwrap(fn):
    if isinstance(fn, code.Var) and hasattr(fn.deref(), "_returns"):
        tp = fn.deref()._returns
        if tp is bool:
            def wrapper(*args):
                ret = fn.invoke(py_list(args))
                if ret is nil or ret is false:
                    return false
                return true
            return wrapper
        elif tp is r_uint:
            return lambda *args: fn.invoke(py_list(args)).r_uint_val()
        else:
            assert False, "Don't know how to convert" + str(tp)
    return lambda *args: fn.invoke(py_list(args))

def init():
    if globals().has_key("__inited__"):
        return

    import sys
    sys.setrecursionlimit(10000) # Yeah we blow the stack sometimes, we promise it's not a bug

    import pixie.vm.numbers as numbers
    import pixie.vm.code
    import pixie.vm.interpreter
    import pixie.vm.stacklet
    import pixie.vm.atom
    import pixie.vm.reduced
    import pixie.vm.util
    import pixie.vm.array
    import pixie.vm.lazy_seq
    import pixie.vm.persistent_list
    import pixie.vm.persistent_hash_map
    import pixie.vm.custom_types
    import pixie.vm.compiler

    numbers.init()

    from pixie.vm.code import _ns_registry, BaseCode, munge

    for name, var in _ns_registry._registry[u"pixie.stdlib"]._registry.iteritems():
        name = munge(name)
        print name
        if isinstance(var.deref(), BaseCode):
            globals()[name] = unwrap(var)
        else:
            globals()[name] = var


    import pixie.vm.bootstrap

    for name, var in _ns_registry._registry[u"pixie.stdlib"]._registry.iteritems():
        name = munge(name)
        if name in globals():
            print "skipping", name
            continue

        print name
        if isinstance(var.deref(), BaseCode):
            globals()[name] = unwrap(var)
        else:
            globals()[name] = var

    globals()["__inited__"] = True






