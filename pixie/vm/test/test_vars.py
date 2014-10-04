import unittest
from pixie.vm.code import intern_var, get_var_if_defined


def test_intern():
    assert intern_var(u"foo", u"bar") is intern_var(u"foo", u"bar")
    assert intern_var(u"foo2", u"bar") is not intern_var(u"foo", u"bar")

    assert get_var_if_defined(u"foo", u"bar")
    assert get_var_if_defined(u"foo2", u"bar")