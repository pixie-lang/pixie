import rpython.rlib.jit as jit
from rpython.rlib.objectmodel import we_are_translated

class Object(object):
    """ Base Object for all VM objects
    """
    _attrs_ = ()

    def type(self):
        affirm(False, u".type isn't overloaded")

    @jit.unroll_safe
    def invoke_k(self, args, stack):
        from pixie.vm2.code import intern_var
        var = intern_var(u"pixie.stdlib", u"-invoke")

        new_args = [None] * (len(args) + 1)

        new_args[0] = self
        for x in range(len(args)):
            new_args[x + 1] = args[x]

        return var.deref().invoke_k(new_args, stack)

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

    def get_field(self, k):
        runtime_error(u"Unsupported operation get-field")

    def to_str(self):
        tp = self.type()
        assert isinstance(tp, Type)
        return u"<inst " + tp._name + u">"

    def to_repr(self):
        tp = self.type()
        assert isinstance(tp, Type)
        return u"<inst " + tp._name + u">"



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

    def name(self):
        return self._name

    def type(self):
        return Type._type

    def add_subclass(self, tp):
        self._subclasses.append(tp)

    def subclasses(self):
        return self._subclasses

    def to_str(self):
        return u"<type " + self._name + u">"

    def to_repr(self):
        return u"<type " + self._name + u">"


Object._type = Type(u"pixie.stdlib.Object", None, False)
Type._type = Type(u"pixie.stdlib.Type")

@jit.elidable_promote()
def istypeinstance(obj_type, t):
    if not isinstance(obj_type, Type):
        return False
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

class Continuation(object):
    should_enter_jit = False
    _immutable_ = True
    def call_continuation(self, val, stack):
        return None, stack

    def get_ast(self):
        from pixie.vm2.primitives import nil
        return nil


class StackCell(object):
    """Defines an immutable call stack, stacks can be copied, spliced and combined"""
    _immutable_fields_ = ["_parent", "_cont"]
    def __init__(self, cont, parent_stack):
        self._parent = parent_stack
        self._cont = cont

def stack_cons(stack, other):
    return StackCell(other, stack)




class RuntimeException(Object):
    _type = Type(u"pixie.stdlib.RuntimeException")
    def __init__(self, msg, kw):
        self._msg = msg
        self._kw = kw

## TODO: fix
def affirm(f, msg):
    if not f:
        print msg
        raise WrappedException(RuntimeException(msg, u"pixie.stdlib.AssertionException"))

class WrappedException(BaseException):
    def __init__(self, ex):
        self._ex = ex

def runtime_error(msg, kw=None):
    print msg
    raise WrappedException(RuntimeException(msg, kw))

