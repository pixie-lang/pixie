from loki_vm.vm.compiler import compile
from loki_vm.vm.reader import StringReader, read
from loki_vm.vm.interpreter import interpret
from rpython.jit.codewriter.policy import JitPolicy
from rpython.rlib.jit import JitHookInterface, Counters
import sys


class DebugIFace(JitHookInterface):
    def on_abort(self, reason, jitdriver, greenkey, greenkey_repr, logops, operations):
        print "Aborted Trace, reason: ", Counters.counter_names[reason]

def jitpolicy(driver):
    return JitPolicy(jithookiface=DebugIFace())

def entry_point(argv):
    try:
        code = argv[1]
    except IndexError:
        print "must provide a program"
        return 1

    interpret(compile(read(StringReader(code), True)))

    return 0

def target(*args):
    return entry_point, None

if __name__ == "__main__":
    entry_point(sys.argv)