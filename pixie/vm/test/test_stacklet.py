import pixie.vm.stacklet as stacklet
import pixie.vm.code as code
import pixie.vm.rt as rt
import pixie.vm.numbers as numbers
from pixie.vm.primitives import nil

class YieldingFn(code.BaseCode):
    def invoke(self, args):
        assert len(args) == 2
        hdler = args[0]
        arg = args[1]

        hdler.invoke([numbers.zero_int])
        hdler.invoke([numbers.one_int])
        hdler.invoke([rt.wrap(2)])

        return


@code.wrap_fn
def yielding_fn(yld):

    yld.invoke([1])
    yld.invoke([2])
    yld.invoke([3])

    return 42

class WrappingFn(code.NativeFn):
    def __init__(self, cont):
        self._cont = cont
    def invoke(self, args):
        ret = args[0]
        ret.invoke([self._cont.invoke([4])])

def test_stacklets():
    @code.wrap_fn
    def main():
        cont = stacklet.new_stacklet(yielding_fn)
        assert cont.invoke([None]) == 1
        assert cont.invoke([None]) == 2
        assert cont.invoke([None]) == 3

    stacklet.with_stacklets(main)

    pass

def test_multi_stacklets():
    @code.wrap_fn
    def main():
        cont1 = stacklet.new_stacklet(yielding_fn)
        cont2 = stacklet.new_stacklet(yielding_fn)
        assert cont1.invoke([None]) == 1
        assert cont2.invoke([None]) == 1
        assert cont1.invoke([None]) == 2
        assert cont2.invoke([None]) == 2
        assert cont1.invoke([None]) == 3
        assert cont2.invoke([None]) == 3

    stacklet.with_stacklets(main)

    pass

def test_stacklets2():
     @code.wrap_fn
     def main():
         cont = stacklet.new_stacklet(yielding_fn)
         cont2 = stacklet.new_stacklet(WrappingFn(cont))
         cont2.invoke([44])

     stacklet.with_stacklets(main)

     pass