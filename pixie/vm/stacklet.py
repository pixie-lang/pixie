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

class StackletThreadBox(py_object):
    def __init__(self):
        self._th = None


th = StackletThreadBox()

def init():
    if th._th is None:
        th._th = rstacklet.StackletThread(rt.__config__)


class Box(object.Object):
    _type = object.Type("Box")
    def __init__(self):
        self._val = None

    def type(self):
        return Box._type

box = Box()
box._val = None
fn_box = Box()
arg_box = Box()

class WrappedHandler(BaseCode):
    _type = object.Type("Stacklet")
    def __init__(self, h, box):
        self._h = h
        self._box = box

    def switch_to(self, val):
        self._box._val = val
        self._h = th._th.switch(self._h)
        return self._box._val

    def _invoke(self, args):
        assert len(args) == 1
        return self.switch_to(args[0])

    def type(self):
        return WrappedHandler._type


def new_stacklet(f, val):
    global box, fn_box, arg_box
    init()
    box._val = Box()
    self_box = box._val
    fn_box._val = f
    arg_box._val = val
    def default_handler(h, o):
        global box, fn_box, arg_box
        handler = WrappedHandler(h, box._val)
        box._val = None
        handler._h = th._th.switch(handler._h)
        retval = fn_box._val.invoke([handler, arg_box._val])

        return handler._h

    h = th._th.new(default_handler)
    return WrappedHandler(h, self_box)

@as_var("create-stacklet")
def _new_stacklet(f):
    return new_stacklet(f, nil)