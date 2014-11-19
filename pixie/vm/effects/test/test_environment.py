import unittest
from pixie.vm.effects.effects import *
from pixie.vm.effects.environment import *
from pixie.vm.effects.effect_transform import resource_effect
from pixie.vm.code import wrap_fn
from pixie.vm.keyword import keyword

@resource_effect
def foo_Ef(x, y):
    return x + y


class TestEnvironment(unittest.TestCase):

    def test_define_resolve(self):


        @wrap_fn()
        def doit():
            ns = keyword(u"foo-ns")
            nm = keyword(u"foo-name")

            eff = Declare(ns, nm, 42)
            raise_Ef(eff)

            eff = Resolve(ns, nm)
            result = raise_Ef(eff)

            return result

        result = run_with_state(doit, default_env)

        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val(), 42)


    def test_opaque_resources(self):


        @wrap_fn()
        def doit():

            result = foo_Ef(1, 2)

            return result

        result = run_with_state(doit, default_env)
        pass
