from pixie.vm.stacklet import with_stacklets
import pixie.vm.stacklet as stacklet
from pixie.vm.code import wrap_fn

@wrap_fn
def bootstrap():
    import pixie.vm.rt as rt
    from pixie.vm.string import String
    assert False
    rt.load_file(String(u"pixie/stdlib.lisp"))


# run bootstrap
#with_stacklets(bootstrap)
# reset the stacklet state so we can translate with different settings
stacklet.global_state = stacklet.GlobalState()