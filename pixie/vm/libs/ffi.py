import rpython.rlib.rdynload as dynload
import pixie.vm.object as object
import pixie.vm.code as code
import pixie.vm.stdlib  as proto
from pixie.vm.code import as_var, affirm, extend
import pixie.vm.rt as rt
from rpython.rtyper.lltypesystem import rffi, lltype
from pixie.vm.primitives import nil
from pixie.vm.numbers import Integer, Float
from pixie.vm.string import String
from rpython.rlib import clibffi
from rpython.rlib.jit_libffi import jit_ffi_prep_cif, jit_ffi_call, CIF_DESCRIPTION
import rpython.rlib.jit as jit
from rpython.rlib.rarithmetic import intmask


"""
FFI interface for pixie.

This code gets a bit interesting. We use the RPython rlib module jit_libffi to do the interfacing, you can find
good docs in that module.

The problem is we can't serialize/translate function pointers (makes sense), so we make use of the _cleanup_ method
hook to clean out all unsupported fields. We then lazy re-load these values as needed. This allows us to specifiy FFI
functions inside of the stdlib (and other places) allowing for fast interpreter boot times.


"""

class ExternalLib(object.Object):
    _type = object.Type(u"pixie.stdlib.ExternalLib")

    def type(self):
        return ExternalLib._type

    def __init__(self, nm):
        assert isinstance(nm, unicode)
        self._name = nm
        self._is_inited = False
        self.thaw()

    def thaw(self):
        if not self._is_inited:
            s = rffi.str2charp(str(self._name))

            try:
                self._dyn_lib = dynload.dlopen(s)
            except dynload.DLOpenError as ex:
                raise object.WrappedException(object.RuntimeException(rt.wrap(ex.msg)))
            finally:
                rffi.free_charp(s)

            self._is_inited = True


    def get_fn_ptr(self, nm):
        assert isinstance(nm, unicode)
        self.thaw()
        s = rffi.str2charp(str(nm))
        sym = dynload.dlsym(self._dyn_lib, s)
        rffi.free_charp(s)
        return sym

    def _cleanup_(self):
        self._dyn_lib = lltype.nullptr(rffi.VOIDP.TO)
        self._is_inited = False


def get_native_size(tp):
    if tp == Integer._type:
        return rffi.sizeof(rffi.LONG)
    if tp == Float._type:
        return rffi.sizeof(rffi.DOUBLE)
    if tp == String._type:
        return rffi.sizeof(rffi.CCHARP)
    if tp == Buffer._type:
        return rffi.sizeof(rffi.CCHARP)
    if tp == FFIVoidP._type:
        return rffi.sizeof(rffi.VOIDP)
    assert False

def get_ret_val(ptr, tp):
    if tp == Integer._type:
        pnt = rffi.cast(rffi.LONGP, ptr)
        val = pnt[0]
        return Integer(val)
    if tp == Float._type:
        pnt = rffi.cast(rffi.DOUBLEP, ptr)
        val = pnt[0]
        return Float(val)
    if tp == String._type:
        pnt = rffi.cast(rffi.CCHARPP, ptr)
        if pnt[0] == lltype.nullptr(rffi.CCHARP.TO):
            return nil
        else:
            return String(unicode(rffi.charp2str(pnt[0])))

    if tp == FFIVoidP._type:
        pnt = rffi.cast(rffi.VOIDPP, ptr)
        val = pnt[0]
        return FFIVoidP(val)

    assert False

def set_native_value(ptr, val, tp):
    if tp is Integer._type:
        pnt = rffi.cast(rffi.LONGP, ptr)
        pnt[0] = rffi.cast(rffi.LONG, val.int_val())
        return rffi.ptradd(rffi.cast(rffi.CCHARP, pnt), rffi.sizeof(rffi.LONG))
    if tp is Float._type:
        pnt = rffi.cast(rffi.DOUBLEP, ptr)
        pnt[0] = rffi.cast(rffi.DOUBLE, val.float_val())
        return rffi.ptradd(rffi.cast(rffi.CCHARP, pnt), rffi.sizeof(rffi.DOUBLE))
    if tp is String._type:
        pnt = rffi.cast(rffi.CCHARPP, ptr)
        pnt[0] = rffi.str2charp(str(rt.name(val)))
        return rffi.ptradd(rffi.cast(rffi.CCHARP, pnt), rffi.sizeof(rffi.CCHARP))
    if tp is Buffer._type:
        pnt = rffi.cast(rffi.CCHARPP, ptr)
        pnt[0] = val.buffer()
        return rffi.ptradd(rffi.cast(rffi.CCHARP, pnt), rffi.sizeof(rffi.CCHARP))
    if tp is FFIVoidP._type:
        pnt = rffi.cast(rffi.VOIDPP, ptr)
        pnt[0] = val.voidp_data()
        return rffi.ptradd(rffi.cast(rffi.CCHARP, pnt), rffi.sizeof(rffi.VOIDP))
    assert False

