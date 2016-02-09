from pixie.vm.object import Object, Type, safe_invoke
from pixie.vm.primitives import true
import rpython.rlib.rthread as rthread
from pixie.vm.primitives import nil
import rpython.rlib.rgil as rgil
from pixie.vm.code import as_var
import pixie.vm.rt as rt

from rpython.rlib.objectmodel import invoke_around_extcall

class Bootstrapper(object):
    def __init__(self):
        self._is_inited = False
        #_self.init()

    def init(self):
        if not self._is_inited:
            self._is_inited = True
            self._lock = rthread.allocate_lock()
            rgil.gil_allocate()
            invoke_around_extcall(before_external_call, after_external_call)

    def aquire(self, fn):
        self.init()
        self._lock.acquire(True)
        self._fn = fn

    def fn(self):
        return self._fn

    def release(self):
        self._fn = None
        self._lock.release()


    def _cleanup_(self):
        self._lock = None
        self._is_inited = False


def bootstrap():
    rthread.gc_thread_start()
    fn = bootstrapper.fn()
    bootstrapper.release()
    safe_invoke(fn, [])
    rthread.gc_thread_die()

bootstrapper = Bootstrapper()

@as_var("-thread")
def new_thread(fn):
    bootstrapper.aquire(fn)
    ident = rthread.start_new_thread(bootstrap, ())
    return nil

@as_var("-yield-thread")
def yield_thread():
    do_yield_thread()
    return nil

# Locks

class Lock(Object):
    _type = Type(u"pixie.stdlib.Lock")
    def __init__(self, ll_lock):
        self._ll_lock = ll_lock


@as_var("-create-lock")
def _create_lock():
    return Lock(rthread.allocate_lock())

@as_var("-acquire-lock")
def _acquire_lock(self, no_wait):
    assert isinstance(self, Lock)
    return rt.wrap(self._ll_lock.acquire(no_wait == true))

@as_var("-acquire-lock-timed")
def _acquire_lock(self, ms):
    assert isinstance(self, Lock)
    return rt.wrap(self._ll_lock.acquire(ms.int_val()))

@as_var("-release-lock")
def _release_lock(self):
    assert isinstance(self, Lock)
    return rt.wrap(self._ll_lock.release())



## From PYPY


after_thread_switch = lambda: None     # hook for signal.py

# Fragile code below.  We have to preserve the C-level errno manually...

def before_external_call():
    # this function must not raise, in such a way that the exception
    # transformer knows that it cannot raise!
    rgil.gil_release()
before_external_call._gctransformer_hint_cannot_collect_ = True
before_external_call._dont_reach_me_in_del_ = True

def after_external_call():
    rgil.gil_acquire()
    rthread.gc_thread_run()
    after_thread_switch()
after_external_call._gctransformer_hint_cannot_collect_ = True
after_external_call._dont_reach_me_in_del_ = True

# The _gctransformer_hint_cannot_collect_ hack is needed for
# translations in which the *_external_call() functions are not inlined.
# They tell the gctransformer not to save and restore the local GC
# pointers in the shadow stack.  This is necessary because the GIL is
# not held after the call to before_external_call() or before the call
# to after_external_call().

def do_yield_thread():
    # explicitly release the gil, in a way that tries to give more
    # priority to other threads (as opposed to continuing to run in
    # the same thread).
    if rgil.gil_yield_thread():
        rthread.gc_thread_run()
        after_thread_switch()
do_yield_thread._gctransformer_hint_close_stack_ = True
do_yield_thread._dont_reach_me_in_del_ = True
do_yield_thread._dont_inline_ = True

# do_yield_thread() needs a different hint: _gctransformer_hint_close_stack_.
# The *_external_call() functions are themselves called only from the rffi
# module from a helper function that also has this hint.
