from rpython.rlib.objectmodel import compute_identity_hash
import rpython.rlib.jit as jit


class FinalizerRegistry(object):
    def __init__(self):
        # TODO: PyPy uses a linked list, investigate if we need that too
        self._registry = []

    def register(self, o):
        print "register finalizer ", o
        self._registry.append(o)

    def run_finalizers(self):
        import pixie.vm.rt as rt

        vals = self._registry
        self._registry = []
        for x in vals:
            rt._finalize_BANG_(x)

finalizer_registry = FinalizerRegistry()

class Object(object):
    """ Base Object for all VM objects
    """
    _attrs_ = ()

    def type(self):
        affirm(False, u".type isn't overloaded")

    @jit.unroll_safe
    def invoke(self, args):
        import pixie.vm.stdlib as stdlib
        return stdlib.invoke_other(self, args)

    def int_val(self):
        affirm(False,  u"Expected Number, not " + self.type().name())
        return 0

    def r_uint_val(self):
        affirm(False, u"Expected Number, not " + self.type().name())
        return 0

    def hash(self):
        import pixie.vm.rt as rt
        return rt.wrap(compute_identity_hash(self))

    def promote(self):
        return self





class TypeRegistry(object):
    def __init__(self):
        self._types = {}
        self._ns_registry = None

    def register_type(self, nm, tp):
        if self._ns_registry is None:
            self._types[nm] = tp
        else:
            self.var_for_type_and_name(nm, tp)

    def var_for_type_and_name(self, nm, tp):
        splits = nm.split(u".")
        size = len(splits) - 1
        assert size >= 0
        ns = u".".join(splits[:size])
        name = splits[size]
        var = self._ns_registry.find_or_make(ns).intern_or_make(name)
        var.set_root(tp)
        return var

    def set_registry(self, registry):
        self._ns_registry = registry
        for nm in self._types:
            tp = self._types[nm]
            self.var_for_type_and_name(nm, tp)


    def get_by_name(self, nm, default=None):
        return self._types.get(nm, default)

_type_registry = TypeRegistry()

def get_type_by_name(nm):
    return _type_registry.get_by_name(nm)

class Type(Object):
    _immutable_fields_ = ["_name", "_has_finalizer?"]
    def __init__(self, name, parent=None, object_inited=True):
        assert isinstance(name, unicode), u"Type names must be unicode"
        _type_registry.register_type(name, self)
        self._name = name

        if object_inited:
            if parent is None:
                parent = Object._type

            parent.add_subclass(self)

        self._parent = parent
        self._subclasses = []
        self._has_finalizer = False

    def name(self):
        return self._name

    def type(self):
        return Type._type

    def parent(self):
        return self._parent

    def add_subclass(self, tp):
        self._subclasses.append(tp)

    def subclasses(self):
        return self._subclasses

    @jit.elidable_promote()
    def has_finalizer(self):
        return self._has_finalizer

    def set_finalizer(self):
        self._has_finalizer = True


Object._type = Type(u"pixie.stdlib.Object", None, False)
Type._type = Type(u"pixie.stdlib.Type")

@jit.elidable_promote()
def istypeinstance(obj, t):
    obj_type = obj.type()
    assert isinstance(obj_type, Type)
    if obj_type is t:
        return True
    elif obj_type._parent is not None:
        obj_type = obj_type._parent
        while obj_type is not None:
            if obj_type is t:
                return True
            obj_type = obj_type._parent
        return False
    else:
        return False

class RuntimeException(Object):
    _type = Type(u"pixie.stdlib.RuntimeException")
    def __init__(self, msg, data):
        assert data is not None
        assert msg is not None
        self._msg = msg
        self._data = data
        self._trace = []

    def type(self):
        return RuntimeException._type

    def __repr__(self):
        import pixie.vm.rt as rt
        s = []
        trace = self._trace[:]
        trace.reverse()
        for x in trace:
            s.append(x.__repr__())
            s.append(u"\n")
        s.extend([u"RuntimeException: " + rt.name(rt.str(self._data)) + u" " +
                  rt.name(rt.str(self._msg)) + u"\n"])

        return u"".join(s)

class WrappedException(Exception):
    def __init__(self, ex):
        assert isinstance(ex, RuntimeException)
        self._ex = ex

    def __repr__(self):
        return repr(self._ex)

    def __str__(self):
        return repr(self._ex)

