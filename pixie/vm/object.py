

class Object(object):
    """ Base Object for all VM objects
    """

    def type(self):
        assert False, str(self)

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
        assert isinstance(name, unicode)
        _type_registry.register_type(name, self)
        self._name = name

    def type(self):
        return Type._type

Type._type = Type(u"Type")


