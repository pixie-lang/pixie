from pixie.vm.effects.environment import run_with_state, default_env, run_thunk_with_state, make_default_env
from pixie.vm.effects.effect_transform import cps
from pixie.vm.primitives import nil
from pixie.vm.compiler import compile_Ef
from pixie.vm.ast import SyntaxThunk, Locals, syntax_thunk_Ef
from pixie.vm.reader import StringReader, read_Ef, PromptReader #, MetaDataReader
from pixie.vm.keyword import keyword
# from pixie.vm.interpreter import interpret

from pixie.vm.code import wrap_fn, NativeFn
# from pixie.vm.stacklet import with_stacklets
# import pixie.vm.stacklet as stacklet
# from pixie.vm.object import RuntimeException, WrappedException
from rpython.translator.platform import platform
# from pixie.vm.primitives import nil
# from pixie.vm.atom import Atom
# from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR

import sys
import os
import os.path as path
import rpython.rlib.rpath as rpath
import rpython.rlib.rpath as rposix
from rpython.rlib.objectmodel import we_are_translated
from rpython.jit.codewriter.policy import JitPolicy
from rpython.rlib.jit import JitHookInterface, Counters
from rpython.rlib.rfile import create_stdio
from rpython.annotator.policy import AnnotatorPolicy
import pixie.vm.stdlib as stdlib

class DebugIFace(JitHookInterface):
    def on_abort(self, reason, jitdriver, greenkey, greenkey_repr, logops, operations):
        print "Aborted Trace, reason: ", Counters.counter_names[reason], logops, greenkey_repr

import sys, pdb

class Policy(JitPolicy, AnnotatorPolicy):
    def __init__(self):
        JitPolicy.__init__(self, DebugIFace())

def jitpolicy(driver):
    return JitPolicy(jithookiface=DebugIFace())

#
# PROGRAM_ARGUMENTS = intern_var(u"pixie.stdlib", u"program-arguments")
# PROGRAM_ARGUMENTS.set_root(nil)
#
# LOAD_PATHS = intern_var(u"pixie.stdlib", u"load-paths")
# LOAD_PATHS.set_root(nil)
# load_path = Var(u"", u"internal-load-path")
#
# STAR_1 = intern_var(u"pixie.stdlib", u"*1")
# STAR_1.set_root(nil)
# STAR_2 = intern_var(u"pixie.stdlib", u"*2")
# STAR_2.set_root(nil)
# STAR_3 = intern_var(u"pixie.stdlib", u"*3")
# STAR_3.set_root(nil)
# STAR_E = intern_var(u"pixie.stdlib", u"*e")
# STAR_E.set_root(nil)
#

KW_EXIT_REPL = keyword(u"exit-repl")

def init():
    import pixie.vm.rt as rt
    globals()["rt"] = rt

class ReplFn(NativeFn):
    def __init__(self, args):
        self._argv = args

    @cps
    def invoke_Ef(self, args):

        s = rt.wrap("Pixie 0.1 - Interactive REPL")
        rt._print_Ef(s)
        s = rt.wrap("(" + platform.name + ", " + platform.cc + ")")
        rt._print_Ef(s)
        s = rt.wrap("----------------------------")
        rt._print_Ef(s)

        #with with_ns(u"user"):
        #    NS_VAR.deref().include_stdlib()

        #acc = vector.EMPTY
        #for x in self._argv:
        #    acc = rt.conj(acc, rt.wrap(x))
        #
        #PROGRAM_ARGUMENTS.set_root(acc)

        #rdr = MetaDataReader(PromptReader())
        rdr = PromptReader()

        #with with_ns(u"user"):
        while True:
            val = read_Ef(rdr, True)
            if val is KW_EXIT_REPL:
                return nil
            ast = compile_Ef(val)
            locals = Locals()
            val = syntax_thunk_Ef(ast, locals)
            sval = rt._str_Ef(val)
            rt._print_Ef(sval)

    def set_recent_vars(self, val):
        if rt.eq(val, STAR_1.deref()):
            return
        STAR_3.set_root(STAR_2.deref())
        STAR_2.set_root(STAR_1.deref())
        STAR_1.set_root(val)

    def set_error_var(self, ex):
        STAR_E.set_root(ex)

def entry_point(_):
    final = run_with_state(ReplFn([]), make_default_env())
    return 0


