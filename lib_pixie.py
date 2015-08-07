import ctypes, sys

dll = ctypes.CDLL("libpixie-vm.dylib")

dll.rpython_startup_code()
dll.pixie_init(sys.argv[0])

def repl():
    dll.pixie_execute_source("(ns user (:require [pixie.repl :as repl])) (pixie.repl/repl)")

repl()