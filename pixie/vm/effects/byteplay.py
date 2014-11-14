# byteplay - Python bytecode assembler/disassembler.
# Copyright (C) 2006-2010 Noam Yorav-Raphael
# Homepage: http://code.google.com/p/byteplay
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

# Many thanks to Greg X for adding support for Python 2.6 and 2.7!

__version__ = '0.2'

__all__ = ['opmap', 'opname', 'opcodes',
           'cmp_op', 'hasarg', 'hasname', 'hasjrel', 'hasjabs',
           'hasjump', 'haslocal', 'hascompare', 'hasfree', 'hascode',
           'hasflow', 'getse',
           'Opcode', 'SetLineno', 'Label', 'isopcode', 'Code',
           'CodeList', 'printcodelist']

import opcode
from dis import findlabels
import types
from array import array
import operator
import itertools
import sys
import warnings
from cStringIO import StringIO

######################################################################
# Define opcodes and information about them

python_version = '.'.join(str(x) for x in sys.version_info[:2])
if python_version not in ('2.4', '2.5', '2.6', '2.7'):
    warnings.warn("byteplay doesn't support Python version "+python_version)

class Opcode(int):
    """An int which represents an opcode - has a nicer repr."""
    def __repr__(self):
        return opname[self]
    __str__ = __repr__

class CodeList(list):
    """A list for storing opcode tuples - has a nicer __str__."""
    def __str__(self):
        f = StringIO()
        printcodelist(self, f)
        return f.getvalue()

opmap = dict((name.replace('+', '_'), Opcode(code))
             for name, code in opcode.opmap.iteritems()
             if name != 'EXTENDED_ARG')
opname = dict((code, name) for name, code in opmap.iteritems())
opcodes = set(opname)

def globalize_opcodes():
    for name, code in opmap.iteritems():
        globals()[name] = code
        __all__.append(name)
globalize_opcodes()

cmp_op = opcode.cmp_op

hasarg = set(x for x in opcodes if x >= opcode.HAVE_ARGUMENT)
hasconst = set(Opcode(x) for x in opcode.hasconst)
hasname = set(Opcode(x) for x in opcode.hasname)
hasjrel = set(Opcode(x) for x in opcode.hasjrel)
hasjabs = set(Opcode(x) for x in opcode.hasjabs)
hasjump = hasjrel.union(hasjabs)
haslocal = set(Opcode(x) for x in opcode.haslocal)
hascompare = set(Opcode(x) for x in opcode.hascompare)
hasfree = set(Opcode(x) for x in opcode.hasfree)
hascode = set([MAKE_FUNCTION, MAKE_CLOSURE])

