import unittest
import pixie.vm.rt as rt
from pixie.vm.numbers import Integer
from pixie.vm.primitives import nil

rt.init()

def test_hashmap_create():

    acc = rt.hashmap(Integer(1), Integer(2))

    val = rt._val_at(acc, Integer(1), nil)

    assert val.int_val() == 2