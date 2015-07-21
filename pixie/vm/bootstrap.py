from pixie.vm.code import wrap_fn

@wrap_fn
def bootstrap():
    import pixie.vm.rt as rt
    assert False
    rt.load_ns(rt.wrap(u"pixie/stdlib.pxi"))