class _se:
    """Quick way of defining static stack effects of opcodes"""
    # Taken from assembler.py by Phillip J. Eby
    NOP       = 0,0

    POP_TOP   = 1,0
    ROT_TWO   = 2,2
    ROT_THREE = 3,3
    ROT_FOUR  = 4,4
    DUP_TOP   = 1,2

    UNARY_POSITIVE = UNARY_NEGATIVE = UNARY_NOT = UNARY_CONVERT = \
        UNARY_INVERT = GET_ITER = LOAD_ATTR = 1,1

    IMPORT_FROM = 1,2

    BINARY_POWER = BINARY_MULTIPLY = BINARY_DIVIDE = BINARY_FLOOR_DIVIDE = \
        BINARY_TRUE_DIVIDE = BINARY_MODULO = BINARY_ADD = BINARY_SUBTRACT = \
        BINARY_SUBSCR = BINARY_LSHIFT = BINARY_RSHIFT = BINARY_AND = \
        BINARY_XOR = BINARY_OR = COMPARE_OP = 2,1

    INPLACE_POWER = INPLACE_MULTIPLY = INPLACE_DIVIDE = \
        INPLACE_FLOOR_DIVIDE = INPLACE_TRUE_DIVIDE = INPLACE_MODULO = \
        INPLACE_ADD = INPLACE_SUBTRACT = INPLACE_LSHIFT = INPLACE_RSHIFT = \
        INPLACE_AND = INPLACE_XOR = INPLACE_OR = 2,1

    SLICE_0, SLICE_1, SLICE_2, SLICE_3 = \
        (1,1),(2,1),(2,1),(3,1)
    STORE_SLICE_0, STORE_SLICE_1, STORE_SLICE_2, STORE_SLICE_3 = \
        (2,0),(3,0),(3,0),(4,0)
    DELETE_SLICE_0, DELETE_SLICE_1, DELETE_SLICE_2, DELETE_SLICE_3 = \
        (1,0),(2,0),(2,0),(3,0)

    STORE_SUBSCR = 3,0
    DELETE_SUBSCR = STORE_ATTR = 2,0
    DELETE_ATTR = STORE_DEREF = 1,0
    PRINT_NEWLINE = 0,0
    PRINT_EXPR = PRINT_ITEM = PRINT_NEWLINE_TO = IMPORT_STAR = 1,0
    STORE_NAME = STORE_GLOBAL = STORE_FAST = 1,0
    PRINT_ITEM_TO = 2,0

    LOAD_LOCALS = LOAD_CONST = LOAD_NAME = LOAD_GLOBAL = LOAD_FAST = \
        LOAD_CLOSURE = LOAD_DEREF = BUILD_MAP = 0,1

    DELETE_FAST = DELETE_GLOBAL = DELETE_NAME = 0,0

    EXEC_STMT = 3,0
    BUILD_CLASS = 3,1

    STORE_MAP = MAP_ADD = 2,0
    SET_ADD = 1,0

    if   python_version == '2.4':
      YIELD_VALUE = 1,0
      IMPORT_NAME = 1,1
      LIST_APPEND = 2,0
    elif python_version == '2.5':
      YIELD_VALUE = 1,1
      IMPORT_NAME = 2,1
      LIST_APPEND = 2,0
    elif python_version == '2.6':
      YIELD_VALUE = 1,1
      IMPORT_NAME = 2,1
      LIST_APPEND = 2,0
    elif python_version == '2.7':
      YIELD_VALUE = 1,1
      IMPORT_NAME = 2,1
      LIST_APPEND = 1,0


_se = dict((op, getattr(_se, opname[op]))
           for op in opcodes
           if hasattr(_se, opname[op]))

hasflow = opcodes - set(_se) - \
          set([CALL_FUNCTION, CALL_FUNCTION_VAR, CALL_FUNCTION_KW,
               CALL_FUNCTION_VAR_KW, BUILD_TUPLE, BUILD_LIST,
               UNPACK_SEQUENCE, BUILD_SLICE, DUP_TOPX,
               RAISE_VARARGS, MAKE_FUNCTION, MAKE_CLOSURE])
if python_version == '2.7':
  hasflow = hasflow - set([BUILD_SET])

def getse(op, arg=None):
    """Get the stack effect of an opcode, as a (pop, push) tuple.

    If an arg is needed and is not given, a ValueError is raised.
    If op isn't a simple opcode, that is, the flow doesn't always continue
    to the next opcode, a ValueError is raised.
    """
    try:
        return _se[op]
    except KeyError:
        # Continue to opcodes with an effect that depends on arg
        pass

    if arg is None:
        raise ValueError, "Opcode stack behaviour depends on arg"

    def get_func_tup(arg, nextra):
        if arg > 0xFFFF:
            raise ValueError, "Can only split a two-byte argument"
        return (nextra + 1 + (arg & 0xFF) + 2*((arg >> 8) & 0xFF),
                1)

    if op == CALL_FUNCTION:
        return get_func_tup(arg, 0)
    elif op == CALL_FUNCTION_VAR:
        return get_func_tup(arg, 1)
    elif op == CALL_FUNCTION_KW:
        return get_func_tup(arg, 1)
    elif op == CALL_FUNCTION_VAR_KW:
        return get_func_tup(arg, 2)

    elif op == BUILD_TUPLE:
        return arg, 1
    elif op == BUILD_LIST:
        return arg, 1
    elif python_version == '2.7' and op == BUILD_SET:
        return arg, 1
    elif op == UNPACK_SEQUENCE:
        return 1, arg
    elif op == BUILD_SLICE:
        return arg, 1
    elif op == DUP_TOPX:
        return arg, arg*2
    elif op == RAISE_VARARGS:
        return 1+arg, 1
    elif op == MAKE_FUNCTION:
        return 1+arg, 1
    elif op == MAKE_CLOSURE:
        if python_version == '2.4':
            raise ValueError, "The stack effect of MAKE_CLOSURE depends on TOS"
        else:
            return 2+arg, 1
    else:
        raise ValueError, "The opcode %r isn't recognized or has a special "\
              "flow control" % op

