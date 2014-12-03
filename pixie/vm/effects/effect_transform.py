from byteplay import *
from pixie.vm.effects.effects import Continuation, handle, answer_k
from rpython.translator.translator import TranslationContext
from rpython.translator.unsimplify import insert_empty_startblock, split_block
from rpython.flowspace.model import Variable, Constant
from rpython.flowspace.operation import GetAttr
from rpython.flowspace.flowcontext import FlowContext, const
from pprint import pprint
import types
import dis
from pixie.vm.effects.effects import Object

"""
Why write our own bytcode transformer when we can leverage PyPy's. This code would replace the existing transformer, and
would work the following way: a) we'd parse a function using RPython's translator. b) we walk the graph splitting blocks
on effect functions, and tracking the new links. c) we stitch the function back together, this time with state machine
saving, after each effect call.
"""


effect_links = set()

__BUILDER_NAME__ = "__BUILDING__"
__RET__ = "__RET__"

global_idx = 0

class UserK(Continuation):
    _immutable_ = True
    def _step(self, x):
        try:
            return self._inner_step(x)
        except:
            #dis.dis(self._inner_step)
            raise

def sort_blocks(code):
    block_line_no = -2
    block_contents = []
    blocks = []
    for op, arg in code:
        if op == SetLineno:
            if block_line_no == -1:
                block_line_no = arg

            block_contents.append((op, arg))
        elif op == "SPLIT":
            blocks.append((block_line_no, block_contents))
            block_contents = []
            block_line_no = -1
        else:
            block_contents.append((op, arg))

    blocks.append((block_line_no, block_contents))


    blocks = sorted(blocks, key=lambda x: x[0])

    last_idx = -1
    for _, block in blocks:
        for op, arg in block:
            if op is SetLineno:
                if arg <= last_idx:
                    continue
                else:
                    last_idx = arg
            yield op, arg

