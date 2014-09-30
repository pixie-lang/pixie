import unittest
from pixie.vm.code import intern_var, get_var_if_defined


def test_intern():
    assert intern_var("foo", "bar") is intern_var("foo", "bar")
    assert intern_var("foo2", "bar") is not intern_var("foo", "bar")

    assert get_var_if_defined("foo", "bar")
    assert get_var_if_defined("foo2", "bar")