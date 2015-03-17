import pixie.vm.object as object


class Nil(object.Object):
    _type = object.Type(u"pixie.stdlib.Nil")

    def __repr__(self):
        return u"nil"

    def type(self):
        return Nil._type


nil = Nil()


class Bool(object.Object):
    _type = object.Type(u"pixie.stdlib.Bool")

    def type(self):
        return Bool._type


true = Bool()
false = Bool()