#
# class BatchModeFn(NativeFn):
#     def __init__(self, args):
#         self._file = args[0]
#         self._argv = args[1:]
#
#     def inner_invoke(self, args):
#         import pixie.vm.rt as rt
#         import pixie.vm.persistent_vector as vector
#
#         with with_ns(u"user"):
#             NS_VAR.deref().include_stdlib()
#
#         acc = vector.EMPTY
#         for x in self._argv:
#             acc = rt.conj(acc, rt.wrap(x))
#
#         PROGRAM_ARGUMENTS.set_root(acc)
#
#         with with_ns(u"user"):
#             try:
#                 f = None
#                 if self._file == '-':
#                     f, _, _ = create_stdio()
#                 else:
#                     if not path.isfile(self._file):
#                         print "Error: Cannot open '" + self._file + "'"
#                         os._exit(1)
#                     f = open(self._file)
#                 data = f.read()
#                 f.close()
#
#                 if data.startswith("#!"):
#                     newline_pos = data.find("\n")
#                     if newline_pos > 0:
#                         data = data[newline_pos:]
#
#                 rt.load_reader(StringReader(unicode(data)))
#             except WrappedException as ex:
#                 print "Error: ", ex._ex.__repr__()
#                 os._exit(1)
#
# class EvalFn(NativeFn):
#     def __init__(self, expr):
#         self._expr = expr
#
#     def inner_invoke(self, args):
#         import pixie.vm.rt as rt
#
#         with with_ns(u"user"):
#             NS_VAR.deref().include_stdlib()
#
#             interpret(compile(read(StringReader(unicode(self._expr)), True)))
#
# @wrap_fn
# def run_load_stdlib():
#     import pixie.vm.compiler as compiler
#     import pixie.vm.reader as reader
#     f = open(rpath.rjoin(str(load_path.deref()._str), "pixie/stdlib.pxi"))
#     data = f.read()
#     f.close()
#     rdr = reader.MetaDataReader(reader.StringReader(unicode(data)), u"pixie/stdlib.pixie")
#     result = nil
#
#     if not we_are_translated():
#         print "Loading stdlib while interpreted, this will take some time..."
#
#     with compiler.with_ns(u"pixie.stdlib"):
#         while True:
#             if not we_are_translated():
#                 sys.stdout.write(".")
#                 sys.stdout.flush()
#             form = reader.read(rdr, False)
#             if form is reader.eof:
#                 break
#             result = compiler.compile(form).invoke([])
#
#     if not we_are_translated():
#         print "done"
#
# def load_stdlib():
#
#
#
#
#
#
#
#     stacklet.with_stacklets(run_load_stdlib)
#
# def entry_point(args):
#     interactive = True
#     script_args = []
#
#     init_load_path(args[0])
#     load_stdlib()
#     add_to_load_paths(".")
#
#     i = 1
#     while i < len(args):
#         arg = args[i]
#
#         if arg.startswith('-') and arg != '-':
#             if arg == '-v' or arg == '--version':
#                 print "Pixie 0.1"
#                 return 0
#             elif arg == '-h' or arg == '--help':
#                 print args[0] + " [<options>] [<file>]"
#                 print "  -h, --help             print this help"
#                 print "  -v, --version          print the version number"
#                 print "  -e, --eval=<expr>      evaluate the given expression"
#                 print "  -l, --load-path=<path> add <path> to pixie.stdlib/load-paths"
#                 return 0
#             elif arg == '-e' or arg == '--eval':
#                 i += 1
#                 if i < len(args):
#                     expr = args[i]
#                     with_stacklets(EvalFn(expr))
#                     return 0
#                 else:
#                     print "Expected argument for " + arg
#                     return 1
#             elif arg == '-l' or arg == '--load-path':
#                 i += 1
#                 if i < len(args):
#                     path = args[i]
#                     add_to_load_paths(path)
#                 else:
#                     print "Expected argument for " + arg
#                     return 1
#             else:
#                 print "Unknown option " + arg
#                 return 1
#         else:
#             interactive = False
#             script_args = args[i:]
#             break
#
#         i += 1
#
#     if interactive:
#         with_stacklets(ReplFn(args))
#     else:
#         with_stacklets(BatchModeFn(script_args))
#
#     return 0
#
# def add_to_load_paths(path):
#     rt.reset_BANG_(LOAD_PATHS.deref(), rt.conj(rt.deref(LOAD_PATHS.deref()), rt.wrap(path)))
#
# def init_load_path(self_path):
#     if not path.isfile(self_path):
#         self_path = find_in_path(self_path)
#         assert self_path is not None
#     if path.islink(self_path):
#         self_path = os.readlink(self_path)
#     self_path = dirname(rpath.rabspath(self_path))
#
#     # runtime is not loaded yet, so we have to do it manually
#     LOAD_PATHS.set_root(Atom(EMPTY_VECTOR.conj(rt.wrap(self_path))))
#     # just for run_load_stdlib (global variables can't be assigned to)
#     load_path.set_root(rt.wrap(self_path))
#
# def dirname(path):
#     return rpath.sep.join(path.split(rpath.sep)[0:-1])
#
# def find_in_path(exe_name):
#     paths = os.environ.get('PATH')
#     paths = paths.split(path.pathsep)
#     for p in paths:
#         exe_path = path.join(p, exe_name)
#         if path.isfile(exe_path):
#             return exe_path
#     return None

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
#stacklet.global_state = stacklet.GlobalState()

def target(*args):
    init()
    driver = args[0]
    driver.exe_name = "pixie-vm"
    rt.__config__ = args[0].config




    return entry_point, None

import rpython.config.translationoption
print rpython.config.translationoption.get_combined_translation_config()

if __name__ == "__main__":
    #entry_point()
    run_debug(sys.argv)
