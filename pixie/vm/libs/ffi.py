import rpython.rlib.rdynload as dynload
import pixie.vm.object as object
import pixie.vm.code as code
import pixie.vm.rt as rt
from rpython.rtyper.lltypesystem import rffi, lltype

class ExternalLib(object.Object):
    _type = object.Type("pixie.stdlib.ExternalLib")

    def __init__(self, nm):
        self._dyn_lib = dynload.dlopen(nm)

import ctypes
from rpython.rlib.clibffi import get_libc_name
print get_libc_name()

s = rffi.str2charp("/usr/lib/libc.dylib")
lib = dynload.dlopen(s)
rffi.free_charp(s)

#LIBC = ExternalLib(rffi.str2charp("/usr/lib/libc.dynlib"))

