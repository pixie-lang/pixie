from pixie.vm.stacklet import with_stacklets
from pixie.vm.code import NativeFn, wrap_fn
from pixie.vm.libs.uv_file import _open, FileHandle
import pixie.vm.rt as rt
import unittest

rt.init()

class TestUV(unittest.TestCase):

    def test_open_once(self):

        @wrap_fn
        def test():
            result = _open.invoke([rt.wrap("README.md"), rt.wrap(0), rt.wrap(0)])
            self.assertIsInstance(result, FileHandle)

        with_stacklets(test)

    def test_open_once_several(self):

        @wrap_fn
        def test():
            result = _open.invoke([rt.wrap("README.md"), rt.wrap(0), rt.wrap(0)])
            self.assertIsInstance(result, FileHandle)

        for x in range(10):
            with_stacklets(test)


