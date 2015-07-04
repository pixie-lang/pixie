
import pixie.vm2.interpreter as i
from pixie.vm2.interpreter import run_stack
from pixie.vm2.object import StackCell
import pixie.vm2.rt as rt
from pixie.vm2.primitives import nil, true, false
import pixie.vm2.code as code
from pixie.vm2.keyword import keyword as kw
from pixie.vm2.symbol import symbol as sym
from pixie.vm2.numbers import parse_number
from pixie.vm2.pxic_reader import read_file, read_object, Reader
from rpython.rlib.objectmodel import we_are_translated

rt.init()
import sys

def testit(max):
    rdr = Reader("./bootstrap.pxic")
    while True:
        try:
            obj = read_object(rdr)
        except EOFError:
            break
        if not we_are_translated():
            print ".",
            sys.stdout.flush()
        run_stack(None, i.InterpretK(obj, None))

    return None
    #pixie_code = read_file("/tmp/bootstrap.pxic")
    #return run_stack(None, i.InterpretK(pixie_code, None))

#val = testit()
#print val.int_val(), val

def entry_point(args):
    #s = rt.wrap(u"Foo")
    from pixie.vm2.string import String
    v = parse_number(u"1")

    s = String(u"Foo")
    max = 10000 #int(args[1])

    val = testit(max)
    return 43

## JIT STUFF


from rpython.jit.codewriter.policy import JitPolicy
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.rfile import create_stdio
from rpython.annotator.policy import AnnotatorPolicy
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

#stacklet.global_state = stacklet.GlobalState()

class DebugIFace(JitHookInterface):
    def on_abort(self, reason, jitdriver, greenkey, greenkey_repr, logops, operations):
        print "Aborted Trace, reason: ", Counters.counter_names[reason], logops, greenkey_repr
        #from rpython.rlib.objectmodel import we_are_translated
        #import pdb; pdb.set_trace()
        #exit(0)
        pass

    def before_compile_bridge(self, debug_info):
        print "Compiling Bridge", debug_info
        pass

import sys, pdb

class Policy(JitPolicy, AnnotatorPolicy):
    def __init__(self):
        JitPolicy.__init__(self, DebugIFace())

def jitpolicy(driver):
    return JitPolicy(jithookiface=DebugIFace())

def target(*args):
    import pixie.vm.rt as rt
    driver = args[0]
    driver.exe_name = "pixie-vm2"
    rt.__config__ = args[0].config


    print "ARG INFO: ", args


    return entry_point, None

import rpython.config.translationoption
print rpython.config.translationoption.get_combined_translation_config()

if __name__ == "__main__":
    #run_debug(sys.argv)
    entry_point([])
