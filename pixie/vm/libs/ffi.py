import rpython.rlib.rdynload as dynload
import pixie.vm.object as object
import pixie.vm.code as code
from pixie.vm.code import as_var, affirm
import pixie.vm.rt as rt
from rpython.rtyper.lltypesystem import rffi, lltype
from pixie.vm.primitives import nil
from pixie.vm.numbers import Integer
from pixie.vm.string import String
from rpython.rlib.jit_libffi import CIF_DESCRIPTION
from rpython.rlib import clibffi
from rpython.rlib.jit_libffi import jit_ffi_prep_cif, jit_ffi_call
import rpython.rlib.jit as jit


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
    if tp == String._type:
        return rffi.sizeof(rffi.CCHARP)
    assert False

def get_ret_val(ptr, tp):
    if tp == Integer._type:
        pnt = rffi.cast(rffi.LONGP, ptr)
        val = pnt[0]
        return Integer(val)
    if tp == String._type:
        pnt = rffi.cast(rffi.CCHARPP, ptr)
        if pnt[0] == lltype.nullptr(rffi.CCHARP.TO):
            return nil
        else:
            return String(rffi.charp2str(pnt[0]))

    assert False

def set_native_value(ptr, val, tp):
    if tp is Integer._type:
        pnt = rffi.cast(rffi.LONGP, ptr)
        pnt[0] = rffi.cast(rffi.LONG, val.int_val())
        return rffi.cast(rffi.CCHARP, rffi.ptradd(pnt, rffi.sizeof(rffi.LONG)))
    if tp is String._type:
        pnt = rffi.cast(rffi.CCHARPP, ptr)
        pnt[0] = rffi.str2charp(str(rt.name(val)))
        return rffi.cast(rffi.CCHARP, rffi.ptradd(pnt, rffi.sizeof(rffi.CCHARP)))
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
            transfer_size = 0
            arg0_offset = len(self._arg_types) * rffi.sizeof(rffi.CCHARP)
            exchange_result = arg0_offset
            for x in self._arg_types:
                exchange_result = transfer_size
                transfer_size += get_native_size(x)

            ret_offset = transfer_size
            transfer_size += get_native_size(self._ret_type)

            cd = lltype.malloc(CIF_DESCRIPTION, len(self._arg_types), flavor="raw")
            cd.abi = clibffi.FFI_DEFAULT_ABI
            cd.nargs = len(self._arg_types)
            cd.rtype = get_clibffi_type(self._ret_type)
            atypes = lltype.malloc(clibffi.FFI_TYPE_PP.TO, len(self._arg_types), flavor="raw")
            for x in range(len(self._arg_types)):
                atypes[x] = get_clibffi_type(self._arg_types[x])



            cd.atypes = atypes
            cd.exchange_size = transfer_size
            cd.exchange_result = ret_offset
            cd.exchange_result_libffi = ret_offset
            cd.exchange_args[0] = arg0_offset

            jit_ffi_prep_cif(cd)
            self._cd = cd
            self._transfer_size = transfer_size
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
    def _invoke(self, args):
        if not self._is_inited:
            self.thaw()
        exb = lltype.malloc(rffi.CCHARP.TO, self._transfer_size, flavor="raw")
        offset_p = rffi.ptradd(exb, self._arg0_offset)

        for x in range(len(self._arg_types)):
            offset_p = set_native_value(offset_p, args[x], self._arg_types[x])

        jit_ffi_call(self._cd, self._f_ptr, exb)
        offset_p = rffi.ptradd(exb, self._ret_offset)
        ret_val = get_ret_val(offset_p, self._ret_type)
        lltype.free(exb, flavor="raw")
        return ret_val

    def invoke(self, args):
        self = jit.promote(self)
        return self._invoke(args)



def get_clibffi_type(arg):
    if arg == Integer._type:
        return clibffi.cast_type_to_ffitype(rffi.LONG)
    if arg == String._type:
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


