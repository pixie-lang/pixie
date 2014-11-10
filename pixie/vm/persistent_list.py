import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
from pixie.vm.numbers import Integer
from rpython.rlib.rarithmetic import r_uint, intmask
import pixie.vm.rt as rt

class PersistentList(object.Object):
    _type = object.Type(u"pixie.stdlib.PersistentList")

    def type(self):
        return PersistentList._type

    def __init__(self, head, tail, cnt, meta=nil):
        self._first = head
        self._next = tail
        self._cnt = cnt
        self._meta = meta

    def first(self):
        return self._first

    def next(self):
        return self._next

    def meta(self):
        return self._meta

    def with_meta(self, meta):
        return PersistentList(self._first, self._next, self._cnt, meta)
    


@extend(proto._first, PersistentList)
def _first(self):
    assert isinstance(self, PersistentList)
    return self._first

@extend(proto._next, PersistentList)
def _next(self):
    assert isinstance(self, PersistentList)
    return self._next

@extend(proto._seq, PersistentList)
def _seq(self):
    assert isinstance(self, PersistentList)
    return self

@extend(proto._count, PersistentList)
def _count(self):
    assert isinstance(self, PersistentList)
    return rt.wrap(intmask(self._cnt))

@extend(proto._conj, PersistentList)
def _conj(self, itm):
    assert isinstance(self, PersistentList)
    return PersistentList(itm, self, self._cnt + 1, nil)

@extend(_conj, nil._type)
def _conj(_, itm):
    return PersistentList(itm, nil, 1, nil)

def count(self):
        cnt = 0
        while self is not nil:
            self = self.next()
            cnt += 1
        return cnt

@as_var("list")
def list__args(args):
    if len(args) == 0:
        return EmptyList()

    i = r_uint(len(args))
    acc = nil
    while i > 0:
        acc = PersistentList(args[i - 1], acc, len(args) - i + 1, nil)
        i -= 1
    return acc

@extend(proto._meta, PersistentList)
def _meta(self):
    assert isinstance(self, PersistentList)
    return self.meta()

@extend(proto._with_meta, PersistentList)
def _with_meta(self, meta):
    assert isinstance(self, PersistentList)
    return self.with_meta(meta)



    
class EmptyList(object.Object):
    _type = object.Type(u"pixie.stdlib.EmptyList")
    def type(self):
        return EmptyList._type
    
    def __init__(self, meta=nil):
        self._meta = meta
        
    def meta(self):
        return self._meta
    
    def with_meta(self, meta):
        return EmptyList(meta)
    




@extend(proto._first, EmptyList)
def _first(self):
    assert isinstance(self, EmptyList)
    return nil

@extend(proto._next, EmptyList)
def _next(self):
    assert isinstance(self, EmptyList)
    return nil

@extend(proto._seq, EmptyList)
def _seq(self):
    assert isinstance(self, EmptyList)
    return nil

@extend(proto._count, EmptyList)
def _count(self):
    assert isinstance(self, EmptyList)
    return rt.wrap(0)

@extend(proto._conj, EmptyList)
def _conj(self, itm):
    assert isinstance(self, EmptyList)
    return PersistentList(itm, nil, 1)

@extend(proto._meta, EmptyList)
def _meta(self):
    assert isinstance(self, EmptyList)
    return self.meta()

@extend(proto._with_meta, EmptyList)
def _with_meta(self, meta):
    assert isinstance(self, EmptyList)
    return self.with_meta(meta)

@extend(proto._str, EmptyList)
def _str(self):
    return rt.wrap(u"()")

@extend(proto._repr, EmptyList)
def _str(self):
    return rt.wrap(u"()")

@extend(proto._reduce, EmptyList)
def _str(self, f, init):
    return init


