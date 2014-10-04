

class Object(object):
    """ Base Object for all VM objects
    """

    def type(self):
        assert False, str(self)

class Type(Object):

    def __init__(self, name):
        assert isinstance(name, unicode)
        self._name = name

    def type(self):
        return Type._type

Type._type = Type(u"Type")


