from rpython.translator.platform import platform
import pixie.vm.rt as rt
from pixie.vm.string import String
from pixie.vm.code import as_var
import os


as_var("pixie.platform", "os")(String(os.name))
as_var("pixie.platform", "name")(String(platform.name))
as_var("pixie.platform", "so-ext")(String(platform.so_ext))

