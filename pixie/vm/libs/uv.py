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
from pixie.vm.object import affirm
import os
import shutil
import pixie.vm.libs.ffi as ffi
import rpython.rlib.rgc as rgc


pkgpath = py.path.local(__file__).dirpath()
srcpath = pkgpath.join("c")

shutil.copyfile(str(srcpath / "uv_ffi.c"), str(udir.udir / "uv_ffi.c"))
shutil.copyfile(str(srcpath / "uv_ffi.h"), str(udir.udir / "uv_ffi.h"))


compilation_info = ExternalCompilationInfo(
        includes=['uv.h', "ffi.h", "uv_ffi.h"],
        include_dirs=[srcpath],
        libraries=["uv", "ffi"],
        separate_module_files=[udir.udir / "uv_ffi.c"]).merge(ExternalCompilationInfo.from_pkg_config("libffi"))

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)


uv_work = rffi_platform.Struct("uv_work_t",
                               [("data", rffi.VOIDP)])

uv_timer_t = rffi.COpaque("uv_timer_t", compilation_info=compilation_info)
uv_baton_t = rffi.COpaque("work_baton_t", compilation_info=compilation_info)


uv_timer = lltype.Ptr(uv_timer_t)

uv_timer_cb = lltype.Ptr(lltype.FuncType([uv_timer, rffi.INT], lltype.Void))

uv_callback_t = rffi.CCallback([rffi.VOIDP, rffi.INT], lltype.Void)

data_container = {}

def as_cb(T):
    def _inner(fn):
        return llhelper(T, fn)
    return _inner

def _timer_cb(timer_t, status):
    import pixie.vm.stacklet as stacklet
    casted = rffi.cast(rffi.INT, timer_t)
    data = data_container[casted]
    del data_container[casted]
    stacklet.pending_stacklets.push((data, nil))

def set_timeout(loop, cont, timeout, repeat):
    timer = lltype.malloc(uv_timer_t, flavor="raw", track_allocation="false")
    data_container[rffi.cast(rffi.INT, timer)] = cont
    assert not timer_init(loop, timer)
    assert not timer_start(timer, _timer_cb, timeout, repeat)



loop_new = llexternal('uv_loop_new', [], rffi.VOIDP)
run = llexternal("uv_run", [rffi.VOIDP, rffi.INT], rffi.SIZE_T)

timer_init = llexternal("uv_timer_init", [rffi.VOIDP, uv_timer], rffi.INT)
timer_start = llexternal("uv_timer_start", [uv_timer, uv_timer_cb, rffi.ULONGLONG, rffi.ULONGLONG], rffi.INT)

ffi_run = llexternal("uv_ffi_run", [rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, rffi.VOIDP, uv_callback_t], rffi.SIZE_T)
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


work_data_container = {}

def _work_cb(baton, status):
    import pixie.vm.stacklet as stacklet
    casted = rffi.cast(rffi.INT, baton)
    (k, exb, fn) = work_data_container[casted]
    del work_data_container[casted]
    retval = fn.get_ret_val_from_buffer(exb)

    stacklet.pending_stacklets.push((k, retval))
    lltype.free(exb, flavor="raw")
    lltype.free(baton, flavor="raw")

class RunFFIFunc(UVFunction):
    def __init__(self, fn, args):
        affirm(isinstance(fn, ffi.FFIFn), u"Can only use blocking-call against a ffi function")
        self._fn = fn
        self._args = args

    def execute_uv(self, loop, k):
        baton = lltype.malloc(uv_baton_t, flavor="raw")
        rgc.pin(baton)
        exb = self._fn.prep_exb(self._args)

        buffer_array = rffi.cast(rffi.VOIDPP, exb)
        work_data_container[rffi.cast(rffi.INT, baton)] = (k, exb, self._fn)
        cif = self._fn._cd
        for i in range(cif.nargs):
            data = rffi.ptradd(exb, cif.exchange_args[i])
            buffer_array[i] = data
        resultdata = rffi.ptradd(exb,
                                 cif.exchange_result_libffi)

        ffi_run(baton,
                loop,
                rffi.cast(rffi.VOIDP, cif),
                rffi.cast(rffi.VOIDP, self._fn._f_ptr),
                rffi.cast(rffi.VOIDP, exb),
                rffi.cast(rffi.VOIDP, resultdata),
                _work_cb)

@as_var("blocking-call")
def _run_blocking__args(args):
    affirm(len(args) > 0, u"At least one arg must be supplied to blocking-call")
    fn = args[0]
    argc = len(args) - 1
    new_args = [None] * argc
    for x in range(argc):
        new_args[x] = args[x + 1]

    from pixie.vm.stacklet import execute_uv_func
    return execute_uv_func(RunFFIFunc(fn, new_args))

@as_var("sleep")
def _sleep(ms):
    from pixie.vm.stacklet import execute_uv_func
    execute_uv_func(SleepUVFunction(ms))
    return nil