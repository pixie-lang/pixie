import pixie.vm.rt as rt
from pixie.vm.code import as_var, extend
from pixie.vm.object import Object, Type
import pixie.vm.stdlib as proto
from pixie.vm.primitives import true, false
import os

class Path(Object):
    _type = Type(u"pixie.path.Path")

    def type(self):
        return Path._type

    def __init__(self, top):
        self._path = rt.name(top)

    # keyword args don't seem to work nicely.
    #def rel_path(self, other):
    #    "Returns the path relative to other path"
    #    return rt.wrap(str(os.path.relpath(self._path, start=other._path)))

    def abs_path(self):
        "Returns the absolute path"
        return rt.wrap(os.path.abspath(str(self._path)))

    # Basename doesn't play well with pypy...
    #def basename(self):
    #    return rt.wrap(rt.name(os.path.basename("a")))

    def exists(self):
        return true if os.path.exists(str(self._path)) else false

    def is_file(self):
        return true if os.path.isfile(str(self._path)) else false

    def is_dir(self):
        return true if os.path.isdir(str(self._path)) else false

@extend(proto._reduce, Path)
def _reduce(self, f, init):
    assert isinstance(self, Path)
    for dirpath, dirnames, filenames in os.walk(str(self._path)):
        for dirname in dirnames:
            init = f.invoke([init, Path(rt.wrap(dirpath + "/" + dirname))])
            if rt.reduced_QMARK_(init):
                return rt.deref(init)

        for filename in filenames:
            init = f.invoke([init, Path(rt.wrap(dirpath + "/" + filename))])
            if rt.reduced_QMARK_(init):
                return rt.deref(init)

    return init

# I have named prefixed all names with '-' to deal with the
# a namespace issue I was having.
# TODO: remove '-' and update calling functions when issue is fixed.

@as_var("pixie.path", "-path")
def path(path):
    return Path(path)

# TODO: Implement this
@as_var("pixie.path", "-list-dir")
def list_dir(self):
    assert isinstance(self, Path)
    result = rt.vector()
    for item in os.listdir(str(self._path)):
        result = rt.conj(result, rt.wrap(str(self._path) + "/" + str(item)))
    return result

@as_var("pixie.path", "-abs")
def _abs(self):
    assert isinstance(self, Path)
    return self.abs_path()

@as_var("pixie.path", "-exists?")
def exists_QMARK_(self):
    assert isinstance(self, Path)
    return self.exists()

@as_var("pixie.path", "-file?")
def file_QMARK_(self):
    assert isinstance(self, Path)
    return self.is_file()

@as_var("pixie.path", "-dir?")
def dir_QMARK_(self):
    assert isinstance(self, Path)
    return self.is_dir()
