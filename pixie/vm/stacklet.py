import rpython.rlib.rstacklet as rstacklet
from pixie.vm.object import Object, Type, affirm
from pixie.vm.code import as_var
import pixie.vm.rt as rt


class GlobalState(object):
    def __init__(self):
        self._is_inited = False
        self._val = None


global_state = GlobalState()


def init():
    if not global_state._is_inited:
        global_state._th = rstacklet.StackletThread(rt.__config__)
        global_state._is_inited = True


class StackletHandle(Object):
    _type = Type(u"StackletHandle")
    def __init__(self, h):
        self._stacklet_handle = h
        self._used = False

    def invoke(self, args):
        affirm(not self._used, u"Can only call a given stacklet handle once.")
        affirm(len(args) == 1, u"Only one arg should be handed to a stacklet handle")
        self._used = True
        global_state._val = args[0]
        new_h = StackletHandle(global_state._th.switch(self._stacklet_handle))
        val = global_state._val
        global_state._val = None
        return rt.vector(new_h, val)

def new_handler(h, _):
    fn = global_state._val
    global_state._val = None
    h = global_state._th.switch(h)
    val = global_state._val
    fn.invoke([StackletHandle(h), val])
    affirm(False, u"TODO: What do we do now?")
    return h



@as_var("new-stacklet")
def new_stacklet(fn):
    global_state._val = fn
    h = global_state._th.new(new_handler)
    return StackletHandle(h)
