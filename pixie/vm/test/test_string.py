import unittest
from pixie.vm.string import *
from pixie.vm.effects.effects import *
from pixie.vm.code import wrap_fn
import pixie.vm.rt as rt
from pixie.vm.effects.environment import run_with_state, default_env
from pixie.vm.numbers import Integer


class TestString(unittest.TestCase):
    def test_string_creation(self):

        s = String(u"foo")
        self.assertEqual(s._str, u"foo")


    def test_string_count(self):

        @wrap_fn()
        def count_it():
            s = String(u"Foo")
            return rt.count_Ef(s)

        result = run_with_state(count_it, default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 3)


    def test_str(self):

        @wrap_fn()
        def fn():
            s = String(u"Foo")
            return rt._str_Ef(s)

        result = run_with_state(fn, default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), String)
        self.assertEqual(result.val()._str, u"Foo")
