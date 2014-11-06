import py

from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.lltypesystem.lloperation import llop
import rpython.rtyper.tool.rffi_platform as rffi_platform
from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.annlowlevel import llhelper
from rpython.rlib.rgc import pin, unpin
from pixie.vm.code import as_var, extend, NativeFn
from pixie.vm.primitives import nil
import rpython.tool.udir as udir
import os
import shutil
import pixie.vm.libs.ffi as ffi


pkgpath = py.path.local(__file__).dirpath()
srcpath = pkgpath.join("c")

shutil.copyfile(str(srcpath / "uv_ffi.c"), str(udir.udir / "uv_ffi.c"))


compilation_info = ExternalCompilationInfo(
        includes=['uv.h', "ffi.h"],
        libraries=["uv", "ffi"],
        separate_module_files=[udir.udir / "uv_ffi.c"]).merge(ExternalCompilationInfo.from_pkg_config("libffi"))

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)


uv_work = rffi_platform.Struct("uv_work_t",
                               [("data", rffi.VOIDP)])

uv_timer_t = rffi.COpaque("uv_timer_t", compilation_info=compilation_info)

#print rffi.sizeof(uv_timer_t)

uv_timer = lltype.Ptr(uv_timer_t)

uv_timer_cb = lltype.Ptr(lltype.FuncType([uv_timer, rffi.INT], lltype.Void))

uv_callback = lltype.Ptr(lltype.FuncType([rffi.VOIDP, rffi.INT], lltype.Void))

data_container = {}

def as_cb(T, fn):
    return llhelper(T, rffi._make_wrapper_for(T, fn))

def _timer_cb(timer_t, status):
    print status, " status"
    import pixie.vm.stacklet as stacklet
    casted = rffi.cast(rffi.INT, timer_t)
    data = data_container[casted]
    del data_container[casted]
    stacklet.pending_stacklets.push(data)
    print "timeout completed"

def set_timeout(loop, cont, timeout, repeat):
    timer = lltype.malloc(uv_timer_t, flavor="raw", track_allocation="false")
    data_container[rffi.cast(rffi.INT, timer)] = cont
    assert not timer_init(loop, timer)
    print "setting timeout", timeout, repeat
    assert not timer_start(timer, as_cb(uv_timer_cb, _timer_cb), timeout, repeat)



loop_new = llexternal('uv_loop_new', [], rffi.VOIDP)
run = llexternal("uv_run", [rffi.VOIDP, rffi.INT], rffi.SIZE_T)

timer_init = llexternal("uv_timer_init", [rffi.VOIDP, uv_timer], rffi.INT)
timer_start = llexternal("uv_timer_start", [uv_timer, uv_timer_cb, rffi.INT, rffi.UINT], rffi.INT)

ffi_run = llexternal("uv_ffi_run", [rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, uv_callback], rffi.INT)
ffi_make_baton = llexternal("uv_ffi_make_baton", [], rffi.VOIDP)

RUN_DEFAULT = 0
RUN_ONCE = 1
RUN_NO_WAIT = 2

class UVFunction(NativeFn):
    pass


class SleepUVFunction(UVFunction):
    def __init__(self, time):
        self._time = time.int_val()

    def execute_uv(self, loop, k):
        set_timeout(loop, k, self._time, 0)

class RunFFIFunc(UVFunction):
    def __init__(self, fn, args):

        assert isinstance(fn, ffi.FFIFn)
        self._fn = fn
        self._args = args

    def execute_uv(self, loop, k):
        baton = ffi_make_baton()
        data_container[rffi.cast(rffi.INT, baton)] = k
        exb = self._fn.prep_exb(self._args)

        ffi_run(baton, loop, ffi._cd, ffi._f_ptr, exb, as_cb(uv_timer_cb, _timer_cb))

@as_var("run_blocking")
def _run_blocking(fn, arg):
    from pixie.vm.stacklet import execute_uv_func
    execute_uv_func(RunFFIFunc(fn, [arg]))
    return nil

@as_var("sleep")
def _sleep(ms):
    from pixie.vm.stacklet import execute_uv_func
    execute_uv_func(SleepUVFunction(ms))
    return nil