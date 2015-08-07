import ctypes
import os.path

dll_name = os.path.join(os.path.dirname(__file__), "libpixie-vm.dylib")
print("Loading Pixie from " + dll_name)
dll = ctypes.CDLL(dll_name)

dll.rpython_startup_code()
dll.pixie_init("/Users/tim/oss/pixie/pixie-vm".encode("ascii"))


def repl():
    dll.pixie_execute_source("(ns user (:require [pixie.repl :as repl])) (pixie.repl/repl)".encode('ascii'))

#repl()