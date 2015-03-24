import pixie.vm.object as object
from pixie.vm.primitives import nil
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
import pixie.vm.rt as rt
import rpython.rlib.jit as jit


class LazySeq(object.Object):
    _type = object.Type(u"pixie.stdlib.LazySeq")

    def type(self):
        return LazySeq._type

    def __init__(self, fn, meta=nil):
        self._fn = fn
        self._meta = meta
        self._s = nil

    @jit.jit_callback("lazy_seq_sval")
    def sval(self):
        if self._fn is None:
            return self._s
        else:
            self._s = self._fn.invoke([])
            self._fn = None
            return self._s

    @jit.dont_look_inside
    def lazy_seq_seq(self):
        self.sval()
        if self._s is not nil:
            ls = self._s
            while True:
                if isinstance(ls, LazySeq):
                    ls = ls.sval()
                    continue
                else:
                    self._s = ls
                    return rt.seq(self._s)
        else:
            return nil



@extend(proto._first, LazySeq)
def _first(self):
    assert isinstance(self, LazySeq)
    rt.seq(self)
    return rt.first(self._s)

@extend(proto._next, LazySeq)
def _next(self):
    assert isinstance(self, LazySeq)
    rt.seq(self)
    return rt.next(self._s)

@extend(proto._seq, LazySeq)
def _seq(self):
    assert isinstance(self, LazySeq)
    return self.lazy_seq_seq()


@as_var("lazy-seq*")
def lazy_seq(f):
    return LazySeq(f)
