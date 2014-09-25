from loki_vm.vm.code import as_var
import loki_vm.vm.object as object
from loki_vm.vm.code import BaseCode
from loki_vm.vm.primitives import true, false, nil


@as_var("type")
def type(o):
    return o.type()


@as_var("set-effect!")
def set_effect(c, v):
    assert isinstance(c, BaseCode)
    c.set_is_effect(v)
    return c
