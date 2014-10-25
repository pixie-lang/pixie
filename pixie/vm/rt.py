__config__ = None
py_list = list
py_str = str
from rpython.rlib.objectmodel import specialize



def init():

    import pixie.vm.code as code
    from pixie.vm.object import affirm, _type_registry
    from rpython.rlib.rarithmetic import r_uint
    from pixie.vm.primitives import nil, true, false
    from pixie.vm.string import String
    from pixie.vm.object import Object

    _type_registry.set_registry(code._ns_registry)

    def unwrap(fn):
        if isinstance(fn, code.Var) and hasattr(fn.deref(), "_returns"):
            tp = fn.deref()._returns
            if tp is bool:
                def wrapper(*args):
                    ret = fn.invoke(py_list(args))
                    if ret is nil or ret is false:
                        return False
                    return True
                return wrapper
            elif tp is r_uint:
                return lambda *args: fn.invoke(py_list(args)).r_uint_val()
            elif tp is unicode:
                def wrapper(*args):
                    ret = fn.invoke(py_list(args))
                    if ret is nil:
                        return None
                    affirm(isinstance(ret, String), u"Invalid return value, expected String")
                    return ret._str
                return wrapper
            else:
                assert False, "Don't know how to convert" + str(tp)
        return lambda *args: fn.invoke(py_list(args))


    if globals().has_key("__inited__"):
        return

    import sys
    sys.setrecursionlimit(10000) # Yeah we blow the stack sometimes, we promise it's not a bug

    import pixie.vm.numbers as numbers
    from pixie.vm.code import wrap_fn
    import pixie.vm.interpreter
    import pixie.vm.stacklet as stacklet
    import pixie.vm.atom
    import pixie.vm.reduced
    import pixie.vm.util
    import pixie.vm.array
    import pixie.vm.lazy_seq
    import pixie.vm.persistent_list
    import pixie.vm.persistent_hash_map
    import pixie.vm.custom_types
    import pixie.vm.compiler as compiler
    import pixie.vm.map_entry
    import pixie.vm.reader as reader
    import pixie.vm.libs.platform
    import pixie.vm.libs.ffi



    numbers.init()

    @specialize.argtype(0)
    def wrap(x):
        if isinstance(x, int):
            return numbers.Integer(x)
        if isinstance(x, unicode):
            return String(x)
        if isinstance(x, py_str):
            return String(unicode(x))
        if isinstance(x, Object):
            return x
        affirm(False, u"Bad wrap")

    globals()["wrap"] = wrap

    from pixie.vm.code import _ns_registry, BaseCode, munge

    for name, var in _ns_registry._registry[u"pixie.stdlib"]._registry.iteritems():
        name = munge(name)
        print name
        if isinstance(var.deref(), BaseCode):
            globals()[name] = unwrap(var)
        else:
            globals()[name] = var


    import pixie.vm.bootstrap

    def reinit():
        for name, var in _ns_registry._registry[u"pixie.stdlib"]._registry.iteritems():
            name = munge(name)
            if name in globals():
                continue

            print "Found ->> ", name, var.deref()
            if isinstance(var.deref(), BaseCode):
                globals()[name] = unwrap(var)
            else:
                globals()[name] = var

    f = open("pixie/stdlib.lisp")
    data = f.read()
    f.close()
    rdr = reader.MetaDataReader(reader.StringReader(unicode(data)), u"pixie/stdlib.pixie")
    result = nil

    @wrap_fn
    def run_load_stdlib():
        with compiler.with_ns(u"pixie.stdlib"):
            while True:
                form = reader.read(rdr, False)
                if form is reader.eof:
                    return result
                result = compiler.compile(form).invoke([])
                reinit()

    stacklet.with_stacklets(run_load_stdlib)




    globals()["__inited__"] = True







