import py

from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.lltypesystem.lloperation import llop
import rpython.rtyper.tool.rffi_platform as rffi_platform
from rpython.translator import cdir
from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.annlowlevel import llhelper
from rpython.rlib.rgc import pin, unpin
from pixie.vm.code import as_var, extend, NativeFn
from pixie.vm.primitives import nil


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
timer_start = llexternal("uv_timer_start", [uv_timer, uv_timer_cb, rffi.UINT, rffi.UINT], rffi.INT)



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

@as_var("sleep")
def _sleep(ms):
    from pixie.vm.stacklet import execute_uv_func
    execute_uv_func(SleepUVFunction(ms))
    return nil