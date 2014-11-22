import unittest

from pixie.vm.effects.effects import *
from pixie.vm.effects.environment import FindPolymorphicOverride, KW_NAME, KW_TP, KW_TP1, KW_TP2, KW_K, PolymorphicFn
from pixie.vm.code import wrap_fn
from pixie.vm.numbers import Integer
from pixie.vm.keyword import keyword




class TestWrapFn(unittest.TestCase):
    def test_arity_0(self):

        @wrap_fn()
        def fn_Ef():
            return 42

        result = fn_Ef.invoke_Ef(ArgList())
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 42)

    def test_arity_1(self):

        @wrap_fn()
        def fn_Ef(x):
            return x

        result = fn_Ef.invoke_Ef(ArgList([1]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 1)

    def test_arity_2(self):

        @wrap_fn()
        def fn_Ef(x, y):
            return y

        result = fn_Ef.invoke_Ef(ArgList([1, 2]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 2)

    def test_arity_3(self):

        @wrap_fn()
        def fn_Ef(x, y, z):
            return z

        result = fn_Ef.invoke_Ef(ArgList([1, 2, 3]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 3)

    def test_arity_4(self):

        @wrap_fn()
        def fn_Ef(x, y, z, a):
            return a

        result = fn_Ef.invoke_Ef(ArgList([1, 2, 3, 4]))
        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 4)

    def test_variadic(self):

        @wrap_fn()
        def fn__args(args):
            return args

        args = ArgList([1, 2, 3, 4])
        result = fn__args.invoke_Ef(args)
        self.assertIsInstance(result, Answer)
        self.assertIs(result.val(), args)


class TestPolymorphicFn(unittest.TestCase):
    def test_calling_polymorphic_fn(self):
        pfn_name = keyword(u"pixie.stdlib.-foo")
        pfn = PolymorphicFn(u"pixie.stdlib.IFoo", pfn_name)

        result = pfn.invoke_Ef(ArgList([Integer(42)]))

        self.assertIsInstance(result, FindPolymorphicOverride)
        self.assertIs(result.get(KW_NAME), pfn_name)
        self.assertIs(result.get(KW_TP), Integer(0).type())

        @wrap_fn()
        def fn_arg(x):
            return x

        result = result.get(KW_K).step(fn_arg)
        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 42)
