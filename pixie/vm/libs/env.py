from pixie.vm.code import as_var
from pixie.vm.object import Object, Type, runtime_error
from pixie.vm.primitives import nil
from pixie.vm.string import String
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
import pixie.vm.rt as rt
import os

class Environment(Object):
    _type = Type(u"pixie.stdlib.Environment")

    def val_at(self, key, not_found):
        if not isinstance(key, String):
            runtime_error(u"Environment variables are strings ")
        key_str = str(rt.name(key))
        try:
            var = os.environ[key_str]
            return rt.wrap(var)
        except KeyError:
            return not_found
    
    # TODO: Implement me.
    # def dissoc(self):
    # def asssoc(self):

    def reduce_vars(self, f, init):
        for k, v in os.environ.items():
            init = f.invoke([init, rt.map_entry(rt.wrap(k), rt.wrap(v))])
            if rt.reduced_QMARK_(init):
                return init
        return init

 
@extend(proto._val_at, Environment)
def _val_at(self, key, not_found):
    assert isinstance(self, Environment)
    v = self.val_at(key, not_found)
    return v

@extend(proto._reduce, Environment)
def _reduce(self, f, init):
    assert isinstance(self, Environment)
    val = self.reduce_vars(f, init)
    if rt.reduced_QMARK_(val):
        return rt.deref(val)

    return val

@as_var("pixie.stdlib", "env")
def _env():
    return Environment()
