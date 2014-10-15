

class Object(object):
    """ Base Object for all VM objects
    """

    def type(self):
        affirm(False, u".type isn't overloaded")

class TypeRegistry(object):
    def __init__(self):
        self._types = {}

    def register_type(self, nm, tp):
        self._types[nm] = tp

    def get_by_name(self, nm, default=None):
        return self._types.get(nm, default)

_type_registry = TypeRegistry()

class Type(Object):

    def __init__(self, name):
        assert isinstance(name, unicode), u"Type names must be unicode"
        _type_registry.register_type(name, self)
        self._name = name

    def type(self):
        return Type._type


Type._type = Type(u"Type")

class RuntimeException(Object):
    _type = Type(u"pixie.stdlib.RuntimeException")
    def __init__(self, data):
        self._data = data
        self._trace = []

    def __repr__(self):
        import pixie.vm.rt as rt
        return u"RuntimeException(" + rt._str(self._data)._str + u") \n" + u"\n".join(self._trace)

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
        from pixie.vm.string import String
        raise WrappedException(RuntimeException(String(msg)))




