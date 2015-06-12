from pixie.vm2.object import Type, Object, affirm
from pixie.vm2.code import as_var
import rpython.rlib.jit as jit
from pixie.vm2.primitives import nil, true, false
import pixie.vm2.rt as rt


class SwitchTable(Object):
    _type = Type(u"pixie.stdlib.SwitchTable")
    _immutable_fields_ = ["_switch_table"]

    def type(self):
        return SwitchTable._type

    def __init__(self, d):
        self._switch_table = d


    @jit.elidable_promote()
    def lookup(self, itm):
        return self._switch_table.get(itm, nil)

    def invoke_k(self, args, stack):
        affirm(len(args) == 1, u"SwitchTables should be called with one arg")
        return self.lookup(args[0]), stack



@as_var("switch-table")
def swith_table__args(args):
    idx = 0
    acc = {}
    while idx < len(args):
        affirm(idx + 1 < len(args), u"Even number of args should be passed to switch-table")
        acc[args[idx]] = args[idx + 1]
        idx += 2

    return SwitchTable(acc)

class ContainsTable(Object):
    _type = Type(u"pixie.stdlib.ContainsTable")
    _immutable_fields_ = ["_switch_table"]

    def type(self):
        return ContainsTable._type

    def __init__(self, dict):
        self._switch_table = dict


    @jit.elidable_promote()
    def lookup(self, itm):
        return rt.wrap(itm in self._switch_table)

    def invoke_k(self, args, stack):
        affirm(len(args) == 1, u"ContainsTables should be called with one arg")
        return self.lookup(args[0]), stack

@as_var("contains-table")
def contains_table__args(args):
    idx = 0
    acc = {}
    while idx < len(args):
        acc[args[idx]] = args[idx]
        idx += 1

    return ContainsTable(acc)