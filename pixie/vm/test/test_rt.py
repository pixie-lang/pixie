import unittest

from pixie.vm.effects.environment import Resolve, run_with_state, Environment
from pixie.vm.effects.effects import Answer, ArgList
from pixie.vm.code import wrap_fn
from pixie.vm.keyword import Keyword, keyword
import pixie.vm.rt as rt


class TestRTDispatch(unittest.TestCase):
    def test_RT_intercept(self):
        ns = keyword(u"pixie.stdlib")
        nm = keyword(u"first")

        @wrap_fn
        def testfn__args(args):
            return args

        result = rt.first_Ef(1)
        self.assertIsInstance(result, Resolve)
        self.assertIs(result._w_ns, ns)
        self.assertIs(result._w_nm, nm)

        result = result._k.step(testfn__args)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), ArgList)
        self.assertEqual(result.val()._args_w[0], 1)
