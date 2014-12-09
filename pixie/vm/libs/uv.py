from pixie.vm.object import Object, Type
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




compilation_info = ExternalCompilationInfo(
        includes=['uv.h'],
        include_dirs=["/usr/local/include"],
        library_dirs=["/usr/local/lib"],
        libraries=["uv"])

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)


uv_work = rffi_platform.Struct("uv_work_t",
                               [("data", rffi.VOIDP)])

uv_timer_t = rffi.COpaque("uv_timer_t", compilation_info=compilation_info)
uv_baton_t = rffi.COpaque("work_baton_t", compilation_info=compilation_info)


uv_timer = lltype.Ptr(uv_timer_t)

uv_timer_cb = lltype.Ptr(lltype.FuncType([uv_timer, rffi.INT], lltype.Void))

uv_callback_t = rffi.CCallback([rffi.VOIDP, rffi.INT], lltype.Void)


uv_loop_new = llexternal('uv_loop_new', [], rffi.VOIDP)
uv_run = llexternal("uv_run", [rffi.VOIDP, rffi.INT], rffi.SIZE_T)

timer_init = llexternal("uv_timer_init", [rffi.VOIDP, uv_timer], rffi.INT)
timer_start = llexternal("uv_timer_start", [uv_timer, uv_timer_cb, rffi.ULONGLONG, rffi.ULONGLONG], rffi.INT)


RUN_DEFAULT = 0
RUN_ONCE = 1
RUN_NO_WAIT = 2

class UVLoop(Object):
    _type = Type(u"pixie.uv.UVLoop")

    def type(self):
        return UVLoop._type

    def __init__(self, loop):
        self._loop = loop

    def loop(self):
        return self._loop

@as_var("pixie.uv", "new-loop")
def new_loop():
    return UVLoop(uv_loop_new())

@as_var("pixie.uv", "run-loop")
def run_loop(loop):
    affirm(isinstance(loop, UVLoop), u"First argument must be a UVLoop")
    uv_run(loop.loop(), RUN_DEFAULT)
    return loop

def _timer_cb(timer_t, status):
    print "timer done!", timer_t, status
    id = rffi.cast(rffi.INT, timer_t)
    data = data_store[id]
    del data_store[id]
    data.invoke([])


data_store = {}

@as_var("pixie.uv", "timeout")
def timeout(loop, ms, fn):
    affirm(isinstance(loop, UVLoop), u"First argument must be a UVLoop")
    timeout = ms.int_val()
    timer = lltype.malloc(uv_timer_t, flavor="raw")
    data_store[rffi.cast(rffi.INT, timer)] = fn
    timer_init(loop.loop(), timer)
    timer_start(timer, _timer_cb, timeout, 0)
    return loop


# (do (def loop (pixie.uv/new-loop)) (pixie.uv/timeout loop 2000 (fn [] (println "inside"))) (pixie.uv/run-loop loop))