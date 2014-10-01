import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
import pixie.vm.protocols as proto
from  pixie.vm.code import extend, as_var


class Cons(object.Object):
    _type = object.Type("Cons")

    def type(self):
        return Cons._type

    def __init__(self, head, tail, meta=nil):
        self._first = head
        self._next = tail
        self._meta = meta

    def first(self):
        return self._first

    def next(self):
        return self._next

    def meta(self):
        return self._meta

    def with_meta(self, meta):
        return Cons(self._first, self._next, meta)


@extend(proto._first, Cons._type)
def _first(x):
    return x._first

@extend(proto._next, Cons._type)
def _next(x):
    return x._next

@extend(proto._seq, Cons._type)
def _seq(x):
    return x

@as_var("cons")
def cons(head, tail):
    return Cons(head, tail)

def count(self):
        cnt = 0
        while self is not nil:
            self = self.next()
            cnt += 1
        return cnt

def cons(head, tail=nil):
    return Cons(head, tail, nil)