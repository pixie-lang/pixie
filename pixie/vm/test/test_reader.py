from pixie.vm.effects.effects import *
from pixie.vm.reader import StringReader, read_Ef
from pixie.vm.effects.environment import *
from pixie.vm.code import wrap_fn
from pixie.vm.persistent_list import PersistentList
from pixie.vm.numbers import Integer
from pixie.vm.symbol import Symbol, symbol
import unittest

data = {u"(1 2)": (1, 2,),
        u"(foo)": (symbol(u"foo"),),
        u"foo": symbol(u"foo"),
        u"1": 1,
        u"2": 2,
        u"((42))": ((42,),),
        u"(platform+ 1 2)": (symbol(u"platform+"), 1, 2),
        #u"[42 43 44]": [42, 43, 44],
        u"(1 2 ; 7 8 9\n3)": (1, 2, 3,),
        u"(1 2 ; 7 8 9\r\n3)": (1, 2, 3,)
}


class TestRead(unittest.TestCase):
    

    
    def test_basic_reader(self):

        @wrap_fn()
        def doit():
            rdr = StringReader(u"(1 2)")
            return read_Ef(rdr, True)

        result = run_with_state(doit, default_env)
        self.assertIsInstance(result, Answer)
        _compare(result.val(), (1, 2))

        pass
    
    
    def test_forms(self):

        @wrap_fn()
        def doit():
            idx = 0
            dat = list(data.iteritems())
            while idx < len(dat):
                s, tst = dat[idx]
                print tst
                rdr = StringReader(s)
                result = read_Ef(rdr, True)

                _compare(result, tst)

                idx += 1

        result = run_with_state(doit, default_env)
        self.assertIsInstance(result, Answer)
   


# class TestReader(unittest.TestCase):
#     def _compare(self, frm, to):
#         if isinstance(to, tuple):
#             assert isinstance(frm, Cons)
#
#             for x in to:
#                 self._compare(frm.first(), x)
#                 frm = frm.next()
#         elif isinstance(to, int):
#             assert isinstance(frm, Integer)
#             assert frm._int_val == to
#
#         elif isinstance(to, Symbol):
#             assert isinstance(frm, Symbol)
#             assert frm._str == to._str
#
#         elif isinstance(to, list):
#             assert isinstance(frm, PersistentVector)
#
#             for x in range(len(to)):
#                 self._compare(rt.nth(frm, rt.wrap(x)), to[x])
#
#         else:
#             raise Exception("Don't know how to handle " + str(type(to)))
#
#     def test_forms(self):
#         for s in data:
#             tst = data[s]
#             result = read(StringReader(s), True)
#             assert isinstance(result, Object)
#
#             self._compare(result, tst)
#
#

def _compare(frm, to):
    if isinstance(to, tuple):
        assert isinstance(frm, PersistentList)

        for x in to:
            _compare(frm.first(), x)
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
            _compare(rt.nth(frm, rt.wrap(x)), to[x])

    else:
        raise Exception("Don't know how to handle " + str(type(to)))

if __name__ == '__main__':
    unittest.main()