class FFIFn(object.Object):
    _type = object.Type(u"pixie.stdlib.FFIFn")
    __immutable_fields__ = ["_is_inited?", "_lib", "_name", "_arg_types[*]", "_ret_type", \
                            "_transfer_size?", "_arg0_offset?", "_ret_offset?", "_cd?"]

    def type(self):
        return FFIFn._type

    def __init__(self, lib, name, arg_types, ret_type):
        self._rev = 0
        self._name = name
        self._lib = lib
        self._arg_types = arg_types
        self._ret_type = ret_type
        self._is_inited = False


    def thaw(self):
        if not self._is_inited:
            self._f_ptr = self._lib.get_fn_ptr(self._name)
            nargs = len(self._arg_types)

            exchange_buffer_size = nargs * rffi.sizeof(rffi.CCHARP)

            cd = lltype.malloc(CIF_DESCRIPTION, nargs, flavor="raw")
            cd.abi = clibffi.FFI_DEFAULT_ABI
            cd.nargs = nargs
            cd.rtype = get_clibffi_type(self._ret_type)

            atypes = lltype.malloc(clibffi.FFI_TYPE_PP.TO, nargs, flavor="raw")
            arg0_offset = exchange_buffer_size
            for idx in range(nargs):
                cd.exchange_args[idx] = exchange_buffer_size
                tp = self._arg_types[idx]
                native_size = get_native_size(tp)
                atypes[idx] = get_clibffi_type(tp)
                exchange_buffer_size += native_size

            ret_offset = exchange_buffer_size
            exchange_buffer_size += get_native_size(self._ret_type)



            cd.atypes = atypes
            cd.exchange_size = exchange_buffer_size
            cd.exchange_result = ret_offset
            cd.exchange_result_libffi = ret_offset

            jit_ffi_prep_cif(cd)
            self._cd = cd
            self._transfer_size = exchange_buffer_size
            self._arg0_offset = arg0_offset
            self._ret_offset = ret_offset

            self._is_inited = True

        return self

    def _cleanup_(self):
        self._rev += 1
        self._f_ptr = lltype.nullptr(rffi.VOIDP.TO)
        self._cd = lltype.nullptr(CIF_DESCRIPTION)
        self._is_inited = False

    @jit.unroll_safe
    def prep_exb(self, args):
        if not self._is_inited:
            self.thaw()
        exb = lltype.malloc(rffi.CCHARP.TO, self._transfer_size, flavor="raw")
        offset_p = rffi.ptradd(exb, self._arg0_offset)

        for x in range(len(self._arg_types)):
            offset_p = set_native_value(offset_p, args[x], self._arg_types[x])
        return exb

    def get_ret_val_from_buffer(self, exb):
        offset_p = rffi.ptradd(exb, self._cd.exchange_result_libffi)
        ret_val = get_ret_val(offset_p, self._ret_type)
        return ret_val

    @jit.unroll_safe
    def _invoke(self, args):

        exb = self.prep_exb(args)
        jit_ffi_call(self._cd, self._f_ptr, exb)
        ret_val = self.get_ret_val_from_buffer(exb)
        lltype.free(exb, flavor="raw")
        return ret_val

    def invoke(self, args):
        self = jit.promote(self)
        return self._invoke(args)



def get_clibffi_type(arg):
    if arg == Integer._type:
        return clibffi.cast_type_to_ffitype(rffi.LONG)
    if arg == Float._type:
        return clibffi.cast_type_to_ffitype(rffi.DOUBLE)
    if arg == String._type:
        return clibffi.ffi_type_pointer
    if arg == Buffer._type:
        return clibffi.ffi_type_pointer
    if arg == FFIVoidP._type:
        return clibffi.ffi_type_pointer
    assert False


@as_var("ffi-library")
def _ffi_library(ns):
    nm = rt.name(ns)
    return ExternalLib(nm)

@as_var("ffi-fn")
def _ffi_fn(lib, nm, args, ret_type):
    affirm(isinstance(lib, ExternalLib), u"First argument must be an ExternalLib")
    affirm(isinstance(ret_type, object.Type), u"Ret type must be a type")
    affirm(rt.namespace(nm) is None, u"Name must not be namespaced")

    cnt = rt.count(args)
    new_args = [None] * cnt
    for x in range(cnt):
        t = rt.nth(args, rt.wrap(x))
        affirm(isinstance(t, object.Type), u"Arg defs must be types")
        new_args[x] = t

    f = FFIFn(lib, rt.name(nm), new_args, ret_type)
    return f

class FFIVoidP(object.Object):
    _type = object.Type(u"pixie.stdlib.VoidP")

    def type(self):
        return FFIVoidP._type

    def __init__(self, data):
        self._voidp_data = data

    def voidp_data(self):
        return self._voidp_data




class Buffer(object.Object):
    """ Defines a byte buffer with non-gc'd (therefore non-movable) contents
    """
    _type = object.Type(u"pixie.stdlib.Buffer")

    def type(self):
        return Buffer._type

    def __init__(self, size):
        self._size = size
        self._used_size = 0
        self._buffer = lltype.malloc(rffi.CCHARP.TO, size, flavor="raw")


    def __del__(self):
        lltype.free(self._buffer, flavor="raw")

    def set_used_size(self, size):
        self._used_size = size

    def buffer(self):
        return self._buffer

    def count(self):
        return self._used_size

    def nth_char(self, idx):
        return self._buffer[idx]


@extend(proto._nth, Buffer)
def _nth(self, idx):
    return rt.wrap(ord(self.nth_char(idx.int_val())))

@extend(proto._count, Buffer)
def _count(self):
    return rt.wrap(self.count())

@as_var("buffer")
def buffer(size):
    return Buffer(size.int_val())

@as_var("set-buffer-count")
def set_buffer_size(self, size):
    self.set_used_size(size.int_val())
    return self
