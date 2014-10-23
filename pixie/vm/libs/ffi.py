import rpython.rlib.rdynload as dynload
import pixie.vm.object as object
import pixie.vm.code as code
import pixie.vm.rt as rt
from rpython.rtyper.lltypesystem import rffi, lltype
from pixie.vm.numbers import Integer
from rpython.rlib.jit_libffi import CIF_DESCRIPTION
from rpython.rlib import clibffi
from rpython.rlib.jit_libffi import jit_ffi_prep_cif, jit_ffi_call

class ExternalLib(object.Object):
    _type = object.Type(u"pixie.stdlib.ExternalLib")

    def type(self):
        return ExternalLib._type

    def __init__(self, nm):
        assert isinstance(nm, unicode)
        s = rffi.str2charp(str(nm))
        self._dyn_lib = dynload.dlopen(s)
        rffi.free_charp(s)


    def get_fn(self, nm):
        assert isinstance(nm, unicode)
        s = rffi.str2charp(str(nm))
        sym = dynload.dlsym(self._dyn_lib, s)
        rffi.free_charp(s)
        return sym



sizes = {Integer._type: rffi.sizeof(rffi.LONG)}

native_types = {Integer._type: rffi.LONG}
native_types_p = {Integer._type: rffi.LONGP}

class FFIFn(object.Object):
    _type = object.Type(u"pixie.stdlib.FFIFn")

    def type(self):
        return FFIFn._type

    def __init__(self, cd, f, arg_types, ret_type, exb_size, arg_offset):
        self._cd = cd
        self._f_ptr = f
        self._arg_types = arg_types
        self._ret_type = ret_type
        self._exb_size = exb_size
        self._arg_offset = arg_offset

    def invoke(self, args):
        exb = lltype.malloc(rffi.CCHARP.TO, self._exb_size, flavor="raw")
        offset_p = rffi.ptradd(exb, self._arg_offset)
        for x in range(len(args)):
            pnt = rffi.cast(native_types_p[self._arg_types[x]], offset_p)
            pnt[0] = rffi.cast(native_types[self._arg_types[x]], args[x].int_val())
            offset_p = rffi.ptradd(offset_p, sizes[self._arg_types[x]])

        print "_____________________________\n"
        print args[0].int_val()
        jit_ffi_call(self._cd, self._f_ptr, exb)
        print "_____________________________\n"




def wrap_dyfn(f, args, ret):
    transfer_size = 0
    exchange_result = len(args) * rffi.sizeof(rffi.CCHARP)
    for x in args:
        exchange_result = transfer_size
        transfer_size += sizes[x]

    transfer_size += sizes[ret]

    cd = lltype.malloc(CIF_DESCRIPTION, 1, flavor="raw")
    cd.abi = clibffi.FFI_DEFAULT_ABI
    cd.nargs = len(args)
    cd.rtype = clibffi.cast_type_to_ffitype(native_types[ret])
    atypes = lltype.malloc(clibffi.FFI_TYPE_PP.TO, len(args), flavor="raw")
    for x in range(len(args)):
        atypes[x] = clibffi.cast_type_to_ffitype(native_types[args[x]])


    cd.atypes = atypes
    cd.exchange_size = transfer_size
    cd.exchange_result = len(args) * rffi.sizeof(rffi.CCHARP)
    cd.exchange_result_libffi = len(args) * rffi.sizeof(rffi.CCHARP)
    cd.exchange_args[0] = len(args) * rffi.sizeof(rffi.CCHARP)

    jit_ffi_prep_cif(cd)

    return FFIFn(cd, f, args, ret, transfer_size, len(args) * rffi.sizeof(rffi.CCHARP))


@code.as_var("doit")
def _doit():
    LIBC = ExternalLib(u"/usr/lib/libc.dylib")
    putc = LIBC.get_fn(u"putc")
    ffifn = wrap_dyfn(putc, [Integer._type], Integer._type)

    ffifn.invoke([Integer(42)])
    return Integer(1)