class SetLinenoType(object):
    def __repr__(self):
        return 'SetLineno'
SetLineno = SetLinenoType()

class Label(object):
    pass

def isopcode(obj):
    """Return whether obj is an opcode - not SetLineno or Label"""
    return obj is not SetLineno and not isinstance(obj, Label)

# Flags from code.h
CO_OPTIMIZED              = 0x0001      # use LOAD/STORE_FAST instead of _NAME
CO_NEWLOCALS              = 0x0002      # only cleared for module/exec code
CO_VARARGS                = 0x0004
CO_VARKEYWORDS            = 0x0008
CO_NESTED                 = 0x0010      # ???
CO_GENERATOR              = 0x0020
CO_NOFREE                 = 0x0040      # set if no free or cell vars
CO_GENERATOR_ALLOWED      = 0x1000      # unused
# The future flags are only used on code generation, so we can ignore them.
# (It does cause some warnings, though.)
CO_FUTURE_DIVISION        = 0x2000
CO_FUTURE_ABSOLUTE_IMPORT = 0x4000
CO_FUTURE_WITH_STATEMENT  = 0x8000


######################################################################
# Define the Code class

class Code(object):
    """An object which holds all the information which a Python code object
    holds, but in an easy-to-play-with representation.

    The attributes are:

    Affecting action
    ----------------
    code - list of 2-tuples: the code
    freevars - list of strings: the free vars of the code (those are names
               of variables created in outer functions and used in the function)
    args - list of strings: the arguments of the code
    varargs - boolean: Does args end with a '*args' argument
    varkwargs - boolean: Does args end with a '**kwargs' argument
    newlocals - boolean: Should a new local namespace be created.
                (True in functions, False for module and exec code)

    Not affecting action
    --------------------
    name - string: the name of the code (co_name)
    filename - string: the file name of the code (co_filename)
    firstlineno - int: the first line number (co_firstlineno)
    docstring - string or None: the docstring (the first item of co_consts,
                if it's str or unicode)

    code is a list of 2-tuples. The first item is an opcode, or SetLineno, or a
    Label instance. The second item is the argument, if applicable, or None.
    code can be a CodeList instance, which will produce nicer output when
    being printed.
    """
    def __init__(self, code, freevars, args, varargs, varkwargs, newlocals,
                 name, filename, firstlineno, docstring):
        self.code = code
        self.freevars = freevars
        self.args = args
        self.varargs = varargs
        self.varkwargs = varkwargs
        self.newlocals = newlocals
        self.name = name
        self.filename = filename
        self.firstlineno = firstlineno
        self.docstring = docstring

    @staticmethod
    def _findlinestarts(code):
        """Find the offsets in a byte code which are start of lines in the
        source.

        Generate pairs (offset, lineno) as described in Python/compile.c.

        This is a modified version of dis.findlinestarts, which allows multiple
        "line starts" with the same line number.
        """
        byte_increments = [ord(c) for c in code.co_lnotab[0::2]]
        line_increments = [ord(c) for c in code.co_lnotab[1::2]]

        lineno = code.co_firstlineno
        addr = 0
        for byte_incr, line_incr in zip(byte_increments, line_increments):
            if byte_incr:
                yield (addr, lineno)
                addr += byte_incr
            lineno += line_incr
        yield (addr, lineno)

    @classmethod
    def from_code(cls, co):
        """Disassemble a Python code object into a Code object."""
        co_code = co.co_code
        labels = dict((addr, Label()) for addr in findlabels(co_code))
        linestarts = dict(cls._findlinestarts(co))
        cellfree = co.co_cellvars + co.co_freevars

        code = CodeList()
        n = len(co_code)
        i = 0
        extended_arg = 0
        while i < n:
            op = Opcode(ord(co_code[i]))
            if i in labels:
                code.append((labels[i], None))
            if i in linestarts:
                code.append((SetLineno, linestarts[i]))
            i += 1
            if op in hascode:
                lastop, lastarg = code[-1]
                if lastop != LOAD_CONST:
                    raise ValueError, \
                          "%s should be preceded by LOAD_CONST code" % op
                code[-1] = (LOAD_CONST, Code.from_code(lastarg))
            if op not in hasarg:
                code.append((op, None))
            else:
                arg = ord(co_code[i]) + ord(co_code[i+1])*256 + extended_arg
                extended_arg = 0
                i += 2
                if op == opcode.EXTENDED_ARG:
                    extended_arg = arg << 16
                elif op in hasconst:
                    code.append((op, co.co_consts[arg]))
                elif op in hasname:
                    code.append((op, co.co_names[arg]))
                elif op in hasjabs:
                    code.append((op, labels[arg]))
                elif op in hasjrel:
                    code.append((op, labels[i + arg]))
                elif op in haslocal:
                    code.append((op, co.co_varnames[arg]))
                elif op in hascompare:
                    code.append((op, cmp_op[arg]))
                elif op in hasfree:
                    code.append((op, cellfree[arg]))
                else:
                    code.append((op, arg))

        varargs = bool(co.co_flags & CO_VARARGS)
        varkwargs = bool(co.co_flags & CO_VARKEYWORDS)
        newlocals = bool(co.co_flags & CO_NEWLOCALS)
        args = co.co_varnames[:co.co_argcount + varargs + varkwargs]
        if co.co_consts and isinstance(co.co_consts[0], basestring):
            docstring = co.co_consts[0]
        else:
            docstring = None
        return cls(code = code,
                   freevars = co.co_freevars,
                   args = args,
                   varargs = varargs,
                   varkwargs = varkwargs,
                   newlocals = newlocals,
                   name = co.co_name,
                   filename = co.co_filename,
                   firstlineno = co.co_firstlineno,
                   docstring = docstring,
                   )

    def __eq__(self, other):
        if (self.freevars != other.freevars or
            self.args != other.args or
            self.varargs != other.varargs or
            self.varkwargs != other.varkwargs or
            self.newlocals != other.newlocals or
            self.name != other.name or
            self.filename != other.filename or
            self.firstlineno != other.firstlineno or
            self.docstring != other.docstring or
            len(self.code) != len(other.code)
            ):
            return False

        # Compare code. This isn't trivial because labels should be matching,
        # not equal.
        labelmapping = {}
        for (op1, arg1), (op2, arg2) in itertools.izip(self.code, other.code):
            if isinstance(op1, Label):
                if labelmapping.setdefault(op1, op2) is not op2:
                    return False
            else:
                if op1 != op2:
                    return False
                if op1 in hasjump:
                    if labelmapping.setdefault(arg1, arg2) is not arg2:
                        return False
                elif op1 in hasarg:
                    if arg1 != arg2:
                        return False
        return True

    def _compute_flags(self):
        opcodes = set(op for op, arg in self.code if isopcode(op))

        optimized = (STORE_NAME not in opcodes and
                     LOAD_NAME not in opcodes and
                     DELETE_NAME not in opcodes)
        generator = (YIELD_VALUE in opcodes)
        nofree = not (opcodes.intersection(hasfree))

        flags = 0
        if optimized: flags |= CO_OPTIMIZED
        if self.newlocals: flags |= CO_NEWLOCALS
        if self.varargs: flags |= CO_VARARGS
        if self.varkwargs: flags |= CO_VARKEYWORDS
        if generator: flags |= CO_GENERATOR
        if nofree: flags |= CO_NOFREE
        return flags

    def _compute_stacksize(self):
        """Get a code list, compute its maximal stack usage."""
        # This is done by scanning the code, and computing for each opcode
        # the stack state at the opcode.
        code = self.code

        # A mapping from labels to their positions in the code list
        label_pos = dict((op, pos)
                         for pos, (op, arg) in enumerate(code)
                         if isinstance(op, Label))

        # sf_targets are the targets of SETUP_FINALLY opcodes. They are recorded
        # because they have special stack behaviour. If an exception was raised
        # in the block pushed by a SETUP_FINALLY opcode, the block is popped
        # and 3 objects are pushed. On return or continue, the block is popped
        # and 2 objects are pushed. If nothing happened, the block is popped by
        # a POP_BLOCK opcode and 1 object is pushed by a (LOAD_CONST, None)
        # operation.
        #
        # Our solution is to record the stack state of SETUP_FINALLY targets
        # as having 3 objects pushed, which is the maximum. However, to make
        # stack recording consistent, the get_next_stacks function will always
        # yield the stack state of the target as if 1 object was pushed, but
        # this will be corrected in the actual stack recording.

        sf_targets = set(label_pos[arg]
                         for op, arg in code
                         if op == SETUP_FINALLY)

        # What we compute - for each opcode, its stack state, as an n-tuple.
        # n is the number of blocks pushed. For each block, we record the number
        # of objects pushed.
        stacks = [None] * len(code)

        def get_next_stacks(pos, curstack):
            """Get a code position and the stack state before the operation
            was done, and yield pairs (pos, curstack) for the next positions
            to be explored - those are the positions to which you can get
            from the given (pos, curstack).

            If the given position was already explored, nothing will be yielded.
            """
            op, arg = code[pos]

            if isinstance(op, Label):
                # We should check if we already reached a node only if it is
                # a label.
                if pos in sf_targets:
                    curstack = curstack[:-1] + (curstack[-1] + 2,)
                if stacks[pos] is None:
                    stacks[pos] = curstack
                else:
                    if stacks[pos] != curstack:
                        raise ValueError, "Inconsistent code"
                    return

            def newstack(n):
                # Return a new stack, modified by adding n elements to the last
                # block
                if curstack[-1] + n < 0:
                    raise ValueError, "Popped a non-existing element"
                return curstack[:-1] + (curstack[-1]+n,)

            if not isopcode(op):
                # label or SetLineno - just continue to next line
                yield pos+1, curstack

            elif op in (STOP_CODE, RETURN_VALUE, RAISE_VARARGS):
                # No place in particular to continue to
                pass

            elif op == MAKE_CLOSURE and python_version == '2.4':
                # This is only relevant in Python 2.4 - in Python 2.5 the stack
                # effect of MAKE_CLOSURE can be calculated from the arg.
                # In Python 2.4, it depends on the number of freevars of TOS,
                # which should be a code object.
                if pos == 0:
                    raise ValueError, \
                          "MAKE_CLOSURE can't be the first opcode"
                lastop, lastarg = code[pos-1]
                if lastop != LOAD_CONST:
                    raise ValueError, \
                          "MAKE_CLOSURE should come after a LOAD_CONST op"
                try:
                    nextrapops = len(lastarg.freevars)
                except AttributeError:
                    try:
                        nextrapops = len(lastarg.co_freevars)
                    except AttributeError:
                        raise ValueError, \
                              "MAKE_CLOSURE preceding const should "\
                              "be a code or a Code object"

                yield pos+1, newstack(-arg-nextrapops)

            elif op not in hasflow:
                # Simple change of stack
                pop, push = getse(op, arg)
                yield pos+1, newstack(push - pop)

            elif op in (JUMP_FORWARD, JUMP_ABSOLUTE):
                # One possibility for a jump
                yield label_pos[arg], curstack

            elif python_version < '2.7' and op in (JUMP_IF_FALSE, JUMP_IF_TRUE):
                # Two possibilities for a jump
                yield label_pos[arg], curstack
                yield pos+1, curstack

            elif python_version >= '2.7' and op in (POP_JUMP_IF_FALSE, POP_JUMP_IF_TRUE):
                # Two possibilities for a jump
                yield label_pos[arg], newstack(-1)
                yield pos+1, newstack(-1)

            elif python_version >= '2.7' and op in (JUMP_IF_TRUE_OR_POP, JUMP_IF_FALSE_OR_POP):
                # Two possibilities for a jump
                yield label_pos[arg], curstack
                yield pos+1, newstack(-1)

            elif op == FOR_ITER:
                # FOR_ITER pushes next(TOS) on success, and pops TOS and jumps
                # on failure
                yield label_pos[arg], newstack(-1)
                yield pos+1, newstack(1)

            elif op == BREAK_LOOP:
                # BREAK_LOOP jumps to a place specified on block creation, so
                # it is ignored here
                pass

            elif op == CONTINUE_LOOP:
                # CONTINUE_LOOP jumps to the beginning of a loop which should
                # already ave been discovered, but we verify anyway.
                # It pops a block.
                if python_version == '2.6':
                  pos, stack = label_pos[arg], curstack[:-1]
                  if stacks[pos] != stack: #this could be a loop with a 'with' inside
                    yield pos, stack[:-1] + (stack[-1]-1,)
                  else:
                    yield pos, stack
                else:
                  yield label_pos[arg], curstack[:-1]

            elif op == SETUP_LOOP:
                # We continue with a new block.
                # On break, we jump to the label and return to current stack
                # state.
                yield label_pos[arg], curstack
                yield pos+1, curstack + (0,)

            elif op == SETUP_EXCEPT:
                # We continue with a new block.
                # On exception, we jump to the label with 3 extra objects on
                # stack
                yield label_pos[arg], newstack(3)
                yield pos+1, curstack + (0,)

            elif op == SETUP_FINALLY:
                # We continue with a new block.
                # On exception, we jump to the label with 3 extra objects on
                # stack, but to keep stack recording consistent, we behave as
                # if we add only 1 object. Extra 2 will be added to the actual
                # recording.
                yield label_pos[arg], newstack(1)
                yield pos+1, curstack + (0,)

            elif python_version == '2.7' and op == SETUP_WITH:
                yield label_pos[arg], curstack
                yield pos+1, newstack(-1) + (1,)

            elif op == POP_BLOCK:
                # Just pop the block
                yield pos+1, curstack[:-1]

            elif op == END_FINALLY:
                # Since stack recording of SETUP_FINALLY targets is of 3 pushed
                # objects (as when an exception is raised), we pop 3 objects.
                yield pos+1, newstack(-3)

            elif op == WITH_CLEANUP:
                # Since WITH_CLEANUP is always found after SETUP_FINALLY
                # targets, and the stack recording is that of a raised
                # exception, we can simply pop 1 object and let END_FINALLY
                # pop the remaining 3.
                if python_version == '2.7':
                  yield pos+1, newstack(2)
                else:
                  yield pos+1, newstack(-1)

            else:
                assert False, "Unhandled opcode: %r" % op


        # Now comes the calculation: open_positions holds positions which are
        # yet to be explored. In each step we take one open position, and
        # explore it by adding the positions to which you can get from it, to
        # open_positions. On the way, we update maxsize.
        # open_positions is a list of tuples: (pos, stack state)
        maxsize = 0
        open_positions = [(0, (0,))]
        while open_positions:
            pos, curstack = open_positions.pop()
            maxsize = max(maxsize, sum(curstack))
            open_positions.extend(get_next_stacks(pos, curstack))

        return maxsize

    def to_code(self):
        """Assemble a Python code object from a Code object."""
        co_argcount = len(self.args) - self.varargs - self.varkwargs
        co_stacksize = self._compute_stacksize()
        co_flags = self._compute_flags()

        co_consts = [self.docstring]
        co_names = []
        co_varnames = list(self.args)

        co_freevars = tuple(self.freevars)

        # We find all cellvars beforehand, for two reasons:
        # 1. We need the number of them to construct the numeric argument
        #    for ops in "hasfree".
        # 2. We need to put arguments which are cell vars in the beginning
        #    of co_cellvars
        cellvars = set(arg for op, arg in self.code
                       if isopcode(op) and op in hasfree
                       and arg not in co_freevars)
        co_cellvars = [x for x in self.args if x in cellvars]

        def index(seq, item, eq=operator.eq, can_append=True):
            """Find the index of item in a sequence and return it.
            If it is not found in the sequence, and can_append is True,
            it is appended to the sequence.

            eq is the equality operator to use.
            """
            for i, x in enumerate(seq):
                if eq(x, item):
                    return i
            else:
                if can_append:
                    seq.append(item)
                    return len(seq) - 1
                else:
                    raise IndexError, "Item not found"

        # List of tuples (pos, label) to be filled later
        jumps = []
        # A mapping from a label to its position
        label_pos = {}
        # Last SetLineno
        lastlineno = self.firstlineno
        lastlinepos = 0

        co_code = array('B')
        co_lnotab = array('B')
        for i, (op, arg) in enumerate(self.code):
            if isinstance(op, Label):
                label_pos[op] = len(co_code)

            elif op is SetLineno:
                incr_lineno = arg - lastlineno
                incr_pos = len(co_code) - lastlinepos
                lastlineno = arg
                lastlinepos = len(co_code)

                if incr_lineno == 0 and incr_pos == 0:
                    co_lnotab.append(0)
                    co_lnotab.append(0)
                else:
                    while incr_pos > 255:
                        co_lnotab.append(255)
                        co_lnotab.append(0)
                        incr_pos -= 255
                    while incr_lineno > 255:
                        co_lnotab.append(incr_pos)
                        co_lnotab.append(255)
                        incr_pos = 0
                        incr_lineno -= 255
                    if incr_pos or incr_lineno:
                        co_lnotab.append(incr_pos)
                        co_lnotab.append(incr_lineno)

            elif op == opcode.EXTENDED_ARG:
                raise ValueError, "EXTENDED_ARG not supported in Code objects"

            elif not op in hasarg:
                co_code.append(op)

            else:
                if op in hasconst:
                    if isinstance(arg, Code) and i < len(self.code)-1 and \
                       self.code[i+1][0] in hascode:
                        arg = arg.to_code()
                    arg = index(co_consts, arg, operator.is_)
                elif op in hasname:
                    arg = index(co_names, arg)
                elif op in hasjump:
                    # arg will be filled later
                    jumps.append((len(co_code), arg))
                    arg = 0
                elif op in haslocal:
                    arg = index(co_varnames, arg)
                elif op in hascompare:
                    arg = index(cmp_op, arg, can_append=False)
                elif op in hasfree:
                    try:
                        arg = index(co_freevars, arg, can_append=False) \
                              + len(cellvars)
                    except IndexError:
                        arg = index(co_cellvars, arg)
                else:
                    # arg is ok
                    pass

                if arg > 0xFFFF:
                    co_code.append(opcode.EXTENDED_ARG)
                    co_code.append((arg >> 16) & 0xFF)
                    co_code.append((arg >> 24) & 0xFF)
                co_code.append(op)
                co_code.append(arg & 0xFF)
                co_code.append((arg >> 8) & 0xFF)

        for pos, label in jumps:
            jump = label_pos[label]
            if co_code[pos] in hasjrel:
                jump -= pos+3
            if jump > 0xFFFF:
                raise NotImplementedError, "Extended jumps not implemented"
            co_code[pos+1] = jump & 0xFF
            co_code[pos+2] = (jump >> 8) & 0xFF

        co_code = co_code.tostring()
        co_lnotab = co_lnotab.tostring()

        co_consts = tuple(co_consts)
        co_names = tuple(co_names)
        co_varnames = tuple(co_varnames)
        co_nlocals = len(co_varnames)
        co_cellvars = tuple(co_cellvars)

        return types.CodeType(co_argcount, co_nlocals, co_stacksize, co_flags,
                              co_code, co_consts, co_names, co_varnames,
                              self.filename, self.name, self.firstlineno, co_lnotab,
                              co_freevars, co_cellvars)


