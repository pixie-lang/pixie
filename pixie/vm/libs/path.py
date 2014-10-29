import pixie.vm.rt as rt
from pixie.vm.string import String
from pixie.vm.code import as_var, extend
from pixie.vm.object import Object, Type
import pixie.vm.stdlib as proto
from pixie.vm.keyword import keyword
from rpython.rlib.clibffi import get_libc_name
import os
import pixie.vm.rt as rt

class FileList(Object):
    _type = Type(u"pixie.path.FileList")

    def type(self):
        return FileList._type

    def __init__(self, top):
        self._top = rt.name(top)

KW_DIR = keyword(u"dir")
KW_FILE = keyword(u"file")

@extend(proto._reduce, FileList)
def _reduce(self, f, init):
    assert isinstance(self, FileList)
    for dirpath, dirnames, filenames in os.walk(str(self._top)):
        for dirname in dirnames:
            init = f.invoke([init, rt.vector(rt.wrap(dirpath), KW_DIR, rt.wrap(dirname))])
            if rt.reduced_QMARK_(init):
                return rt.deref(init)

        for filename in filenames:
            init = f.invoke([init, rt.vector(rt.wrap(dirpath), KW_FILE, rt.wrap(filename))])
            if rt.reduced_QMARK_(init):
                return rt.deref(init)



    return init


@as_var("pixie.path", "file-list")
def file_list(path):
    return FileList(path)
