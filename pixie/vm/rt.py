__config__ = None
py_list = list


def unwrap(fn):
    return lambda *args: fn.invoke(py_list(args))

def init():
    if globals().has_key("__inited__"):
        return

    import pixie.vm.numbers as numbers
    import pixie.vm.stacklet
    import pixie.vm.atom
    import pixie.vm.reduced
    import pixie.vm.util
    import pixie.vm.array
    import pixie.vm.lazy_seq
    import pixie.vm.persistent_list
    import pixie.vm.custom_types
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






