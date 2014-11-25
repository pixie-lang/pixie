from pixie.vm.effects.effects import Object, Type, Answer
from pixie.vm.primitives import nil
from pixie.vm.code import extend, as_global, wrap_fn
import pixie.vm.rt as rt
from rpython.rlib.rarithmetic import intmask, r_uint


class PersistentList(Object):
    _type = Type(u"pixie.stdlib.PersistentList")

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

    def count(self):
        return self._cnt

    def with_meta(self, meta):
        return PersistentList(self._first, self._next, self._cnt, meta)






class EmptyList(Object):
    _type = Type(u"pixie.stdlib.EmptyList")
    def type(self):
        return EmptyList._type

    def __init__(self, meta=nil):
        self._meta = meta

    def meta(self):
        return self._meta

    def with_meta(self, meta):
        return EmptyList(meta)
    


@extend("pixie.stdlib.-first", PersistentList)
def _first(self):
    return self.first()

@extend("pixie.stdlib.-next", PersistentList)
def _next(self):
    return self.next()

@extend("pixie.stdlib.-seq", PersistentList)
def _seq(self):
    return self

@extend("pixie.stdlib.-count", PersistentList)
def _count(self):
    return rt.wrap(intmask(self.count()))

@extend("pixie.stdlib.-conj", PersistentList)
def _conj(self, itm):
    return PersistentList(itm, self, self.count() + 1, nil)

@extend("pixie.stdlib.-conj", nil._type)
def _conj(_, itm):
    return PersistentList(itm, nil, 1, nil)

@as_global("pixie.stdlib", "list")
@wrap_fn()
def list__args(args):
    if args.arg_count() == 0:
        return EmptyList()

    i = r_uint(args.arg_count())
    acc = nil
    while i > 0:
        acc = PersistentList(args.get_arg(i - 1), acc, args.arg_count() - i + 1, nil)
        i -= 1
    return acc

@extend("pixie.stdlib.-meta", PersistentList)
def _meta(self):
    return self.meta()

@extend("pixie.stdlib.-with-meta", PersistentList)
def _with_meta(self, meta):
    return self.with_meta(meta)

    




@extend("pixie.stdlib.-first", EmptyList)
def _first(self):
    return nil

@extend("pixie.stdlib.-next", EmptyList)
def _next(self):
    return nil

@extend("pixie.stdlib.-seq", EmptyList)
def _seq(self):
    return nil

@extend("pixie.stdlib.-count", EmptyList)
def _count(self):
    return rt.wrap(0)

@extend("pixie.stdlib.-conj", EmptyList)
def _conj(self, itm):
    return PersistentList(itm, nil, 1)

@extend("pixie.stdlib.-meta", EmptyList)
def _meta(self):
    return self.meta()

@extend("pixie.stdlib.-with-meta", EmptyList)
def _with_meta(self, meta):
    return self.with_meta(meta)

@extend("pixie.stdlib.-str", EmptyList)
def _str(self):
    return rt.wrap(u"()")

@extend("pixie.stdlib.-repr", EmptyList)
def _str(self):
    return rt.wrap(u"()")

@extend("pixie.stdlib.-reduce", EmptyList)
def _str(self, f, init):
    return init


