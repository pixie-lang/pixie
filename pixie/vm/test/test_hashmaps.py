import unittest
import pixie.vm.rt as rt
from pixie.vm.numbers import Integer
from pixie.vm.primitives import nil

rt.init()

def test_hashmap_create():

    acc = rt.hashmap(rt.wrap(1), rt.wrap(2))

    val = rt._val_at(acc, rt.wrap(1), nil)

    assert val.int_val() == 2