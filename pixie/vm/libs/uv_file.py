from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.lltypesystem.lloperation import llop
import rpython.rtyper.tool.rffi_platform as rffi_platform
import pixie.vm.rt as rt
from pixie.vm.code import as_var
from pixie.vm.libs.uv import UVFunction, llexternal
from pixie.vm.stacklet import execute_uv_func, pending_stacklets
from pixie.vm.object import Object, Type
from pixie.vm.primitives import nil

def __module_init__():
    def define_int_const(ns, nm, header):
        as_var(ns, nm)(rt.wrap(rffi_platform.getconstantinteger(nm, "#include <" + header + ">")))

    fcntl_consts = "O_RDONLY O_WRONLY O_RDWR O_CLOEXEC O_CREAT O_DIRECTORY O_EXCL O_NOCTTY O_NOFOLLOW O_TRUNC"
    for x in fcntl_consts.split(" "):
        define_int_const("pixie.io", x, "fcntl.h")


uv_fs_t = rffi_platform.getstruct("uv_fs_t", "#include<uv.h>", [("result", rffi.INT)])
uv_fs_t_p = lltype.Ptr(uv_fs_t)

uv_fs_cb = rffi.CCallback([uv_fs_t_p], lltype.Void)
uv_fs_open = llexternal("uv_fs_open", [rffi.VOIDP, uv_fs_t_p, rffi.CCHARP, rffi.INT, rffi.INT, uv_fs_cb], rffi.VOIDP)


# File Open
fs_open_data = {}

class FileHandle(Object):
    _type = Type(u"pixie.io.FileHandle")
    def __init__(self, handle):
        self._fs_handle = handle

    def type(self):
        return FileHandle._type

def fs_cb(req):
    (k, charp) = fs_open_data[rffi.cast(rffi.SIZE_T, req)]
    result = req.c_result
    lltype.free(charp, flavor="raw")
    if result == -1:
        pending_stacklets.push((k, nil))
    else:
        pending_stacklets.push((k, FileHandle(result)))
    lltype.free(req, flavor="raw")


class FSOpen(UVFunction):
    def __init__(self, path, flags, mode):
        self._path = rt.name(path)
        self._flags = flags.int_val()
        self._mode = mode.int_val()

    def execute_uv(self, loop, k):
        req = lltype.malloc(uv_fs_t, flavor="raw")
        charp = rffi.str2charp(str(self._path))
        fs_open_data[rffi.cast(rffi.SIZE_T, req)] = (k, charp)
        uv_fs_open(loop, req, charp, self._flags, self._mode, fs_cb)

@as_var("pixie.io", "open")
def _open(name, flags, mode):
    return execute_uv_func(FSOpen(name, flags, mode))

## End File Open