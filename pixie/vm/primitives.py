import pixie.vm.object as object

class Nil(object.Object):
    _type = object.Type(u"pixie.stdlib.Nil")

    def __repr__(self):
        return u"nil"

nil = Nil()

class Bool(object.Object):
    _type = object.Type(u"pixie.stdlib.Bool")

true = Bool()
false = Bool()
