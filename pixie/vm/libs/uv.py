import py

from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.lltypesystem.lloperation import llop
import rpython.rtyper.tool.rffi_platform as rffi_platform
from rpython.translator import cdir
from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.annlowlevel import llhelper

srcdir = py.path.local(cdir) / 'src'
compilation_info = ExternalCompilationInfo(
        includes=['uv.h'],
        libraries=["uv"])

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)


uv_work = rffi_platform.Struct("uv_work_t",
                               [("data", rffi.VOIDP)])

uv_timer_t = rffi.COpaque("uv_timer_t", compilation_info=compilation_info)

#print rffi.sizeof(uv_timer_t)

uv_timer = lltype.Ptr(uv_timer_t)

uv_timer_cb = lltype.Ptr(lltype.FuncType([uv_timer, rffi.INT], lltype.Void))

def as_cb(T, fn):
    return llhelper(T, rffi._make_wrapper_for(T, fn))

def _timer_cb(timer_t, status):
    pass
    #lltype.free(timer_t)
    print "foo!"

def queue_something(loop):
    print "starting"
    timer = lltype.malloc(uv_timer_t, flavor="raw", track_allocation="false")
    assert not timer_init(loop, timer)
    assert not timer_start(timer, as_cb(uv_timer_cb, _timer_cb), 10000, 0)
    print "Started"


loop_new = llexternal('uv_loop_new', [], rffi.VOIDP)
run = llexternal("uv_run", [rffi.VOIDP, rffi.INT], rffi.INT)

timer_init = llexternal("uv_timer_init", [rffi.VOIDP, uv_timer], rffi.INT)

timer_start = llexternal("uv_timer_start", [uv_timer, uv_timer_cb, rffi.INT, rffi.INT], rffi.INT)



RUN_DEFAULT = 0
RUN_ONCE = 1
RUN_NO_WAIT = 2