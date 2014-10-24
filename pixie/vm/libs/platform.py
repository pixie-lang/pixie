from rpython.translator.platform import platform
import pixie.vm.rt as rt
from pixie.vm.string import String
from pixie.vm.code import as_var
import os


as_var("pixie.platform", "os")(String(unicode(os.name)))
as_var("pixie.platform", "name")(String(unicode(platform.name)))
as_var("pixie.platform", "so-ext")(String(unicode(platform.so_ext)))

