from loki_vm.vm.reader import read, StringReader, eof
from loki_vm.vm.object import Object
from loki_vm.vm.cons import Cons
from loki_vm.vm.numbers import Integer
from loki_vm.vm.symbol import symbol, Symbol
from loki_vm.vm.compiler import compile_form, compile
from loki_vm.vm.interpreter import interpret
from loki_vm.vm.code import Code, Var
from loki_vm.vm.primitives import nil, true, false
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

        result = interpret(compile(form))


def test_fn():
    code = compile(read_code("((fn (x y) (platform+ x y)) 1 2)"))
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
    assert isinstance(eval_string("((fn r () r))"), Code)

def test_recursive():
    retval = eval_string("""((fn rf (x)
                               (if (platform= x 10)
                                   x
                                   (rf (platform+ x 1))))
                              0)""")

    assert isinstance(retval, Integer)
    assert retval.int_val() == 10

def test_closures():
    retval = eval_string("""((fn (x) ((fn () x))) 42)""")

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