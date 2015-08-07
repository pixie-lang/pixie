

from rpython.rlib.entrypoint import entrypoint, RPython_StartupCode
from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.rtyper.lltypesystem.lloperation import llop


@entrypoint('main', [rffi.CCHARP], c_name='pixie_init')
def pypy_execute_source(ll_progname):
    from target import init_vm
    after = rffi.aroundstate.after
    if after: after()
    progname = rffi.charp2str(ll_progname)
    init_vm(progname)
    res = 0
    before = rffi.aroundstate.before
    if before: before()
    return rffi.cast(rffi.INT, res)

@entrypoint('main', [rffi.CCHARP], c_name='pixie_execute_source')
def pypy_execute_source(ll_source):
    from target import EvalFn, run_with_stacklets
    after = rffi.aroundstate.after
    if after: after()
    source = rffi.charp2str(ll_source)
    f = EvalFn(source)
    run_with_stacklets.invoke([f])
    res = 0
    before = rffi.aroundstate.before
    if before: before()
    return rffi.cast(rffi.INT, res)