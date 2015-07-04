import pixie.vm2.rt as rt
import pixie.vm2.object as object
from pixie.vm2.object import affirm
from pixie.vm2.code import extend, as_var
from pixie.vm2.numbers import Integer
from pixie.vm2.primitives import nil
#import pixie.vm.stdlib as proto
import rpython.rlib.jit as jit
from rpython.rtyper.lltypesystem import lltype
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.objectmodel import we_are_translated
from pixie.vm2.keyword import keyword
import pixie.vm2.rt as rt
UNROLL_IF_SMALLER_THAN = 8

KW_count = keyword(u"count")


class Array(object.Object):
    _type = object.Type(u"pixie.stdlib.Array")
    _immutable_fields_ = ["_list"]
    def type(self):
        return Array._type

    def __init__(self, lst):
        if we_are_translated():
            for x in lst:
                assert x is not None
        self._list = lst

    @jit.unroll_safe
    def reduce_small(self, f, init):
        for x in range(len(self._list)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, self._list[x]])
        return init


    def reduce_large(self, f, init):
        for x in range(len(self._list)):
            if rt.reduced_QMARK_(init):
                return rt.deref(init)
            init = f.invoke([init, self._list[x]])
        return init

    def get_field(self, k, not_found):
        if k is KW_count:
            return rt.wrap(len(self._list))
        return not_found

    def array_val(self):
        return self._list

@as_var("array")
def array__args(lst):
    return Array(lst)

@as_var("make-array")
def _make_array(size):
    return Array([nil] * size.int_val())

#@extend(proto._count, Array)
#def _count(self):
#    assert isinstance(self, Array)
#    return rt.wrap(len(self._list))
#
# @extend(proto._nth, Array)
# def _nth(self, idx):
#     assert isinstance(self, Array)
#     ival = idx.int_val()
#     if ival < len(self._list):
#         return self._list[ival]
#     else:
#         affirm(False, u"Index out of Range")
#
# @extend(proto._nth_not_found, Array)
# def _nth_not_found(self, idx, not_found):
#     assert isinstance(self, Array)
#     ival = idx.int_val()
#     if ival < len(self._list):
#         return self._list[ival]
#     else:
#         return not_found
#
# @extend(proto._reduce, Array)
# def reduce(self, f, init):
#     assert isinstance(self, Array)
#     if len(self._list) > UNROLL_IF_SMALLER_THAN:
#         return self.reduce_large(f, init)
#     return self.reduce_small(f, init)
#
# @extend(proto._seq, Array)
# def _seq(self):
#     assert isinstance(self, Array)
#     if rt.count(self) > 0:
#         return ArraySeq(0, self)
#     else:
#         return nil
#
# class ArraySeq(object.Object):
#     _type = object.Type(u"pixie.stdlib.ArraySeq")
#     _immutable_fields_ = ["_idx", "_w_array"]
#
#     def __init__(self, idx, array):
#         self._idx = idx
#         self._w_array = array
#
#     def first(self):
#         return rt.nth(self._w_array, rt.wrap(self._idx))
#
#     def next(self):
#         if self._idx < rt.count(self._w_array) - 1:
#             return ArraySeq(self._idx + 1, self._w_array)
#         else:
#             return nil
#
#     def reduce(self, f, init):
#         for x in range(self._idx, rt.count(self._w_array)):
#             if rt.reduced_QMARK_(init):
#                 return rt.deref(init)
#             init = f.invoke([init, rt.nth(self._w_array, rt.wrap(x))])
#         return init
#
#     def type(self):
#         return self._type
# #
# @extend(proto._first, ArraySeq)
# def _first(self):
#     assert isinstance(self, ArraySeq)
#     return self.first()
#
# @extend(proto._next, ArraySeq)
# def _next(self):
#     assert isinstance(self, ArraySeq)
#     return self.next()
#
# @extend(proto._seq, ArraySeq)
# def _seq(self):
#     assert isinstance(self, ArraySeq)
#     return self
#
# @extend(proto._reduce, ArraySeq)
# def _reduce(self, f, init):
#     assert isinstance(self, ArraySeq)
#     return self.reduce(f, init)
#
# def array(lst):
#     assert isinstance(lst, list)
#     return Array(lst)
#
@as_var("aget")
def aget(self, idx):
    assert isinstance(self, Array)
    return self._list[idx.int_val()]