class CPSTransformer(object):
    def __init__(self):
        global global_idx
        global_idx += 1
        self._global_idx = global_idx
        self._block_labels = {}
        self._processed_blocks = set()
        self._remaining_blocks = []

    def find_setters(self, var):
        for block in self._graph.iterblocks():
            for op in block.operations:
                if op.result is var:
                    yield op
                    return

        for block in self._graph.iterblocks():
            if var in block.inputargs:
                idx = block.inputargs.index(var)
                for link in self._graph.iterlinks():
                    if link.target is block:
                        yield link.args[idx]

    def is_effect(self, var):
        for arg in self.find_setters(var):
            name = None
            if isinstance(arg, GetAttr):
                name = arg.args[1].value
            elif isinstance(arg, Constant) and isinstance(arg.value, Global):
                name = arg.value.name
            elif isinstance(arg, Constant):
                name = getattr(arg.value, "__name__", None)
            if name is not None:
                if name.endswith("_Ef"):
                    return True
        return False

    def init_lineno(self, linenotab):
        self._byte_offsets = map(ord, linenotab[0::2])
        self._line_offsets = map(ord, linenotab[1::2])

    def get_line_no(self, offset):
        line = self._fn.func_code.co_firstlineno
        byte = 0
        idx = 0
        while idx < len(self._byte_offsets) and byte + self._byte_offsets[idx] <= offset:
            byte += self._byte_offsets[idx]
            line += self._line_offsets[idx]
            idx += 1
        return line

    def scan_fn(self, fn):
        self._fn = fn
        self.init_lineno(fn.func_code.co_lnotab)
        self._effect_links = {}
        ctx = TranslationContext()
        graph = ctx.buildflowgraph(fn)
        self._graph = graph

        for block in list(graph.iterblocks()):
            for index in range(len(block.operations)-1, -1, -1):
                hlop = block.operations[index]
                if hlop.opname == "simple_call":
                    is_xform = False
                    if isinstance(hlop.args[0], Variable):
                        is_xform = self.is_effect(hlop.args[0])

                    elif isinstance(hlop.args[0], Constant):
                        fn = hlop.args[0].value
                        if getattr(fn, "_is_effect", None):
                            is_xform = True
                        elif isinstance(fn, Global):
                            if fn.name.endswith("_Ef"):
                                is_xform = True
                        elif fn.__name__.endswith("_Ef"):
                            is_xform = True

                    if is_xform:
                        if index + 1 == len(block.operations):
                            assert len(block.exits) == 1
                            self._effect_links[block.exits[0]] = len(self._effect_links)
                        else:
                            newlink = split_block(None, block, index + 1)
                            self._effect_links[newlink] = len(self._effect_links)

                    pass

    def get_link_klass_name(self, link):
        return self._fn.__name__ + "_State_" + str(self._effect_links[link]) + "_step_" + str(global_idx)

    def emit_from(self, block, link=None):
        self._remaining_blocks = []
        self._processed_blocks = set()
        self._block_labels = {}

        start_label = Label()
        yield JUMP_ABSOLUTE, start_label
        yield "SPLIT", None
        yield start_label, None

        preamble = True
        while True:
            for op in self.emit_block(block, link=link, with_preamble=preamble):
                yield op

            preamble=False
            if not self._remaining_blocks:
                break

            block = self._remaining_blocks.pop()
            self._processed_blocks.add(block)

            yield "SPLIT", None

            yield self._block_labels[block], None





    def emit_block(self, block, link=None, with_preamble=False):
        from pixie.vm.effects.effects import Answer, Continuation, handle

        if block is self._graph.returnblock:
            assert len(block.inputargs) == 1
            assert len(block.operations) == 0
            yield LOAD_CONST, Answer
            yield LOAD_FAST, block.inputargs[0].name
            yield CALL_FUNCTION, 1
            yield RETURN_VALUE, None
            return

        if with_preamble:

            if block is self._graph.startblock:
                for x in range(len(block.inputargs)):
                    yield LOAD_FAST, self._fn.func_code.co_varnames[x]
                    yield STORE_FAST, block.inputargs[x].name
            else:
                for x in range(len(block.inputargs)):
                    if link is not None and link.args[x] is link.prevblock.operations[-1].result:
                        yield LOAD_FAST, __RET__
                    else:
                        yield LOAD_FAST, __BUILDER_NAME__
                        yield LOAD_ATTR, block.inputargs[x].name
                    yield STORE_FAST, block.inputargs[x].name

                #if link is not None and link.prevblock.operations[-1].result in link.args:
                #    yield LOAD_FAST, __RET__
                #    yield STORE_FAST, block.inputargs[-1].name

        for hlop in block.operations:
            mthd = getattr(OpEmitter, hlop.opname)
            yield SetLineno, self.get_line_no(hlop.offset)
            if not getattr(mthd, "_skip_all", None):
                for arg in range(len(hlop.args) - getattr(mthd, "_skip_last", 0)):
                    for op in OpEmitter.emit_arg(hlop.args[arg]):
                        yield op
            for op in mthd(hlop):
                yield op
            yield STORE_FAST, hlop.result.name

        for link in block.exits:
            if link not in self._effect_links:
                if link.target not in self._block_labels:
                    self._block_labels[link.target] = Label()
                if link.target not in self._processed_blocks:
                    self._remaining_blocks.append(link.target)

        if len(block.exits) == 1:
            link = block.exits[0]
            for x in self.emit_link(link):
                yield x
        elif block is self._graph.exceptblock:
            yield LOAD_FAST, block.inputargs[1].name
            yield LOAD_FAST, block.inputargs[0].name
            yield RAISE_VARARGS, 2

        else:
            assert len(block.exits) == 2
            other_block = Label()
            if isinstance(block.exitswitch, Variable):
                yield LOAD_FAST, block.exitswitch.name
            else:
                yield LOAD_CONST, block.exitswitch.value
            yield POP_JUMP_IF_TRUE, other_block

            for op in self.emit_link(block.exits[0]):
                yield op

            yield other_block, None

            for op in self.emit_link(block.exits[1]):
                yield op



    def emit_link(self, link):
        for op in self.emit_effect_link(link) if link in self._effect_links else self.emit_jump_link(link):
            yield op

    def emit_effect_link(self, link):
        from pixie.vm.effects.effects import handle
        if link.target is self._graph.returnblock:
            assert len(link.args) == 1
            for op in OpEmitter.emit_arg(link.args[0]):
                yield op
            yield RETURN_VALUE, None
            return

        yield LOAD_CONST, handle
        yield LOAD_FAST, link.prevblock.operations[-1].result.name

        yield LOAD_GLOBAL, self.get_link_klass_name(link)
        yield CALL_FUNCTION, 0
        yield STORE_FAST, __BUILDER_NAME__
        for x in range(len(link.args)):
            if link.prevblock.operations[-1].result is not link.args[x]:
                for o in OpEmitter.emit_arg(link.args[x]):
                    yield o
                yield LOAD_FAST, __BUILDER_NAME__
                yield STORE_ATTR, link.target.inputargs[x].name
        yield LOAD_FAST, __BUILDER_NAME__
        yield CALL_FUNCTION, 2
        yield RETURN_VALUE, None

    def emit_jump_link(self, link):
        for x in range(len(link.args)):
            for o in OpEmitter.emit_arg(link.args[x]):
                yield o
            yield STORE_FAST, link.target.inputargs[x].name
        yield JUMP_ABSOLUTE, self._block_labels[link.target]

    def emit_all(self):
        start = list(sort_blocks(self.emit_from(self._graph.startblock)))

        # Construct a code object and a class
        f = self._fn
        c = Code(code=start, freevars=[], args=f.func_code.co_varnames[:f.func_code.co_argcount],
                 varargs=False, varkwargs=False, newlocals=True, name=f.func_code.co_name,
                 filename=f.func_code.co_filename, firstlineno=f.func_code.co_firstlineno,
                 docstring=f.func_code.__doc__)

        try:
            new_func = types.FunctionType(c.to_code(), f.func_globals, f.__name__)
        except Exception as ex:
            print f.func_code.co_name
            pprint(start)
            raise ex

        for eff_link in self._effect_links:
            if eff_link.target is self._graph.returnblock:
                continue
            code = list(sort_blocks(self.emit_from(eff_link.target, eff_link)))

            f = self._fn
            c = Code(code=code, freevars=[], args=[__BUILDER_NAME__, __RET__],
                     varargs=False, varkwargs=False, newlocals=True, name=f.func_code.co_name,
                     filename=f.func_code.co_filename, firstlineno=f.func_code.co_firstlineno,
                     docstring=f.func_code.__doc__)

            try:
                method = types.FunctionType(c.to_code(), f.func_globals, f.__name__)
            except Exception as ex:
                print f.func_code.co_name
                pprint(code)
                raise

            klass_name = self.get_link_klass_name(eff_link)
            f.func_globals[klass_name] = type(klass_name, (UserK,), {"_inner_step": method, "_immutable_": True})

        return new_func



