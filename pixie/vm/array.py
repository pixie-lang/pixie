import pixie.vm.rt as rt
from pixie.vm.effects.effects import Object, Type
from pixie.vm.primitives import nil
from pixie.vm.code import extend
import pixie.vm.stdlib as proto
import rpython.rlib.jit as jit
from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rlib.rarithmetic import intmask
from rpython.rlib.rarithmetic import build_int

UNROLL_IF_SMALLER_THAN = 8

class Array(Object):
    _type = Type(u"pixie.stdlib.Array")
    __immutable_fields__ = ["_list[*]"]
    def type(self):
        return Array._type

    def __init__(self, lst):
        self._list = lst

    def list(self):
        return self._list

    # @jit.unroll_safe
    # def reduce_small(self, f, init):
    #     for x in range(len(self._list)):
    #         if rt.reduced_QMARK_(init):
    #             return rt.deref(init)
    #         init = f.invoke([init, self._list[x]])
    #     return init
    #
    #
    # def reduce_large(self, f, init):
    #     for x in range(len(self._list)):
    #         if rt.reduced_QMARK_(init):
    #             return rt.deref(init)
    #         init = f.invoke([init, self._list[x]])
    #     return init

@extend("pixie.stdlib.-count", Array)
def _count(self):
    return rt.wrap(len(self.list()))

@extend("pixie.stdlib.-nth", Array)
def _nth(self, idx):
    ival = idx.int_val()
    if ival < len(self.list()):
        return self.list()[ival]
    else:
        return nil
#
# @extend(proto._reduce, Array)
# def reduce(self, f, init):
#     assert isinstance(self, Array)
#     if len(self._list) > UNROLL_IF_SMALLER_THAN:
#         return self.reduce_large(f, init)
#     return self.reduce_small(f, init)



def array(lst):
    return Array(lst)
#
# @as_var("aget")
# def aget(self, idx):
#     assert isinstance(self, Array)
#     return self._list[idx.int_val()]
#
# @as_var("aset")
# def aset(self, idx, val):
#     assert isinstance(self, Array)
#     self._list[idx.int_val()] = val
#     return val
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
#     return nil
#
# @extend(proto._count, ByteArray)
# def _count(self):
#     assert isinstance(self, ByteArray)
#     return rt.wrap(intmask(self._cnt))