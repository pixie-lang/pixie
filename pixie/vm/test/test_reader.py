from pixie.vm.reader import read, StringReader
from pixie.vm.object import Object
from pixie.vm.cons import Cons
from pixie.vm.numbers import Integer
from pixie.vm.symbol import symbol, Symbol
from pixie.vm.persistent_vector import PersistentVector
import pixie.vm.rt as rt
import unittest


data = {"(1 2)": (1, 2,),
        "(foo)": (symbol("foo"),),
        "foo": symbol("foo"),
        "1": 1,
        "((42))": ((42,),),
        "(platform+ 1 2)": (symbol("platform+"), 1, 2),
        "[42 43 44]": [42, 43, 44]}

class TestReader(unittest.TestCase):
    def _compare(self, frm, to):
        if isinstance(to, tuple):
            assert isinstance(frm, Cons)

            for x in to:
                self._compare(frm.first(), x)
                frm = frm.next()
        elif isinstance(to, int):
            assert isinstance(frm, Integer)
            assert frm._int_val == to

        elif isinstance(to, Symbol):
            assert isinstance(frm, Symbol)
            assert frm._str == to._str

        elif isinstance(to, list):
            assert isinstance(frm, PersistentVector)

            for x in range(len(to)):
                self._compare(rt.nth(frm, Integer(x)), to[x])

        else:
            raise Exception("Don't know how to handle " + str(type(to)))

    def test_forms(self):
        for s in data:
            tst = data[s]
            result = read(StringReader(s), True)
            assert isinstance(result, Object)

            self._compare(result, tst)


