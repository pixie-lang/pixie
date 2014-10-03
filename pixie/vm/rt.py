__config__ = None

def unwrap(fn):
    return lambda *args: fn.invoke(list(args))

def init():
    if globals().has_key("__inited__"):
        return

    import pixie.vm.protocols as proto
    from pixie.vm.code import BaseCode
    for name, fn in proto.__dict__.iteritems():
        if isinstance(fn, BaseCode):
            globals()[name] = unwrap(fn)

    import pixie.vm.protocols as math
    from pixie.vm.code import BaseCode
    for name, fn in math.__dict__.iteritems():
        if isinstance(fn, BaseCode):
            globals()[name] = unwrap(fn)

    globals()["__inited__"] = True






