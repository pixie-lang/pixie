from pixie.vm.reader import read, StringReader, eof
from pixie.vm.object import Object, Type
from pixie.vm.cons import Cons
from pixie.vm.numbers import Integer
from pixie.vm.symbol import symbol, Symbol
from pixie.vm.keyword import Keyword
from pixie.vm.compiler import compile_form, compile
from pixie.vm.interpreter import interpret
from pixie.vm.code import Code, Var
from pixie.vm.primitives import nil, true, false
from pixie.vm.custom_types import CustomTypeInstance
import unittest

def read_code(s):
    return read(StringReader(s), False)

def test_add_compilation():
    code = compile(read_code("(platform+ 1 2)"))
    assert isinstance(code, Code)

    #interpret(code)

def eval_string(s):
    rdr = StringReader(s)
    result = nil
    while True:
        form = read(rdr, False)
        if form is eof:
            return result

        result = compile(form).invoke([])

def test_fn():
    code = compile(read_code("((fn [x y] (+ x y)) 1 2)"))
    assert isinstance(code, Code)
    retval = interpret(code)
    assert isinstance(retval, Integer) and retval.int_val() == 3

def test_if():
    code = compile(read_code("(if 1 2 3)"))
    assert  isinstance(code, Code)

    retval = interpret(code)
    assert isinstance(retval, Integer) and retval.int_val() == 2
    code = compile(read_code("(if false 2 3)"))
    assert isinstance(code, Code)
    retval = interpret(code)
    assert isinstance(retval, Integer) and retval.int_val() == 3

def test_eq():
    assert eval_string("(platform= 1 2)") is false
    assert eval_string("(platform= 1 1)") is true

def test_if_eq():
    assert eval_string("(if (platform= 1 2) true false)") is false

def test_return_self():
    assert isinstance(eval_string("((fn r [] r))"), Code)

def test_recursive():
    retval = eval_string("""((fn rf [x]
                               (if (platform= x 100)
                                   x
                                   (recur (+ x 1))))
                               0)""")

    assert isinstance(retval, Integer)
    assert retval.int_val() == 100

def test_closures():
    retval = eval_string("""((fn [x] ((fn [] x))) 42)""")

    assert isinstance(retval, Integer)
    assert retval.int_val() == 42


def test_def():
    retval = eval_string("""(def x 42)""")
    assert isinstance(retval, Var)

    retval = eval_string("""(do (def x 42) x)""")
    assert isinstance(retval, Integer)

    retval = eval_string("""(def y 42) y""")
    assert isinstance(retval, Integer)
    assert retval.int_val() == 42

def test_native():
    retval = eval_string("""(type 42)""")
    assert isinstance(retval, Type)


def test_build_list():
    retval = eval_string("""((fn [i lst]
                              (if (platform= i 100)
                                (count lst)
                                (recur (+ i 1) (cons i lst)))) 0 nil)
     """)

    assert isinstance(retval, Integer) and retval.int_val() == 100

def test_build_vector():
    retval = eval_string("""((fn [i lst]
                              (if (platform= i 100)
                                (count lst)
                                (recur (+ i 1) (conj lst i)))) 0 [])
     """)

    assert isinstance(retval, Integer) and retval.int_val() == 100
#
# def test_handlers():
#     retval = eval_string("""(def x 42)
#                             (platform_install_handler 42 (fn () 1))""")
#     assert isinstance(retval, Integer) and retval.int_val() == 1
#     retval = eval_string("""(def pass (fn (x k) (k true)))
#                             (set-effect! pass true)
#                             (def handler 42)
#                             (platform_install_handler handler (fn () (pass handler)))""")
#     assert retval is true
#
# def test_mult_call_handlers():
#     retval = eval_string("""(def pass (fn pass (x k) (+ (k 1) (k 2))))
#                             (set-effect! pass true)
#                             (def handler 42)
#                             (platform_install_handler handler (fn hfn () (pass handler) 42))""")
#
#     assert isinstance(retval, Integer) and retval.int_val() == 84
#
# def test_quoted():
#     retval = eval_string("""'(1 2)""")
#     assert isinstance(retval, Cons)
#     retval = eval_string("""'type""")
#     assert isinstance(retval, Symbol)
#
# def test_custom_type():
#     retval = eval_string("""(def my-type (make-type 'my-type '(:a :b)))
#                             (new my-type 1 2)""")
#     assert isinstance(retval, CustomTypeInstance)
#     retval = eval_string("""(def my-type (make-type 'my-type '(:a :b)))
#                             (get-field (new my-type 1 2) :a)""")
#     assert isinstance(retval, Integer) and retval.int_val() == 1
#
# def test_keyword():
#     retval = eval_string(""":foo""")
#     assert isinstance(retval, Keyword)
#
#
# def test_real_effects():
#     retval = eval_string("""
#
#     (do (def tp (make-type 'Foo '(:x)))
#         (def pass (fn (x) (get-field (new tp x) :x)))
#
#         ((fn r (x)
#             (if (platform= x 10000)
#               x
#               (r (+ 1 (pass x)))))
#
#         0))
#               """)
#
#     assert isinstance(retval, Integer) and retval.int_val() == 1000
#
#
# def test_real_effects():
#     retval = eval_string("""
#
#
#     (do (def tp (make-type 'Foo '(:x)))
#         (def pass (fn (x) (get-field (new tp x) :x)))
#         (def add (fn (h i k) (k (+ i 1))))
#         (set-effect! add true)
#         (def handler 0)
#
#         ((fn r (x)
#             (if (platform= x 10000)
#               x
#               (r (platform_install_handler handler (fn () (add handler x))))))
#
#         0))
#               """)
#
#     assert isinstance(retval, Integer) and retval.int_val() == 1000
#
#
#
