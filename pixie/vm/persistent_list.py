import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
import pixie.vm.protocols as proto
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
        return PersistentList(self._first, self._next, meta)


@extend(proto._first, PersistentList)
def _first(x):
    return x._first

@extend(proto._next, PersistentList)
def _next(x):
    return x._next

@extend(proto._seq, PersistentList)
def _seq(x):
    return x

@extend(proto._count, PersistentList)
def _count(self):
    return rt.wrap(intmask(self._cnt))

@extend(proto._conj, PersistentList)
def _conj(self, itm):
    return PersistentList(itm, self, self._cnt + 1, nil)

def count(self):
        cnt = 0
        while self is not nil:
            self = self.next()
            cnt += 1
        return cnt

@as_var("list")
def list__args(args):
    i = r_uint(len(args))
    acc = nil
    while i > 0:
        acc = PersistentList(args[i - 1], acc, len(args) - i + 1, nil)
        i -= 1
    return acc


