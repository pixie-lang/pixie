from pixie.vm.compiler import compile_Ef
from pixie.vm.code import wrap_fn
from pixie.vm.reader import StringReader, read_Ef
from pixie.vm.effects.effects import Answer
from pixie.vm.numbers import Integer
from pixie.vm.string import String
from pixie.vm.effects.effect_transform import cps
from pixie.vm.ast import SyntaxThunk
from pixie.vm.effects.environment import run_with_state, default_env, run_thunk_with_state, _builtin_defs

import unittest

@wrap_fn()
def read_and_compile(arg):
    rdr = StringReader(arg)
    result = read_Ef(rdr, True)
    return compile_Ef(result)



class TestCompilation(unittest.TestCase):
    def test_compile_integer(self):

        ast = run_with_state(read_and_compile, default_env, "1")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), None), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)

    def test_compile_call_global(self):

        ast = run_with_state(read_and_compile, default_env, "(-str 1)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), None), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), String)
        self.assertEqual(result.val().str(), "1")


    def test_compile_if(self):

        ast = run_with_state(read_and_compile, default_env, "(if true 1 2)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), None), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)

        ast = run_with_state(read_and_compile, default_env, "(if false 1 2)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), None), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 2)
