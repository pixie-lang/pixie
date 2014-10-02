import pixie.vm.stacklet as stacklet
import pixie.vm.code as code
import pixie.vm.rt as rt
import pixie.vm.numbers as numbers
from pixie.vm.primitives import nil

class YieldingFn(code.BaseCode):
    def _invoke(self, args):
        assert len(args) == 2
        hdler = args[0]
        arg = args[1]

        hdler.invoke([numbers.zero_int])
        hdler.invoke([numbers.one_int])
        hdler.invoke([numbers.Integer(2)])

        return



def test_stacklets():
    st = stacklet.new_stacklet(YieldingFn(), nil)
    result = st.invoke([nil])
    assert isinstance(result, numbers.Integer) and result.int_val() == 0
    result = st.invoke([nil])
    assert isinstance(result, numbers.Integer) and result.int_val() == 1
    result = st.invoke([nil])
    assert isinstance(result, numbers.Integer) and result.int_val() == 2

    pass