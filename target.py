from pixie.vm.compiler import compile, with_ns, NS_VAR
from pixie.vm.reader import StringReader, read, eof, PromptReader, MetaDataReader
from pixie.vm.interpreter import interpret
from rpython.jit.codewriter.policy import JitPolicy
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.annotator.policy import AnnotatorPolicy
from pixie.vm.code import wrap_fn, NativeFn, intern_var
from pixie.vm.stacklet import with_stacklets
import pixie.vm.stacklet as stacklet
from pixie.vm.object import RuntimeException, WrappedException
from rpython.translator.platform import platform
from pixie.vm.primitives import nil
import sys


class DebugIFace(JitHookInterface):
    def on_abort(self, reason, jitdriver, greenkey, greenkey_repr, logops, operations):
        print "Aborted Trace, reason: ", Counters.counter_names[reason], logops, greenkey_repr

import sys, pdb

class Policy(JitPolicy, AnnotatorPolicy):
    def __init__(self):
        JitPolicy.__init__(self, DebugIFace())

def jitpolicy(driver):
    return JitPolicy(jithookiface=DebugIFace())


PROGRAM_ARGUMENTS = intern_var(u"pixie.stdlib", u"program-arguments")
PROGRAM_ARGUMENTS.set_root(nil)


class ReplFn(NativeFn):
    def __init__(self, args):
        self._argv = args

    def inner_invoke(self, args):
        from pixie.vm.keyword import keyword
        import pixie.vm.rt as rt
        from pixie.vm.string import String
        import pixie.vm.persistent_vector as vector

        print "Pixie 0.1 - Interactive REPL"
        print "(" + platform.name + ", " + platform.cc + ")"
        print "----------------------------"

        with with_ns(u"user"):
            NS_VAR.deref().include_stdlib()

        acc = vector.EMPTY
        for x in self._argv:
            acc = rt.conj(acc, rt.wrap(x))

        PROGRAM_ARGUMENTS.set_root(acc)


        rdr = MetaDataReader(PromptReader())
        with with_ns(u"user"):
            while True:
                try:
                    val = read(rdr, False)
                    if val is eof:
                        break
                    val = interpret(compile(val))
                except WrappedException as ex:
                    print "Error: ", ex._ex.__repr__()
                    rdr.reset_line()
                    continue
                if val is keyword(u"exit-repl"):
                    break
                val = rt.str(val)
                assert isinstance(val, String), "str should always return a string"
                print val._str

class BatchModeFn(NativeFn):
    def __init__(self, args):
        self._cmd  = args[0]
        self._argv = args[1:]

    def inner_invoke(self, args):
        import pixie.vm.rt as rt
        import pixie.vm.persistent_vector as vector

        with with_ns(u"user"):
            NS_VAR.deref().include_stdlib()

        acc = vector.EMPTY
        for x in self._argv:
            acc = rt.conj(acc, rt.wrap(x))

        PROGRAM_ARGUMENTS.set_root(acc)

        rt.load_file(rt.wrap(self._cmd))

def entry_point(args):
    interactive = True
    n = 0
    script_args = []

    for arg in args[1:]:
        if arg.startswith('-'):
            if arg == '-v' or arg == '--version':
                print "Pixie 0.1"
                return 0
            elif arg == '-h' or arg == '--help':
                print args[0] + " [<options>] [<file>]"
                print "  -h|--help     print this help"
                print "  -v|--version  print the version number"
                return 0
            else:
                print "Unknown option " + arg
                return 1
        else:
            interactive = False
            script_args = args[(n+1):]
            break

        n += 1

    if interactive:
        with_stacklets(ReplFn(args))
    else:
        with_stacklets(BatchModeFn(script_args))

    return 0



from rpython.rtyper.lltypesystem import lltype
from rpython.jit.metainterp import warmspot

def run_child(glob, loc):
    interp = loc['interp']
    graph = loc['graph']
    interp.malloc_check = False

    def returns_null(T, *args, **kwds):
        return lltype.nullptr(T)
    interp.heap.malloc_nonmovable = returns_null     # XXX

    from rpython.jit.backend.llgraph.runner import LLGraphCPU
    #LLtypeCPU.supports_floats = False     # for now
    apply_jit(interp, graph, LLGraphCPU)


def apply_jit(interp, graph, CPUClass):
    print 'warmspot.jittify_and_run() started...'
    policy = Policy()
    warmspot.jittify_and_run(interp, graph, [], policy=policy,
                             listops=True, CPUClass=CPUClass,
                             backendopt=True, inline=True)

def run_debug(argv):
    from rpython.rtyper.test.test_llinterp import get_interpreter

    # first annotate and rtype
    try:
        interp, graph = get_interpreter(entry_point, [], backendopt=False,
                                        #config=config,
                                        #type_system=config.translation.type_system,
                                        policy=Policy())
    except Exception, e:
        print '%s: %s' % (e.__class__, e)
        pdb.post_mortem(sys.exc_info()[2])
        raise

    # parent process loop: spawn a child, wait for the child to finish,
    # print a message, and restart
    #unixcheckpoint.restartable_point(auto='run')

    from rpython.jit.codewriter.codewriter import CodeWriter
    CodeWriter.debug = True
    run_child(globals(), locals())

import pixie.vm.rt as rt
rt.init()
stacklet.global_state = stacklet.GlobalState()

def target(*args):
    import pixie.vm.rt as rt
    driver = args[0]
    driver.exe_name = "pixie-vm"
    rt.__config__ = args[0].config




    return entry_point, None

import rpython.config.translationoption
print rpython.config.translationoption.get_combined_translation_config()

if __name__ == "__main__":
    entry_point(sys.argv)
