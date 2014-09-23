from loki_vm.vm.compiler import compile
from loki_vm.vm.reader import StringReader, read
from loki_vm.vm.interpreter import interpret
import sys


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