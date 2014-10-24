import rpython.rlib.rdynload as dynload
import pixie.vm.object as object
import pixie.vm.code as code
from pixie.vm.code import as_var, affirm
import pixie.vm.rt as rt
from rpython.rtyper.lltypesystem import rffi, lltype
from pixie.vm.numbers import Integer
from rpython.rlib.jit_libffi import CIF_DESCRIPTION
from rpython.rlib import clibffi
from rpython.rlib.jit_libffi import jit_ffi_prep_cif, jit_ffi_call


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
    assert False

def set_native_value(ptr, val, tp):
    if tp == Integer._type:
        pnt = rffi.cast(rffi.LONGP, ptr)
        pnt[0] = rffi.cast(rffi.LONG, val.int_val())
        return rffi.cast(rffi.CCHARP, rffi.ptradd(pnt, rffi.sizeof(rffi.LONG)))
    assert False

class FFIFn(object.Object):
    _type = object.Type(u"pixie.stdlib.FFIFn")

    def type(self):
        return FFIFn._type

    def __init__(self, lib, name, arg_types, ret_type):
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

            transfer_size += get_native_size(self._ret_type)

            cd = lltype.malloc(CIF_DESCRIPTION, 1, flavor="raw")
            cd.abi = clibffi.FFI_DEFAULT_ABI
            cd.nargs = len(self._arg_types)
            cd.rtype = get_clibffi_type(self._ret_type)
            atypes = lltype.malloc(clibffi.FFI_TYPE_PP.TO, len(self._arg_types), flavor="raw")
            for x in range(len(self._arg_types)):
                atypes[x] = get_clibffi_type(self._arg_types[x])



            cd.atypes = atypes
            cd.exchange_size = transfer_size
            cd.exchange_result = arg0_offset
            cd.exchange_result_libffi = arg0_offset
            cd.exchange_args[0] = arg0_offset

            jit_ffi_prep_cif(cd)
            self._cd = cd
            self._transfer_size = transfer_size
            self._arg0_offset = arg0_offset

        return self

    def _cleanup_(self):
        self._f_ptr = lltype.nullptr(rffi.VOIDP.TO)
        self._cd = lltype.nullptr(CIF_DESCRIPTION)
        self._is_inited = False

    def invoke(self, args):
        self.thaw()
        exb = lltype.malloc(rffi.CCHARP.TO, self._transfer_size, flavor="raw")
        offset_p = rffi.ptradd(exb, self._arg0_offset)
        for x in range(len(args)):
            offset_p = set_native_value(offset_p, args[x], self._arg_types[x])

        jit_ffi_call(self._cd, self._f_ptr, exb)
        lltype.free(exb, flavor="raw")
        return Integer(0)



def get_clibffi_type(arg):
    if arg == Integer._type:
        return clibffi.cast_type_to_ffitype(rffi.LONG)
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

    cnt = rt.count(args).int_val()
    new_args = [None] * cnt
    for x in range(cnt):
        t = rt.nth(args, rt.wrap(x))
        affirm(isinstance(t, object.Type), u"Arg defs must be types")
        new_args[x] = t

    f = FFIFn(lib, rt.name(nm), new_args, ret_type)
    return f


