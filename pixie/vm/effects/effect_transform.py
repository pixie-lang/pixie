from byteplay import *
from pixie.vm.effects.effects import Continuation, handle, answer_k
from rpython.translator.translator import TranslationContext
from rpython.translator.unsimplify import insert_empty_startblock, split_block
from rpython.flowspace.model import Variable, Constant
from rpython.flowspace.operation import GetAttr
from pprint import pprint
import types
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

class CPSTransformer(object):
    def __init__(self):
        self._block_labels = {}
        self._processed_blocks = set()
        self._remaining_blocks = []


    def scan_fn(self, fn):
        self._fn = fn
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
                        resolved = None
                        for j in block.operations:
                            if j.result == hlop.args[0]:
                                resolved = j
                                break
                        assert resolved, "Function crossed block bounaries"
                        if isinstance(resolved, GetAttr):
                            if resolved.args[1].value.endswith("_Ef"):
                                is_xform = True
                            pass

                    elif isinstance(hlop.args[0], Constant):
                        fn = hlop.args[0].value
                        if getattr(fn, "_is_effect", None):
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
        return "State_" + str(self._effect_links[link]) + "_step"

    def emit_from(self, block, link=None):
        self._remaining_blocks = []
        self._processed_blocks = set()
        self._block_labels = {}


        preamble = True
        while True:
            for op in self.emit_block(block, link=link, with_preamble=preamble):
                yield op

            preamble=False
            if not self._remaining_blocks:
                break

            block = self._remaining_blocks.pop()
            self._processed_blocks.add(block)
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
                for arg in block.inputargs:
                    if link is not None and arg is link.prevblock.operations[-1].result:
                        yield LOAD_FAST, __RET__
                    else:
                        yield LOAD_FAST, __BUILDER_NAME__
                        yield LOAD_ATTR, arg.name
                    yield STORE_FAST, arg.name

                if link is not None and link.prevblock.operations[-1].result in link.args:
                    yield LOAD_FAST, __RET__
                    yield STORE_FAST, block.inputargs[-1].name

        for hlop in block.operations:
            mthd = getattr(OpEmitter, hlop.opname)
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

        else:
            assert len(block.exits) == 2
            other_block = Label()
            yield LOAD_FAST, block.exitswitch.name
            yield POP_JUMP_IF_TRUE, other_block

            for op in self.emit_link(block.exits[0]):
                yield op

            yield other_block, None

            for op in self.emit_link(block.exits[1]):
                yield op


    def emit_link(self, link):
        for op in self.emit_effect_link(link)  if link in self._effect_links else self.emit_jump_link(link):
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
        start = list(self.emit_from(self._graph.startblock))

        # Construct a code object and a class
        f = self._fn
        c = Code(code=start, freevars=[], args=f.func_code.co_varnames[:f.func_code.co_argcount],
                 varargs=False, varkwargs=False, newlocals=True, name=f.func_code.co_name,
                 filename=f.func_code.co_filename, firstlineno=f.func_code.co_firstlineno,
                 docstring=f.func_code.__doc__)

        try:
            new_func = types.FunctionType(c.to_code(), f.func_globals, f.__name__)
        except:
            print f.func_code.co_name
            pprint(start)
            raise

        for eff_link in self._effect_links:
            if eff_link.target is self._graph.returnblock:
                continue
            code = list(self.emit_from(eff_link.target, eff_link))

            f = self._fn
            c = Code(code=code, freevars=[], args=[__BUILDER_NAME__, __RET__],
                     varargs=False, varkwargs=False, newlocals=True, name=f.func_code.co_name,
                     filename=f.func_code.co_filename, firstlineno=f.func_code.co_firstlineno,
                     docstring=f.func_code.__doc__)

            try:
                method = types.FunctionType(c.to_code(), f.func_globals, f.__name__)
            except:
                print f.func_code.co_name
                pprint(code)
                raise

            klass_name = self.get_link_klass_name(eff_link)
            f.func_globals[klass_name] = type(klass_name, (Continuation,), {"step": method, "_immutable_": True})

        return new_func



def skip_last(x):
    def with_f(f):
        f._skip_last = x
        return f
    return with_f


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
    def lt(hlop):
        yield COMPARE_OP, "<"

    @staticmethod
    def le(hlop):
        yield COMPARE_OP, "<="

    @staticmethod
    def is_(hlop):
        yield COMPARE_OP, "is"

    @staticmethod
    def bool(hlop):
        yield NOP, None

    @staticmethod
    def emit_arg(arg):
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


def cps(f):
    xform = CPSTransformer()
    xform.scan_fn(f)
    a = xform.emit_all()

    return a
