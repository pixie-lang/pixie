from byteplay import *
from pprint import pprint
import dis as dis
import types
from effects import *


iname = 0
SELF_NAME = "__SELF__"
RET_NAME = "__RET__"
BUILDING_NAME = "__BUILDING__"
STATE_NAME = "_K_state"

class BytecodeRewriter(object):
    """
    Bytecode rewriter for assisting in performing inserts into the middle of a bytecode list.
    """
    def __init__(self, code):
        assert isinstance(code, list)
        self._code = code
        self._i = 0

    def set_position(self, i):
        self._i = i

    def reset(self):
        self.set_position(0)

    def insert(self, op, arg=None):
        self._code.insert(self._i, (op, arg))
        self._i += 1

    def next(self):
        self._i += 1
        return self

    def __getitem__(self, item):
        return self._code[self._i + item]

    def __setitem__(self, key, value):
        assert isinstance(value, tuple)
        self._code[self._i + key] = value

    def get_code(self):
        return self._code

    def __len__(self):
        return len(self._code)

    def inbounds(self):
        return 0 <= self._i < len(self)


def cps(f):
    """
    Transforms a function or method into a function that returns an effect. In essence this transform performs
    continuation passing style edits to the bytecode, creating immutable state machines for each step. There
    are many caveats to this approach, but if the principles are followed the approach works well, and results in
    RPYthon compliant code.

    The rules are stated as follows:


    * Calls to functions or methods that end with a single `_` are considered to be effect functions (functions that
    will either return Answer or an Effect). Thus at every call to such a function the transformer will create a
    continuation.
    * Generators/Iterators should be avoided. A single step of the function may be run many times, thus it is important
     to clone any mutable state.
    * The call stack is not persisted across continuations, so be sure that the stack position is 0 at every effect
    function call.

    For example:


        @cps
        def foo(x):
          r = invoke_(x)
          z = invoke_(r)
          return z


    Is fine, while the following is not:


        @cps
        def foo(x):
          return invoke_(invoke_(x))


    Since the outer `invoke_` will be loaded before the `inner_`.

    * Calls to effect functions that immediately return will be turned into tail calls, so prefer this style when
    possible:


        @cps
        def foo(x):
          return invoke_(x)

    * Currently (until this restriction is removed) effect calls that take anything but locals as arguments are not
    supported.


        @cps
        def foo(x):
          # works
          x = invoke_(something)
          # doesn't work
          x = invoke_(something._zing)

    * `break` and `continue` require the stack to operate, and as such are not supported
    * Since functions are RPython and internally function locals are converted class fields, locals can only have one
    type. Unlike RPython that supports locals with conflicting types as long as they are redefined between usages.



    """
    global iname
    c = Code.from_code(f.func_code)

    iname += 1
    cls_name = "_K_" + str(iname) + "_class"

    code = BytecodeRewriter(c.code)
    ret_points = []
    locals = set(f.func_code.co_varnames[:f.func_code.co_argcount])

    while code.inbounds():
        nm, arg = code[0]


        # Track locals we discover, this is why locals that escape loops must be declared before the loop starts
        if nm == STORE_FAST:
            locals.add(arg)

        # PyPy creates this bytecode, convert it so we can translate easier
        if nm == LOOKUP_METHOD:
            code[0] = (LOAD_ATTR, arg)

        # Convert this as well
        if nm == CALL_METHOD:
            code[0] = (CALL_FUNCTION, arg)

        # Not needed if we don't allow continue or break
        if nm == SETUP_LOOP:
            code[0] = (NOP, None)

        # ditto
        if nm == POP_BLOCK:
            code[0] = (NOP, None)

        # These require blocks, which require the stack, which we don't support
        if nm == BREAK_LOOP:
            raise AssertionError("Can't use break inside a CPS function")

        if nm == CONTINUE_LOOP:
            raise AssertionError("Can't use continue inside a CPS function")

        # Now we come to the good part
        if nm == CALL_METHOD or nm == CALL_FUNCTION:
            next_op, _ = code[1]


            # is the function we're calling an effect?
            op, arg = code[- (arg + 1)]
            if (op == LOAD_ATTR or op == LOAD_GLOBAL) and arg.endswith("_Ef"):
                final_fn = raise_Ef if arg == "raise_Ef" else handle

                # If the next opcode is a return, we can tailcall by simply returning the result directly, except
                # for calls to raise, those take a continuation, so we can't tailcall those
                if next_op == RETURN_VALUE and next_op != "raise_Ef":

                    code.next().next()
                    continue


                # are we calling raise_?
                if arg == "raise_Ef":
                    code[0] = (NOP, None)

                code.next()

                # Construct a new state object
                code.insert(STORE_FAST, RET_NAME)
                code.insert(LOAD_GLOBAL, cls_name)
                code.insert(CALL_FUNCTION, 0)
                code.insert(STORE_FAST, BUILDING_NAME)
                code.insert(LOAD_FAST, BUILDING_NAME)
                code.insert(LOAD_CONST, len(ret_points) + 1)  # The id of this state
                code.insert(LOAD_FAST, BUILDING_NAME)
                code.insert(STORE_ATTR, STATE_NAME)
                # Save the locals to the state machien
                for x in locals:
                    code.insert(LOAD_FAST, x)
                    code.insert(LOAD_FAST, BUILDING_NAME)
                    code.insert(STORE_ATTR, "_K_" + str(iname) + "_" + x)

                # Save the ret value and call handle or raise_
                code.insert(LOAD_FAST, BUILDING_NAME)
                code.insert(LOAD_CONST, final_fn)
                code.insert(LOAD_FAST, RET_NAME)
                code.insert(LOAD_FAST, BUILDING_NAME)
                code.insert(CALL_FUNCTION, 2)

                # Return
                code.insert(RETURN_VALUE, None)

                # Insert a label so we can jump to this state
                lbl = Label()
                ret_points.append(lbl)

                # Load the retvalue
                code.insert(lbl, None)
                code.insert(LOAD_FAST, RET_NAME)

                # Load locals
                for x in locals:
                    code.insert(LOAD_FAST, BUILDING_NAME)
                    code.insert(LOAD_ATTR, "_K_" + str(iname) + "_" + x)
                    code.insert(STORE_FAST, x)

                # We've just inserted a state transition in the middle of this function

                continue

        # Just a bare return, so wrap the result in an answer.
        if nm == RETURN_VALUE:
            code.insert(STORE_FAST, RET_NAME)
            code.insert(LOAD_CONST, answer)
            code.insert(LOAD_FAST, RET_NAME)
            code.insert(CALL_FUNCTION, 1)

        code.next()


    # Now construct a header to the function that sets up all the state we need
    # Load the locals for the first state (state 0)
    code.reset()
    for x in f.func_code.co_varnames[:f.func_code.co_argcount]:
        code.insert(LOAD_FAST, BUILDING_NAME)
        code.insert(LOAD_ATTR, "_K_" + str(iname) + "_" +  x)
        code.insert(STORE_FAST, x)

    # Build a jump table for the states
    state_idx = 1
    for lbl in ret_points:
        code.reset()
        code.insert(LOAD_FAST, BUILDING_NAME)
        code.insert(LOAD_ATTR, STATE_NAME)
        code.insert(LOAD_CONST, state_idx)
        code.insert(COMPARE_OP, "==")
        exit_lbl = Label()
        code.insert(POP_JUMP_IF_FALSE, exit_lbl)
        code.insert(JUMP_ABSOLUTE, lbl)
        code.insert(exit_lbl, None)

        state_idx += 1


    # Construct a code object and a class
    c = Code(code=code.get_code(), freevars=[], args=[BUILDING_NAME, RET_NAME],
             varargs=False, varkwargs=False, newlocals=True, name=f.func_code.co_name,
             filename=f.func_code.co_filename, firstlineno=f.func_code.co_firstlineno,
             docstring=f.func_code.__doc__)

    try:
        new_func = types.FunctionType(c.to_code(), f.func_globals, "step")
    except:
        print f.func_code.co_name
        pprint(code.get_code())
        raise

    dis.dis(new_func)

    f.func_globals[cls_name] = type(cls_name, (Continuation,), {"step": new_func, "_immutable_": True})


    # Now we need a constructor function for the first state of the state machine
    code = [(LOAD_GLOBAL, cls_name),
            (CALL_FUNCTION, 0),
            (STORE_FAST, BUILDING_NAME),
        (LOAD_CONST, 0),
        (LOAD_FAST, BUILDING_NAME),
        (STORE_ATTR, STATE_NAME)]

    # Save args to the state machine
    for x in range(f.func_code.co_argcount):
        code.append((LOAD_FAST, f.func_code.co_varnames[x]))
        code.append((LOAD_FAST, BUILDING_NAME))
        code.append((STORE_ATTR, "_K_" + str(iname) + "_" +  f.func_code.co_varnames[x]))

    # Call the constructed state machine
    code.append((LOAD_FAST, BUILDING_NAME))
    code.append((LOAD_ATTR, "step"))
    code.append((LOAD_CONST, None))
    code.append((CALL_FUNCTION, 1))

    code.append((RETURN_VALUE, None))

    # Build and return the function
    c = Code(code=code, freevars=[], args=f.func_code.co_varnames[:f.func_code.co_argcount],
             varargs=False, varkwargs=False, newlocals=True, name=f.func_code.co_name,
             filename=f.func_code.co_filename, firstlineno=f.func_code.co_firstlineno,
             docstring=f.func_code.__doc__)
    f.func_code = c.to_code()

    return f

