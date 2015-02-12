from rpython.translator.platform import platform
from pixie.vm.persistent_list import create_from_list
from pixie.vm.string import String
from pixie.vm.code import as_var
from rpython.rlib.clibffi import get_libc_name
import os


as_var("pixie.platform", "os")(String(unicode(os.name)))
as_var("pixie.platform", "name")(String(unicode(platform.name)))
as_var("pixie.platform", "so-ext")(String(unicode(platform.so_ext)))
as_var("pixie.platform", "lib-c-name")(String(unicode(get_libc_name())))

c_flags = []
for itm in platform.cflags:
    c_flags.append(String(unicode(itm)))

as_var("pixie.platform", "c-flags")(create_from_list(c_flags))

link_flags = []
for itm in platform.link_flags:
    c_flags.append(String(unicode(itm)))
as_var("pixie.platform", "link-flags")(create_from_list(link_flags))
