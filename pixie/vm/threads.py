from pixie.vm.object import Object, Type, safe_invoke
from pixie.vm.primitives import true
import rpython.rlib.rthread as rthread
from pixie.vm.primitives import nil
import rpython.rlib.rgil as rgil
from pixie.vm.code import as_var
import pixie.vm.rt as rt

class Bootstrapper(object):
    def __init__(self):
        self._is_inited = False
        #_self.init()

    def init(self):
        if not self._is_inited:
            self._lock = rthread.allocate_lock()
            self._is_inited = True
            rgil.allocate()

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
    rgil.yield_thread()
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


# The *_external_call() functions are themselves called only from the rffi
# module from a helper function that also has this hint.