@as_var("aset")
def aset(self, idx, val):
    assert isinstance(self, Array)
    self._list[idx.int_val()] = val
    return val

#
# @as_var("aslice")
# def aslice(self, offset):
#     assert isinstance(self, Array) and isinstance(offset, Integer)
#
#     offset = offset.int_val()
#     if offset >= 0:
#         return Array(self._list[offset:])
#     else:
#         rt.throw(rt.wrap(u"offset must be an Integer >= 0"))
#
# @as_var("aconcat")
# def aconcat(self, other):
#     assert isinstance(self, Array) and isinstance(other, Array)
#     return Array(self._list + other._list)
#
# @as_var("alength")
# def alength(self):
#     assert isinstance(self, Array)
#     return rt.wrap(len(self._list))
#
# @as_var("make-array")
# def make_array(l):
#     affirm(isinstance(l, Integer), u"l must be an Integer")
#     return Array([nil] * l.int_val())
#
#
# # ByteArray
# ARRAY_OF_UCHAR = lltype.Array(lltype.Char)
#
# class ByteArray(object.Object):
#     _type = object.Type(u"pixie.stdlib.ByteArray")
#
#     def __init__(self, size):
#         self._cnt = size
#         self._buffer = lltype.malloc(ARRAY_OF_UCHAR, size, flavor="raw")
#         for x in range(size):
#             self._buffer[x] = chr(0)
#
#     def type(self):
#         return ByteArray._type
#
#
#     def __del__(self):
#         lltype.free(self._buffer, flavor="raw")
#
#
#     @jit.unroll_safe
#     def reduce_small(self, f, init):
#         for x in range(self._cnt):
#             if rt.reduced_QMARK_(init):
#                 return rt.deref(init)
#             init = f.invoke([init, rt.wrap(ord(self._buffer[x]))])
#         return init
#
#
#     def reduce_large(self, f, init):
#         for x in range(self._cnt):
#             if rt.reduced_QMARK_(init):
#                 return rt.deref(init)
#             init = f.invoke([init, rt.wrap(ord(self._buffer[x]))])
#         return init
#
#
# @as_var("byte-array")
# def _byte_array(size):
#     assert isinstance(size, Integer)
#     v = size.r_uint_val()
#     return ByteArray(v)
#
# @extend(proto._reduce, ByteArray)
# def _reduce(self, f, init):
#     assert isinstance(self, ByteArray)
#     if self._cnt > UNROLL_IF_SMALLER_THAN:
#         return self.reduce_large(f, init)
#     return self.reduce_small(f, init)
#
# @extend(proto._nth, ByteArray)
# def _nth(self, idx):
#     assert isinstance(self, ByteArray)
#     affirm(isinstance(idx, Integer), u"Index must be an integer")
#     ival = idx.r_uint_val()
#     if 0 <= ival < self._cnt:
#         return rt.wrap(ord(self._buffer[ival]))
#
#     return affirm(False, u"Index out of Range")
#
# @extend(proto._nth_not_found, ByteArray)
# def _nth_not_found(self, idx, not_found):
#     assert isinstance(self, ByteArray)
#     affirm(isinstance(idx, Integer), u"Index must be an integer")
#     ival = idx.r_uint_val()
#     if 0 <= ival < self._cnt:
#         return rt.wrap(ord(self._buffer[ival]))
#
#     return not_found
#
# @extend(proto._count, ByteArray)
# def _count(self):
#     assert isinstance(self, ByteArray)
#     return rt.wrap(intmask(self._cnt))
