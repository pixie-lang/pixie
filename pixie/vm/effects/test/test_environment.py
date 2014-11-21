import unittest
from pixie.vm.effects.effects import *
from pixie.vm.effects.environment import *
from pixie.vm.effects.effect_transform import resource_effect
from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.code import wrap_fn
from pixie.vm.keyword import keyword

defeffect("pixie.stdlib.test.TestResource", "TestResource", ["a", "b"])

class ResourceHandler(Handler):
    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return effect
        if isinstance(effect, Effect) and effect.type() is TestResource._type:
            val = effect.get(KW_A) + effect.get(KW_B)
            return handle_with(self, ContinuationThunk(effect.get(KW_K), val), answer_k)

def foo_Ef(a, b):
    return TestResource(a, b)

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

        result = run_thunk_with_state(handle_with(ResourceHandler(), doit.invoke_Ef(ArgList()), answer_k), default_env)
        pass