def skip_last(x):
    def with_f(f):
        f._skip_last = x
        return f
    return with_f

def skip_all(f):
    f._skip_all = True
    return f


class OpEmitter(object):

    @staticmethod
    def simple_call(hlop):
        yield CALL_FUNCTION, len(hlop.args) - 1

    @staticmethod
    def switch(hlop):
        assert False



    @staticmethod
    def add(hlop):
        yield BINARY_ADD, len(hlop.args) - 1


    @staticmethod
    def sub(hlop):
        yield BINARY_SUBTRACT, len(hlop.args) - 1

    @staticmethod
    def mul(hlop):
        yield BINARY_MULTIPLY, len(hlop.args) - 1

    @staticmethod
    def div(hlop):
        yield BINARY_DIVIDE, len(hlop.args) - 1

    @staticmethod
    def mod(hlop):
        yield BINARY_MODULO, len(hlop.args) - 1

    @staticmethod
    def lt(hlop):
        yield COMPARE_OP, "<"

    @staticmethod
    def gt(hlop):
        yield COMPARE_OP, ">"

    @staticmethod
    def le(hlop):
        yield COMPARE_OP, "<="

    @staticmethod
    def ge(hlop):
        yield COMPARE_OP, ">="

    @staticmethod
    def ne(hlop):
        yield COMPARE_OP, "!="

    @staticmethod
    @skip_all
    def contains(hlop):
        for x in OpEmitter.emit_arg(hlop.args[1]):
            yield x
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield COMPARE_OP, "in"

    @staticmethod
    def is_(hlop):
        yield COMPARE_OP, "is"

    @staticmethod
    def bool(hlop):
        yield NOP, None

    @staticmethod
    @skip_last(1)
    def str(hlop):
        yield LOAD_CONST, str
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield CALL_FUNCTION, 1

    @staticmethod
    @skip_last(1)
    def iter(hlop):
        yield LOAD_CONST, iter
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield CALL_FUNCTION, 1

    @staticmethod
    @skip_last(1)
    def next(hlop):
        yield LOAD_CONST, next
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield CALL_FUNCTION, 1

    @staticmethod
    @skip_last(1)
    def len(hlop):
        yield LOAD_GLOBAL, "len"
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield CALL_FUNCTION, 1

    @staticmethod
    @skip_last(1)
    def ord(hlop):
        yield LOAD_GLOBAL, "ord"
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield CALL_FUNCTION, 1

    @staticmethod
    @skip_last(1)
    def type(hlop):
        yield LOAD_CONST, type
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        yield CALL_FUNCTION, 1

    @staticmethod
    def emit_arg(arg):
        if isinstance(arg, Constant) and isinstance(arg.value, Global):
            return [(LOAD_GLOBAL, arg.value.name)]
        if isinstance(arg, Variable):
            return [(LOAD_FAST, arg.name)]
        if isinstance(arg, Constant):
            return [(LOAD_CONST, arg.value)]

        assert False
    @staticmethod
    @skip_last(1)
    def getattr(hlop):
        yield LOAD_ATTR, hlop.args[1].key[1]

    @staticmethod
    def eq(hlop):
        yield COMPARE_OP, "=="

    @staticmethod
    def inplace_add(hlop):
        return OpEmitter.add(hlop)

    @staticmethod
    def inplace_sub(hlop):
        return OpEmitter.sub(hlop)

    @staticmethod
    def getitem(hlop):
        yield BINARY_SUBSCR, None

    @staticmethod
    def newdict(hlop):
        yield BUILD_MAP, len(hlop.args) / 2

    @staticmethod
    @skip_all
    def setitem(hlop):
        for x in OpEmitter.emit_arg(hlop.args[1]):
            yield x
        for x in OpEmitter.emit_arg(hlop.args[0]):
            yield x
        for x in OpEmitter.emit_arg(hlop.args[2]):
            yield x
        yield STORE_SUBSCR, None


class Global(object):
    def __init__(self, name):
        self.name = name

import __builtin__

def _find_global(self, w_globals, varname):
    try:
        value = w_globals.value[varname]
    except KeyError:
        # not in the globals, now look in the built-ins
        try:
            value = getattr(__builtin__, varname)
        except AttributeError:
            return const(Global(varname))
    return const(value)

def cps(f):
    # ugly hack to avoid forward declarations
    old_find_global = FlowContext.find_global

    try:
        FlowContext.find_global = _find_global

        xform = CPSTransformer()
        xform.scan_fn(f)
        a = xform.emit_all()

        return a
    except:
        dis.dis(f)
        raise
    finally:
        FlowContext.find_global = old_find_global
