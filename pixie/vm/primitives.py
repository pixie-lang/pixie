import pixie.vm.object as object


class Nil(object.Object):
    _type = object.Type("NilType")

    def type(self):
        return Nil._type


nil = Nil()


class Bool(object.Object):
    _type = object.Type("BoolType")

    def type(self):
        return Bool._type


true = Bool()
false = Bool()