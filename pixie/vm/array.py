import pixie.vm.rt as rt
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.code import extend, as_var
from pixie.vm.numbers import Integer
from pixie.vm.primitives import nil
import pixie.vm.stdlib as proto
import rpython.rlib.jit as jit
from rpython.rtyper.lltypesystem import lltype
from rpython.rlib.rarithmetic import intmask

UNROLL_IF_SMALLER_THAN = 8

class Array(object.Object):
    _type = object.Type(u"pixie.stdlib.Array")
    _immutable_fields_ = ["_list"]

    def __init__(self, lst):
        self._list = lst

    @jit.unroll_safe
    def reduce_small(self, f, init):
        for x in range(len(self._list)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, self._list[x]])
        return init

    def list(self):
        return self._list

    def reduce_large(self, f, init):
        for x in range(len(self._list)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, self._list[x]])
        return init

@extend(proto._count, Array)
def _count(self):
    assert isinstance(self, Array)
    return rt.wrap(len(self.list()))

@extend(proto._nth, Array)
def _nth(self, idx):
    assert isinstance(self, Array)
    ival = idx.int_val()
    if ival < len(self.list()):
        return self.list()[ival]
    else:
        affirm(False, u"Index out of Range")

@extend(proto._nth_not_found, Array)
def _nth_not_found(self, idx, not_found):
    assert isinstance(self, Array)
    ival = idx.int_val()
    if ival < len(self.list()):
        return self.list()[ival]
    else:
        return not_found

@extend(proto._reduce, Array)
def reduce(self, f, init):
    assert isinstance(self, Array)
    if len(self.list()) > UNROLL_IF_SMALLER_THAN:
        return self.reduce_large(f, init)
    return self.reduce_small(f, init)

@extend(proto._seq, Array)
def _seq(self):
    assert isinstance(self, Array)
    if rt.count(self) > 0:
        return ArraySeq(0, self)
    else:
        return nil

class ArraySeq(object.Object):
    _type = object.Type(u"pixie.stdlib.ArraySeq")
    _immutable_fields_ = ["_idx", "_w_array"]

    def __init__(self, idx, array):
        self._idx = idx
        self._w_array = array

    def first(self):
        return rt.nth(self._w_array, rt.wrap(self._idx))

    def next(self):
        if self._idx < rt.count(self._w_array) - 1:
            return ArraySeq(self._idx + 1, self._w_array)
        else:
            return nil

    def reduce(self, f, init):
        for x in range(self._idx, rt.count(self._w_array)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, rt.nth(self._w_array, rt.wrap(x))])
        return init

@extend(proto._first, ArraySeq)
def _first(self):
    assert isinstance(self, ArraySeq)
    return self.first()

@extend(proto._next, ArraySeq)
def _next(self):
    assert isinstance(self, ArraySeq)
    return self.next()

@extend(proto._seq, ArraySeq)
def _seq(self):
    assert isinstance(self, ArraySeq)
    return self

@extend(proto._reduce, ArraySeq)
def _reduce(self, f, init):
    assert isinstance(self, ArraySeq)
    return self.reduce(f, init)

def array(lst):
    assert isinstance(lst, list)
    return Array(lst)

@as_var("aget")
def aget(self, idx):
    affirm(isinstance(self, Array),  u"aget expects an Array as the first argument")
    affirm(isinstance(idx, Integer), u"aget expects an Integer as the second argument")
    return self.list()[idx.int_val()]

@as_var("aset")
def aset(self, idx, val):
    affirm(isinstance(self, Array),  u"aset expects an Array as the first argument")
    affirm(isinstance(idx, Integer), u"aset expects an Integer as the second argument")
    self.list()[idx.int_val()] = val
    return val

@as_var("aslice")
def aslice(self, offset):
    affirm(isinstance(self, Array),     u"aset expects an Array as the first argument")
    affirm(isinstance(offset, Integer), u"aset expects an Integer as the second argument")

    offset = offset.int_val()
    if offset >= 0:
        return Array(self.list()[offset:])
    else:
        rt.throw(rt.wrap(u"offset must be an Integer >= 0"))

@as_var("aconcat")
def aconcat(self, other):
    affirm(isinstance(self, Array) and isinstance(other, Array), 
            u"aconcat expects 2 Arrays")
    return Array(self.list() + other.list())

@as_var("alength")
def alength(self):
    affirm(isinstance(self, Array), u"alength expects an Array")

    return rt.wrap(len(self.list()))

@as_var("make-array")
def make_array(l):
    affirm(isinstance(l, Integer), u"l must be an Integer")
    return Array([nil] * l.int_val())


# ByteArray
ARRAY_OF_UCHAR = lltype.Array(lltype.Char)

class ByteArray(object.Object):
    _type = object.Type(u"pixie.stdlib.ByteArray")

    def __init__(self, size):
        self._cnt = size
        self._buffer = lltype.malloc(ARRAY_OF_UCHAR, size, flavor="raw")
        for x in range(size):
            self._buffer[x] = chr(0)


    def __del__(self):
        lltype.free(self._buffer, flavor="raw")


    @jit.unroll_safe
    def reduce_small(self, f, init):
        for x in range(self._cnt):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, rt.wrap(ord(self._buffer[x]))])
        return init


    def reduce_large(self, f, init):
        for x in range(self._cnt):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, rt.wrap(ord(self._buffer[x]))])
        return init


@as_var("byte-array")
def _byte_array(size):
    assert isinstance(size, Integer)
    v = size.r_uint_val()
    return ByteArray(v)

@extend(proto._reduce, ByteArray)
def _reduce(self, f, init):
    assert isinstance(self, ByteArray)
    if self._cnt > UNROLL_IF_SMALLER_THAN:
        return self.reduce_large(f, init)
    return self.reduce_small(f, init)

@extend(proto._nth, ByteArray)
def _nth(self, idx):
    assert isinstance(self, ByteArray)
    affirm(isinstance(idx, Integer), u"Index must be an integer")
    ival = idx.r_uint_val()
    if 0 <= ival < self._cnt:
        return rt.wrap(ord(self._buffer[ival]))

    return affirm(False, u"Index out of Range")

@extend(proto._nth_not_found, ByteArray)
def _nth_not_found(self, idx, not_found):
    assert isinstance(self, ByteArray)
    affirm(isinstance(idx, Integer), u"Index must be an integer")
    ival = idx.r_uint_val()
    if 0 <= ival < self._cnt:
        return rt.wrap(ord(self._buffer[ival]))

    return not_found

@extend(proto._count, ByteArray)
def _count(self):
    assert isinstance(self, ByteArray)
    return rt.wrap(intmask(self._cnt))
