py_object = object
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
from pixie.vm.util import unicode_to_utf8
from rpython.rlib import clibffi
from rpython.rlib.jit_libffi import jit_ffi_prep_cif, jit_ffi_call, CIF_DESCRIPTION
import rpython.rlib.jit as jit
from rpython.rlib.rarithmetic import intmask, r_uint


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
            cd.rtype = self._ret_type.ffi_type()

            atypes = lltype.malloc(clibffi.FFI_TYPE_PP.TO, nargs, flavor="raw")
            arg0_offset = exchange_buffer_size
            for idx in range(nargs):
                cd.exchange_args[idx] = exchange_buffer_size
                tp = self._arg_types[idx]
                native_size = tp.ffi_size()
                atypes[idx] = tp.ffi_type()
                exchange_buffer_size += native_size

            ret_offset = exchange_buffer_size
            exchange_buffer_size += self._ret_type.ffi_size()



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
        tokens = [None] * len(args)

        for x in range(len(self._arg_types)):
            tokens[x] = self._arg_types[x].ffi_set_value(offset_p, args[x])
            offset_p = rffi.ptradd(offset_p, self._arg_types[x].ffi_size())

        return exb, tokens

    def get_ret_val_from_buffer(self, exb):
        offset_p = rffi.ptradd(exb, self._cd.exchange_result_libffi)
        ret_val = self._ret_type.ffi_get_value(offset_p)
        return ret_val

    @jit.unroll_safe
    def _invoke(self, args):

        exb, tokens = self.prep_exb(args)
        jit_ffi_call(self._cd, self._f_ptr, exb)
        ret_val = self.get_ret_val_from_buffer(exb)

        for x in range(len(args)):
            t = tokens[x]
            if t is not None:
                t.finalize_token()

        lltype.free(exb, flavor="raw")
        return ret_val

    def invoke(self, args):
        self = jit.promote(self)
        return self._invoke(args)

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
        assert isinstance(idx, int)
        return self._buffer[idx]

    def capacity(self):
        return self._size


@extend(proto._nth, Buffer)
def _nth(self, idx):
    return rt.wrap(ord(self.nth_char(idx.int_val())))

@extend(proto._count, Buffer)
def _count(self):
    return rt.wrap(intmask(self.count()))

@as_var("buffer")
def buffer(size):
    return Buffer(size.int_val())

@as_var("buffer-capacity")
def buffer_capacity(buffer):
    return rt.wrap(intmask(buffer.capacity()))

@as_var("set-buffer-count!")
def set_buffer_size(self, size):
    self.set_used_size(size.int_val())
    return self



class CStructType(object.Type):
    def __init__(self, name, size, desc):
        object.Type.__init__(self, name)
        self._desc = desc
        self._size = size
        #offsets is a dict of {nm, (type, offset)}

    def get_offset(self, nm):
        (tp, offset) = self._desc.get(nm, (None, 0))

        assert tp is not None

        return offset

    def get_type(self, nm):
        (tp, offset) = self._desc.get(nm, (None, 0))

        assert tp is not None

        return tp

    def get_desc(self, nm):
        return self._desc[nm]

class Token(py_object):
    """ Tokens are returned by ffi_set_value and are called when ffi is ready to clean up resources
    """
    def finalize_token(self):
        pass


class CType(object.Type):
    def __init__(self, name):
        object.Type.__init__(self, name)


class CInt(CType):
    def __init__(self):
        CType.__init__(self, u"pixie.stdlib.CInt")

    def ffi_get_value(self, ptr):
        casted = rffi.cast(rffi.INTP, ptr)
        return Integer(rffi.cast(rffi.LONG, casted[0]))

    def ffi_set_value(self, ptr, val):
        casted = rffi.cast(rffi.INTP, ptr)
        casted[0] = rffi.cast(rffi.INT, val.int_val())

    def ffi_size(self):
        return rffi.sizeof(rffi.INT)

    def ffi_type(self):
        return clibffi.cast_type_to_ffitype(rffi.INT)
CInt()

class CDouble(CType):
    def __init__(self):
        CType.__init__(self, u"pixie.stdlib.CDouble")

    def ffi_get_value(self, ptr):
        casted = rffi.cast(rffi.DOUBLEP, ptr)
        return Float(casted[0])

    def ffi_set_value(self, ptr, val):
        casted = rffi.cast(rffi.DOUBLEP, ptr)
        casted[0] = rffi.cast(rffi.DOUBLE, val.float_val())

    def ffi_size(self):
        return rffi.sizeof(rffi.DOUBLE)

    def ffi_type(self):
        return clibffi.cast_type_to_ffitype(rffi.DOUBLE)
CDouble()

class CCharP(CType):
    def __init__(self):
        CType.__init__(self, u"pixie.stdlib.CCharP")

    def ffi_get_value(self, ptr):
        casted = rffi.cast(rffi.CCHARPP, ptr)
        if casted[0] == lltype.nullptr(rffi.CCHARP.TO):
            return nil
        else:
            return String(unicode(rffi.charp2str(casted[0])))

    def ffi_set_value(self, ptr, val):
        pnt = rffi.cast(rffi.CCHARPP, ptr)
        utf8 = unicode_to_utf8(rt.name(val))
        data, pinned, raw = rffi.get_nonmovingbuffer(utf8)
        pnt[0] = data
        return CCharPToken(utf8, data, pinned, raw)

    def ffi_size(self):
        return rffi.sizeof(rffi.CCHARP)

    def ffi_type(self):
        return clibffi.ffi_type_pointer
CCharP()

class CCharPToken(Token):
    def __init__(self, s, data, pinned, raw):
        self._s = s
        self._data = data
        self._pinned = pinned
        self._raw = raw

    def finalize_token(self):
        rffi.free_nonmovingbuffer(self._s, self._data, self._pinned, self._raw)



class CVoidP(CType):
    def __init__(self):
        CType.__init__(self, u"pixie.stdlib.CVoidP")

    def ffi_get_value(self, ptr):
        casted = rffi.cast(rffi.VOIDPP, ptr)
        if casted[0] == lltype.nullptr(rffi.VOIDP.TO):
            return nil
        else:
            return VoidP(casted[0])

    def ffi_set_value(self, ptr, val):
        pnt = rffi.cast(rffi.VOIDPP, ptr)
        if isinstance(val, Buffer):
            pnt[0] = val.buffer()
        elif isinstance(val, VoidP):
            pnt[0] = val.raw_data()
        else:
            print val
            affirm(False, u"Cannot encode this type")

    def ffi_size(self):
        return rffi.sizeof(rffi.VOIDP)

    def ffi_type(self):
        return clibffi.ffi_type_pointer
cvoidp = CVoidP()

class VoidP(object.Object):
    def type(self):
        return cvoidp

    def __init__(self, raw_data):
        self._raw_data = raw_data

    def raw_data(self):
        return self._raw_data



class CStruct(object.Object):
    def __init__(self, tp, buffer):
        self._type = tp
        self._buffer = buffer

    def type(self):
        return self._type

    def get_item(self, nm):
        (tp, offset) = self._type.get_desc(nm)
        ptr = rffi.ptradd(self._buffer, offset)
        return tp.ffi_load_from(ptr)
