import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false



class Cons(object.Object):
    _type = object.Type("Cons")

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


def count(self):
        cnt = 0
        while self is not nil:
            self = self.next()
            cnt += 1
        return cnt

def cons(head, tail=nil):
    return Cons(head, tail, nil)