

class Object(object):
    """ Base Object for all VM objects
    """

    def type(self):
        assert False;

class Type(Object):

    def __init__(self, name):
        self.name = name

    def type(self):
        return Type._type

Type._type = Type("Type")


