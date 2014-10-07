__config__ = None

def unwrap(fn):
    return lambda *args: fn.invoke(list(args))

def init():
    if globals().has_key("__inited__"):
        return

    import pixie.vm.numbers as numbers
    import pixie.vm.stacklet
    import pixie.vm.atom
    numbers.init()

    from pixie.vm.code import _ns_registry, BaseCode, munge

    for name, var in _ns_registry._registry[u"pixie.stdlib"]._registry.iteritems():
        name = munge(name)
        print name
        if isinstance(var.deref(), BaseCode):
            globals()[name] = unwrap(var)
        else:
            globals()[name] = var

    globals()["__inited__"] = True