def printcodelist(codelist, to=sys.stdout):
    """Get a code list. Print it nicely."""

    labeldict = {}
    pendinglabels = []
    for i, (op, arg) in enumerate(codelist):
        if isinstance(op, Label):
            pendinglabels.append(op)
        elif op is SetLineno:
            pass
        else:
            while pendinglabels:
                labeldict[pendinglabels.pop()] = i

    lineno = None
    islabel = False
    for i, (op, arg) in enumerate(codelist):
        if op is SetLineno:
            lineno = arg
            print >> to
            continue

        if isinstance(op, Label):
            islabel = True
            continue

        if lineno is None:
            linenostr = ''
        else:
            linenostr = str(lineno)
            lineno = None

        if islabel:
            islabelstr = '>>'
            islabel = False
        else:
            islabelstr = ''

        if op in hasconst:
            argstr = repr(arg)
        elif op in hasjump:
            try:
                argstr = 'to ' + str(labeldict[arg])
            except KeyError:
                argstr = repr(arg)
        elif op in hasarg:
            argstr = str(arg)
        else:
            argstr = ''

        print >> to, '%3s     %2s %4d %-20s %s' % (
            linenostr,
            islabelstr,
            i,
            op,
            argstr)

def recompile(filename):
    """Create a .pyc by disassembling the file and assembling it again, printing
    a message that the reassembled file was loaded."""
    # Most of the code here based on the compile.py module.
    import os
    import imp
    import marshal
    import struct

    f = open(filename, 'U')
    try:
        timestamp = long(os.fstat(f.fileno()).st_mtime)
    except AttributeError:
        timestamp = long(os.stat(filename).st_mtime)
    codestring = f.read()
    f.close()
    if codestring and codestring[-1] != '\n':
        codestring = codestring + '\n'
    try:
        codeobject = compile(codestring, filename, 'exec')
    except SyntaxError:
        print >> sys.stderr, "Skipping %s - syntax error." % filename
        return
    cod = Code.from_code(codeobject)
    message = "reassembled %r imported.\n" % filename
    cod.code[:0] = [ # __import__('sys').stderr.write(message)
        (LOAD_GLOBAL, '__import__'),
        (LOAD_CONST, 'sys'),
        (CALL_FUNCTION, 1),
        (LOAD_ATTR, 'stderr'),
        (LOAD_ATTR, 'write'),
        (LOAD_CONST, message),
        (CALL_FUNCTION, 1),
        (POP_TOP, None),
        ]
    codeobject2 = cod.to_code()
    fc = open(filename+'c', 'wb')
    fc.write('\0\0\0\0')
    fc.write(struct.pack('<l', timestamp))
    marshal.dump(codeobject2, fc)
    fc.flush()
    fc.seek(0, 0)
    fc.write(imp.get_magic())
    fc.close()

def recompile_all(path):
    """recursively recompile all .py files in the directory"""
    import os
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith('.py'):
                    filename = os.path.abspath(os.path.join(root, name))
                    print >> sys.stderr, filename
                    recompile(filename)
    else:
        filename = os.path.abspath(path)
        recompile(filename)

def main():
    import os
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        print """\
Usage: %s dir

Search recursively for *.py in the given directory, disassemble and assemble
them, adding a note when each file is imported.

Use it to test byteplay like this:
> byteplay.py Lib
> make test

Some FutureWarnings may be raised, but that's expected.

Tip: before doing this, check to see which tests fail even without reassembling
them...
""" % sys.argv[0]
        sys.exit(1)
    recompile_all(sys.argv[1])

if __name__ == '__main__':
    main()