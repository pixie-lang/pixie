import pixie.vm.protocols as proto
from pixie.vm.code import BaseCode

def unwrap(fn):
    return lambda *args: fn.invoke(list(args))

for name, fn in proto.__dict__.iteritems():
    if isinstance(fn, BaseCode):
        globals()[name] = unwrap(fn)