def affirm(val, msg):
    """Works a lot like assert except it throws RuntimeExceptions"""
    assert isinstance(msg, unicode)
    if not val:
        import pixie.vm.rt as rt
        from pixie.vm.keyword import keyword
        raise WrappedException(RuntimeException(rt.wrap(msg), keyword(u"pixie.stdlib/AssertionException")))

def runtime_error(msg, data=None):
    import pixie.vm.rt as rt
    from pixie.vm.keyword import keyword
    if data is None:
        data = u"pixie.stdlib/AssertionException"
    raise WrappedException(RuntimeException(rt.wrap(msg), keyword(data)))

def safe_invoke(f, args):
    try:
        f.invoke(args)
    except Exception as ex:
        if isinstance(ex, WrappedException):
            print "UNSAFE EXCEPTION", ex._ex.__repr__()
        else:
            print "UNSAFE EXCEPTION", ex
    return None

class ErrorInfo(Object):
    _type = Type(u"pixie.stdlib.ErrorInfo")
    def type(self):
        return ErrorInfo._type
    def __init__(self):
        pass

class InterpreterCodeInfo(ErrorInfo):
    def __init__(self, line, line_number, column_number, file):
        self._line = line
        self._line_number = line_number
        self._column_number = column_number
        self._file = file

    def pad_chars(self):
        chrs = []
        for x in range(self._column_number - 1):
            chrs += u" "
        return u"".join(chrs)

    def __repr__(self):
        return u"in " + self._file + u" at " + unicode(str(self._line_number)) \
               + u":" + unicode(str(self._column_number)) + u"\n" \
               + self._line.__repr__() + u"\n" \
               + self.pad_chars() + u"^"

    def interpreter_code_info_state(self):
        return self._line, self._line_number, self._column_number, self._file

    def trace_map(self):
        from pixie.vm.string import String
        from pixie.vm.numbers import Integer
        from pixie.vm.keyword import keyword

        tm = {keyword(u"type") : keyword(u"interpreter")}
        tm[keyword(u"line")] = String(self._line.__repr__())
        tm[keyword(u"line-number")] = Integer(self._line_number)
        tm[keyword(u"column-number")] = Integer(self._column_number)
        tm[keyword(u"file")] = String(self._file)
        return tm

class NativeCodeInfo(ErrorInfo):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return u"in internal function " + self._name + u"\n"

    def trace_map(self):
        from pixie.vm.string import String
        from pixie.vm.numbers import Integer
        from pixie.vm.keyword import keyword

        tm = {keyword(u"type") : keyword(u"native")}
        tm[keyword(u"name")] = String(self._name)
        return tm

class PolymorphicCodeInfo(ErrorInfo):
    def __init__(self, name, tp):
        self._name = name
        self._tp = tp

    def __repr__(self):
        tp = self._tp
        assert isinstance(tp, Type)
        return u"in polymorphic function " + self._name + u" dispatching on " + tp._name + u"\n"

    def trace_map(self):
        from pixie.vm.string import String
        from pixie.vm.keyword import keyword

        tp = self._tp
        assert isinstance(tp, Type)
        tm = {keyword(u"type") : keyword(u"polymorphic")}
        tm[keyword(u"name")] = String(self._name)
        tm[keyword(u"tp")] = String(tp._name)
        return tm

class PixieCodeInfo(ErrorInfo):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return u"in pixie function " + self._name + u"\n"

    def trace_map(self):
        from pixie.vm.string import String
        from pixie.vm.keyword import keyword

        tm = {keyword(u"type") : keyword(u"pixie")}
        tm[keyword(u"name")] = String(self._name)
        return tm

class ExtraCodeInfo(ErrorInfo):
    def __init__(self, str, data=None):
        self._str = str
        self._data = data

    def __repr__(self):
        return self._str

    def trace_map(self):
        import pixie.vm.rt as rt
        from pixie.vm.keyword import keyword

        tm = {keyword(u"type"): keyword(u"extra"),
              keyword(u"msg"): rt.wrap(self._str)}

        if self._data:
            tm[keyword(u"data")] = self._data

        return tm


def add_info(ex, data):
    assert isinstance(ex, WrappedException)
    ex._ex._trace.append(ExtraCodeInfo(data))
    return ex
