py_object = object
import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from pixie.vm.code import BaseCode
from pixie.vm.numbers import Integer
import pixie.vm.protocols as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint as r_uint32, intmask, widen
import rpython.rlib.jit as jit
import pixie.vm.rt as rt
import rpython.rlib.rstacklet as rstacklet

th = rstacklet.StackletThread(None)

class Box(py_object):
    def __init__(self):
        self._val = None

box = Box()

class WrappedHandler(BaseCode):
    _type = object.Type("Stacklet")
    def __init__(self, h, box):
        self._h = h
        self._box = box

    def switch_to(self, val):
        self._box._val = val
        self._h = th.switch(self._h)
        return self._box._val

    def _invoke(self, args):
        assert len(args) == 1
        return self.switch_to(args[0])



def new_stacklet(f, val):
    global box
    box = Box()
    self_box = box
    def default_handler(h, o):
        global box
        handler = WrappedHandler(h, box)
        box = None
        handler._h = th.switch(handler._h)
        retval = f.invoke([handler, val])
        return handler._h

    h = th.new(default_handler)
    return WrappedHandler(h, self_box)