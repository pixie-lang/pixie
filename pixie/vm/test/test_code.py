import unittest

from pixie.vm.effects.effects import *
from pixie.vm.code import wrap_fn




class TestWrapFn(unittest.TestCase):
    def test_arity_0(self):

        @wrap_fn
        def fn_Ef():
            return 42

        result = fn_Ef.invoke_Ef(ArgList())
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 42)

    def test_arity_1(self):

        @wrap_fn
        def fn_Ef(x):
            return x

        result = fn_Ef.invoke_Ef(ArgList([1]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 1)

    def test_arity_2(self):

        @wrap_fn
        def fn_Ef(x, y):
            return y

        result = fn_Ef.invoke_Ef(ArgList([1, 2]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 2)

    def test_arity_3(self):

        @wrap_fn
        def fn_Ef(x, y, z):
            return z

        result = fn_Ef.invoke_Ef(ArgList([1, 2, 3]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 3)

    def test_arity_4(self):

        @wrap_fn
        def fn_Ef(x, y, z, a):
            return a

        result = fn_Ef.invoke_Ef(ArgList([1, 2, 3, 4]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 4)

    def test_variadic(self):

        @wrap_fn
        def fn__args(args):
            return args

        args = ArgList([1, 2, 3, 4])
        result = fn__args.invoke_Ef(args)
        self.assertIsInstance(result, Answer)
        self.assertIs(result.val(), args)