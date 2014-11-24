import unittest

from pixie.vm.effects.effect_transform import *
from pixie.vm.effects.effects import Answer, Effect, raise_Ef, handle, Thunk, Handler, handle_with, DefaultHandlerFn
from pixie.vm.effects.effect_generator import defeffect

defeffect("pixie.stdlib.YieldingEffect", "YieldEffect", ["val"])


@cps
def generator_Ef(max):
    x = 0
    while x < max:
        YieldEffect(x).raise_Ef()
        x += 1

    return False

@cps
def generate_3_Ef():
    result = generator_Ef(3)
    return result


def ground_thunk(x):
    while isinstance(x, Thunk):
        x = x.execute_thunk()
    return x

class TestFunctionTransform(unittest.TestCase):
    def run_simple_fn_test(self):
        """
        Test a simple CPS transformation
        """

        x = ground_thunk(generator_Ef(3))
        self.assertIsInstance(x, YieldEffect)
        self.assertEqual(x.get(KW_VAL), 0)
        x = ground_thunk(x.get(KW_K).step(None))

        self.assertIsInstance(x, YieldEffect)
        self.assertEqual(x.get(KW_VAL), 1)
        x = ground_thunk(x.get(KW_K).step(None))


        self.assertIsInstance(x, YieldEffect)
        self.assertEqual(x.get(KW_VAL), 2)
        x = ground_thunk(x.get(KW_K).step(None))

        self.assertIsInstance(x, Answer)
        self.assertEqual(x.val(), False)

    def run_nested_fn_test(self):
        """
        Tests that effects can move up through functions
        """
        x = ground_thunk(generate_3_Ef())
        self.assertIsInstance(x, YieldEffect)
        self.assertEqual(x.get(KW_VAL), 0)
        x = ground_thunk(x.get(KW_K).step(None))

        self.assertIsInstance(x, YieldEffect)
        self.assertEqual(x.get(KW_VAL), 1)
        x = ground_thunk(x.get(KW_K).step(None))


        self.assertIsInstance(x, YieldEffect)
        self.assertEqual(x.get(KW_VAL), 2)
        x = ground_thunk(x.get(KW_K).step(None))

        self.assertIsInstance(x, Answer)
        self.assertEqual(x.val(), False)


    def test_custom_handler(self):
        """
        Tests the installation of handlers, creates a handler that re-installs itself with new state on each yielded
        value. Once it gets an Answer it returns the total number of items received.
        """

        class CountHandler(Handler):
            def __init__(self, cnt):
                self._cnt = cnt

            def handle(self, effect, k):
                if isinstance(effect, YieldEffect):
                    return handle_with(CountHandler(self._cnt + 1),
                                       DefaultHandlerFn(effect.get(KW_K), None))
                if isinstance(effect, Answer):
                    return Answer(self._cnt)

        x = ground_thunk(handle_with(CountHandler(0), generate_3_Ef()))

        self.assertIsInstance(x, Answer)
        self.assertEqual(x.val(), 3)
