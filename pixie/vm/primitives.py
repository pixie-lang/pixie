from pixie.vm.effects.effects import Object, Type


class Nil(Object):
    _type = Type(u"pixie.stdlib.Nil")

    def type(self):
        return Nil._type


nil = Nil()


class Bool(Object):
    _type = Type(u"pixie.stdlib.Bool")

    def type(self):
        return Bool._type


true = Bool()
false = Bool()