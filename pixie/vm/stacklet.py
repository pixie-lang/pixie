py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.code import BaseCode
from pixie.vm.numbers import Integer
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint, intmask, widen
import rpython.rlib.jit as jit
import pixie.vm.rt as rt
import pixie.vm.libs.uv as uv
import pixie.vm.libs.ring_buffer as ring_buffer
import rpython.rlib.rstacklet as rstacklet
from rpython.rtyper.lltypesystem import lltype, rffi

OP_NEW = 0x01
OP_SWITCH = 0x02
OP_CONTINUE = 0x03
OP_EXIT = 0x04
OP_YIELD = 0x05
OP_NEXT_PENDING = 0x06
OP_NEW_THREAD = 0x07
OP_EXECUTE_UV = 0x08

class GlobalState(py_object):
    def __init__(self):
        self.reset()

    def reset(self):
        self._th = None
        self._val = None
        self._ex = None
        self._to = None
        self._op = 0x00
        self._fn = None
        self._init_fn = None
        self._from = None

    def switch_back(self):
        tmp = self._from
        self._from = self._to
        self._to = tmp


global_state = GlobalState()

def init():
    if global_state._th is None:
        global_state._th = rstacklet.StackletThread(rt.__config__)
        global_state._h = global_state._th.get_null_handle()

def shutdown():
    global_state._h = global_state._th.get_null_handle()

    global_state.reset()

class FinishedToken(BaseCode):
    _type = object.Type(u"pixie.stdlib.FinishedToken")
    def __init__(self):
        pass

    def type(self):
        return FinishedToken._type

finished_token = FinishedToken()

class WrappedHandler(BaseCode):
    _type = object.Type(u"Stacklet")
    def __init__(self, h):
        self._h = h
        self._is_finished = False
        self._val = nil


    def type(self):
        return WrappedHandler._type

    def is_finished(self):
        return self._is_finished

    def invoke(self, args):
        affirm(len(args) == 1, u"Only one arg to continuation allowed")
        affirm(not self._is_finished, u"Execution of this stacklet has completed")

        global_state._from = global_state._to
        global_state._to = self
        global_state._op = OP_SWITCH
        global_state._val = args[0]
        global_state._h = global_state._th.switch(global_state._h)

        if global_state._val is finished_token:
            global_state._from._is_finished = True

        global_state._from._val = global_state._val

        return global_state._val


def new_stacklet(f):
    global_state._op = OP_NEW
    global_state._val = f
    global_state.switch_back()
    global_state._h = global_state._th.switch(global_state._h)
    val = global_state._val
    return val

def new_thread(f):
    global_state._op = OP_NEW_THREAD
    global_state._val = f
    global_state._h = global_state._th.switch(global_state._h)

def enqueue_stacklet(k):
    pending_stacklets.push(k)

def yield_stacklet():
    global_state._op = OP_YIELD
    global_state._val = nil
    global_state._h = global_state._th.switch(global_state._h)

def execute_uv_func(func):
    assert isinstance(func, uv.UVFunction)
    global_state._op = OP_EXECUTE_UV
    global_state._val = func
    global_state._h = global_state._th.switch(global_state._h)


def new_handler(h, o):
    global_state._h = h

    affirm(global_state._val is not None, u"Internal Stacklet Error")
    f = global_state._val
    global_state._val = None


    global_state._op = OP_SWITCH
    global_state.switch_back()
    global_state._h = global_state._th.switch(h)


    #try:
    f.invoke([global_state._from])
    global_state._from.invoke([finished_token])

    return global_state._h

def new_thread_handler(h, o):
    global_state._h = h

    affirm(global_state._val is not None, u"Internal Stacklet Error")
    f = global_state._val
    global_state._val = None

    global_state._h = global_state._th.switch(global_state._h)


    #try:
    f.invoke([global_state._from])

    global_state._op = OP_NEXT_PENDING
    global_state._h = global_state._th.switch(global_state._h)

    return global_state._h



def init_handler(h, o):
    global_state._h = h

    affirm(global_state._init_fn is not None, u"Internal Stacklet error")
    f = global_state._init_fn
    global_state._init_fn = None

    #try:
    f.invoke([])
    #except Exception as ex:
    #    print "Uncaught Exception" + str(ex)

    global_state._op = OP_EXIT
    return global_state._h

pending_stacklets = ring_buffer.RingBuffer(r_uint(32))


def with_stacklets(f):
    loop = uv.loop_new()

    init()
    global_state._init_fn = f

    main_h = global_state._th.new(init_handler)
    global_state._from = WrappedHandler(main_h)

    pending_stacklets.push(1)
    assert pending_stacklets.pop() == 1
    pending_stacklets.push(2)
    assert pending_stacklets.pop() == 2

    while True:
        print global_state._op
        if global_state._op == OP_NEW:
            wh = WrappedHandler(global_state._th.get_null_handle())
            global_state._to = wh
            wh._h = global_state._th.new(new_handler)
            global_state._val = wh
            continue

        elif global_state._op == OP_NEW_THREAD:
            wh = WrappedHandler(global_state._th.get_null_handle())
            global_state._to = wh
            wh._h = global_state._th.new(new_thread_handler)
            pending_stacklets.push(wh)
            pending_stacklets.push(global_state._from)
            global_state._op = OP_NEXT_PENDING
            continue

        elif global_state._op == OP_SWITCH:
            to = global_state._to
            to._h = global_state._th.switch(global_state._to._h)
            continue

        elif global_state._op == OP_EXIT:
            shutdown()
            return global_state._val

        elif global_state._op == OP_YIELD:
            assert global_state._from
            pending_stacklets.push(global_state._from)
            global_state._op = OP_NEXT_PENDING
            continue

        elif global_state._op == OP_EXECUTE_UV:
            assert global_state._from
            k = global_state._from
            f = global_state._val
            f.execute_uv(loop, k)
            global_state._op = OP_NEXT_PENDING
            continue

        elif global_state._op == OP_NEXT_PENDING:
            print "running with", pending_stacklets.pending()
            while True:
                if pending_stacklets.pending() == 0:
                    uv.run(loop, uv.RUN_DEFAULT)
                    continue
                else:
                    uv.run(loop, uv.RUN_DEFAULT | uv.RUN_NO_WAIT)
                    break
            f = pending_stacklets.pop()
            global_state._from = f
            f._h = global_state._th.switch(f._h)
            continue

        else:
            break

    shutdown()
    return None

@as_var("create-stacklet")
def _new_stacklet(f):
    stacklet = new_stacklet(f)
    stacklet.invoke([nil])   # prime it
    return stacklet

@as_var("create-thread")
def _new_stacklet(f):
    stacklet = new_thread(f)

    return nil

@as_var("yield-stacklet")
def _stacklet_yield():
    yield_stacklet()
    return nil

@extend(proto._at_end_QMARK_, WrappedHandler)
def _at_end(self):
    assert isinstance(self, WrappedHandler)
    return rt.wrap(self.is_finished())

@extend(proto._move_next_BANG_, WrappedHandler)
def _move_next(self):
    assert isinstance(self, WrappedHandler)
    self.invoke([nil])
    return self

@extend(proto._current, WrappedHandler)
def _current(self):
    assert isinstance(self, WrappedHandler)
    return self._val
