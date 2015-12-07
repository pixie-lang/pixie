

from rpython.rlib.entrypoint import entrypoint_highlevel, RPython_StartupCode
from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.rtyper.lltypesystem.lloperation import llop


@entrypoint_highlevel('main', [rffi.CCHARP], c_name='pixie_init')
def pypy_execute_source(ll_progname):
    from target import init_vm
    progname = rffi.charp2str(ll_progname)
    init_vm(progname)
    res = 0
    return rffi.cast(rffi.INT, res)

@entrypoint_highlevel('main', [rffi.CCHARP], c_name='pixie_execute_source')
def pypy_execute_source(ll_source):
    from target import EvalFn, run_with_stacklets
    source = rffi.charp2str(ll_source)
    f = EvalFn(source)
    run_with_stacklets.invoke([f])
    res = 0
    return rffi.cast(rffi.INT, res)
