from pixie.vm.compiler import compile_Ef
from pixie.vm.primitives import true
from pixie.vm.code import wrap_fn
from pixie.vm.reader import StringReader, read_Ef
from pixie.vm.effects.effects import Answer
from pixie.vm.numbers import Integer
from pixie.vm.string import String
from pixie.vm.effects.effect_transform import cps
from pixie.vm.effects.generators import Generator
from pixie.vm.ast import SyntaxThunk, Locals
from pixie.vm.effects.environment import run_with_state, default_env, run_thunk_with_state
from pixie.vm.keyword import keyword

import unittest

@wrap_fn()
def read_and_compile(arg):
    rdr = StringReader(arg)
    result = read_Ef(rdr, True)
    return compile_Ef(result)



class TestCompilation(unittest.TestCase):
    def test_compile_integer(self):

        ast = run_with_state(read_and_compile, default_env, "1")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)

    def test_compile_call_global(self):

        ast = run_with_state(read_and_compile, default_env, "(-str 1)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), String)
        self.assertEqual(result.val().str(), "1")


    def test_compile_if(self):

        ast = run_with_state(read_and_compile, default_env, "(if true 1 2)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)

        ast = run_with_state(read_and_compile, default_env, "(if false 1 2)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 2)

    def test_function(self):

        ast = run_with_state(read_and_compile, default_env, "((fn* foo [x] (if x 1 2)) true)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)


        ast = run_with_state(read_and_compile, default_env, "((fn* foo [x] (if x 1 2)) false)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 2)

    def test_variadic_function(self):

        ast = run_with_state(read_and_compile, default_env, "((fn* foo [& r] (-count r)) true)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)


        ast = run_with_state(read_and_compile, default_env, "((fn* foo [x & r] (-count r)) 1 2 3)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 2)


    def test_mult_arity_function(self):

        ast = run_with_state(read_and_compile, default_env, "((fn* foo ([x] 1) ([x y] 2)) true)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 1)


        ast = run_with_state(read_and_compile, default_env, "((fn* foo ([x] 1) ([x y] 2)) 1 true)")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 2)


    def test_recursive_fn(self):
        ast = run_with_state(read_and_compile, default_env, """((fn* self [x]
                                                                  (if (-num-eq x 10)
                                                                    x
                                                                    (self (-add 1 x))))
                                                                0)""")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 10)

    def test_def(self):
        ast = run_with_state(read_and_compile, default_env, """(do (def x 42) x)""")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 42)

    def test_let(self):
        ast = run_with_state(read_and_compile, default_env, """(let* [x 40 y 2] (-add x y))""")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 42)


    def test_recursive_ref_fn(self):
        ast = run_with_state(read_and_compile, default_env, """(-with-ref 0
                                                                 (fn* countup [id]
                                                                   (let* [x (get-ref id)]
                                                                     (if (-num-eq x 3)
                                                                       x
                                                                       (do (swap-ref id (-add x 1))
                                                                           (countup id))))))""")
        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Integer)
        self.assertEqual(result.val().int_val(), 3)

    def test_yield_exists(self):
        from pixie.vm.effects.generators import YieldEffect
        ast = run_with_state(read_and_compile, default_env,

                             """(yield 42)""")

        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env, error_on_unhandled=False)

        self.assertIsInstance(result, YieldEffect, str(result))

    def test_handle_works(self):
        from pixie.vm.effects.generators import YieldEffect
        ast = run_with_state(read_and_compile, default_env,

                             """(-handle
                                  (fn* [e]
                                    (effect? e))
                                  (fn* [] (yield 42)))""")

        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env, error_on_unhandled=False)

        self.assertIsInstance(result, Answer)
        self.assertIs(result.val(), true)


    def test_generators(self):
        ast = run_with_state(read_and_compile, default_env,

                             """(-generator
                                  (fn* [] (yield 42)
                                          (yield 43)
                                          :done))""")

        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Generator)
        self.assertEqual(result.val().val().int_val(), 42)

        result = run_with_state(result.val(), default_env)

        self.assertIsInstance(result, Answer)
        self.assertIsInstance(result.val(), Generator)
        self.assertEqual(result.val().val().int_val(), 43)

        result = run_with_state(result.val(), default_env)

        self.assertIsInstance(result, Answer)
        self.assertNotIsInstance(result.val(), Generator)
        self.assertIs(result.val(), keyword("done"))


    def test_count_generator(self):
        ast = run_with_state(read_and_compile, default_env,

                             """((fn* loop [g i]
                                  (if (generator? g)
                                    (loop (g) (-add i 1))
                                    i))
                                  (-iterator [1 2 3])
                                  0)""")

        result = run_thunk_with_state(SyntaxThunk(ast.val(), Locals()), default_env)

        self.assertIsInstance(result, Answer)
        self.assertEqual(result.val().int_val(), 3)

