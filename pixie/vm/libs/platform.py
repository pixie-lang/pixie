from rpython.translator.platform import platform
from pixie.vm.string import String
from pixie.vm.code import as_var
from rpython.rlib.clibffi import get_libc_name
import os


as_var("pixie.platform", "os")(String(unicode(os.name)))
as_var("pixie.platform", "name")(String(unicode(platform.name)))
as_var("pixie.platform", "so-ext")(String(unicode(platform.so_ext)))
as_var("pixie.platform", "lib-c-name")(String(unicode(get_libc_name())))
