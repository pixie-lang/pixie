import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
import pixie.vm.protocols as proto
from  pixie.vm.code import extend


class Cons(object.Object):
    _type = object.Type("Cons")

    def type(self):
        return Cons._type

    def __init__(self, head, tail, meta=nil):
        self._head = head
        self._tail = tail
        self._meta = meta

    def first(self):
        return self._head

    def next(self):
        return self._tail

    def meta(self):
        return self._meta

    def with_meta(self, meta):
        return Cons(self._head, self._tail, meta)


@extend(proto._first, Cons._type)
def _first(x):
    return x._head

@extend(proto._next, Cons._type)
def _next(x):
    return x._tail


def count(self):
        cnt = 0
        while self is not nil:
            self = self.next()
            cnt += 1
        return cnt

def cons(head, tail=nil):
    return Cons(head, tail, nil)