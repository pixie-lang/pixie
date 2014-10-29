import pixie.vm.rt as rt
from pixie.vm.string import String
from pixie.vm.code import as_var, extend
from pixie.vm.object import Object, Type
import pixie.vm.stdlib as proto
from pixie.vm.keyword import keyword
from rpython.rlib.clibffi import get_libc_name
import os
import pixie.vm.rt as rt



@as_var("pixie.string", "starts-with")
def startswith(a, b):
    return rt.wrap(rt.name(a).startswith(rt.name(b)))


@as_var("pixie.string", "ends-with")
def endswith(a, b):
    return rt.wrap(rt.name(a).endswith(rt.name(b)))
