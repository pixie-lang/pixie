import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint
from rpython.rlib.jit import elidable, elidable_promote, promote


BYTECODES = ["LOAD_CONST",
             "ADD",
             "EQ",
             "INVOKE",
             "TAIL_CALL",
             "DUP_NTH",
             "RETURN",
             "COND_BR",
             "JMP",
             "CLOSED_OVER",
             "MAKE_CLOSURE",
             "SET_VAR",
             "POP",
             "DEREF_VAR",
             "INSTALL"]

for x in range(len(BYTECODES)):
    globals()[BYTECODES[x]] = r_uint(x)

class BaseCode(object.Object):
    __immutable_fields__ = ["_is_effect?"]
    def __init__(self):
        self._is_effect = False

    def set_is_effect(self, arg):
        self._is_effect = True if arg is true else False

    def is_effect(self):
        return self._is_effect

    def invoke(self, frame, argc):
        raise NotImplementedError()

    def tail_call(self, frame, argc):
        raise NotImplementedError()

    def get_consts(self):
        raise NotImplementedError()

    def get_bytecode(self):
        raise NotImplementedError()




class NativeFn(BaseCode):
    """Wrapper for a native function"""
    _type = object.Type("NativeFn")

    def __init__(self):
        BaseCode.__init__(self)

    def type(self):
        return NativeFn._type

    def invoke(self, frame, argc):
        result = self.inner_invoke(frame, r_uint(argc))
        frame.pop()
        frame.push(result)
        return frame

    def inner_invoke(self, frame, argc):
        raise NotImplementedError()

    def tail_call(self, frame, argc):
        self.invoke(frame, argc)
        return frame


class StackSlice(BaseCode):
    """A subsection of a stack created by a call to an effect,
       this is handed to the handler and can be called. On being invoked, the slice will
       be spliced back into the stack and execution will resume."""
    _type = object.Type("StackSlice")

    def type(self):
        return StackSlice._type

    def __init__(self, bottom_frame, top_frame):
        BaseCode.__init__(self)
        self._bottom_frame = bottom_frame
        self._top_frame = top_frame


    def clone_slice(self):
        new_top = self._top_frame.clone()
        frame = new_top
        prev_frame = None
        while frame.prev_frame is not None:
            prev_frame = frame
            frame = frame.prev_frame
            frame.clone()
            prev_frame.prev_frame = frame

        return (frame, new_top)

    def tail_call(self, frame, argc):
        assert argc == 2

        arg = frame.pop()
        slice = frame.pop()

        (bottom, new_frame) = self.clone_slice()

        bottom.prev_frame = frame
        frame = new_frame

        frame.push(arg)

        return frame

    def invoke(self, frame, argc):
        assert argc == 2

        arg = frame.pop()
        slice = frame.pop()

        (bottom, new_frame) = self.clone_slice()
        bottom.prev_frame = frame
        frame = new_frame

        frame.push(arg)

        return frame





class Code(BaseCode):
    """Interpreted code block. Contains consts and """
    _type = object.Type("Code")
    __immutable_fields__ = ["_consts[*]", "_bytecode"]

    def type(self):
        return Code._type

    def __init__(self, name, bytecode, consts):
        BaseCode.__init__(self)
        self._bytecode = bytecode
        self._consts = consts
        self._name = name

    def invoke(self, frame, argc):
        args = frame.pop_n(argc)


        if self._is_effect:
            handler = args[-2]

            (frame, bottom_of_slice, top_of_slice) = frame.slice_stack(handler)
            frame = frame.make_frame(self)

            frame.push_n(args, argc)


            frame.push(StackSlice(bottom_of_slice, top_of_slice))
            argc += 1
        else:
            frame = frame.make_frame(self)
            frame.push_n(args, argc)


        frame.code_obj = self
        frame.argc = argc
        frame.consts = self._consts
        frame.bc = self._bytecode
        frame.ip = r_uint(0)

        return frame

    def tail_call(self, frame, argc):
        args = frame.pop_n(argc)

        if self._is_effect:
            handler = args[-2]

            (frame, bottom_of_slice, top_of_slice) = frame.slice_stack(handler)

            frame.push_n(args, argc)


            frame.push(StackSlice(bottom_of_slice, top_of_slice))
            argc += 1

        else:
            # remove current frame args
            if frame.prev_frame is not None:
                frame = frame.prev_frame
            else:
                frame = frame.new(self)

            # replace args
            frame.push_n(args, argc)


        # reset frame to our state
        frame.code_obj = self
        frame.argc = argc
        frame.consts = self._consts
        frame.bc = self._bytecode
        frame.ip = r_uint(0)

        return frame

    def get_consts(self):
        return self._consts

    def get_bytecode(self):
        return self._bytecode

class Closure(BaseCode):
    _type = object.Type("Closure")
    __immutable_fields__ = ["_closed_overs[*]", "_code"]
    def type(self):
        return Closure._type

    def __init__(self, code, closed_overs):
        BaseCode.__init__(self)
        self._code = code
        self._closed_overs = closed_overs

    def invoke(self, frame, argc):
        frame = self._code.invoke(frame, argc)
        frame.code_obj = self
        return frame

    def tail_call(self, frame, argc):
        frame = self._code.tail_call(frame, argc)
        frame.code_obj = self
        return frame

    def get_closed_over(self, idx):
        return self._closed_overs[idx]

    def get_consts(self):
        return self._code.get_consts()

    def get_bytecode(self):
        return self._code.get_bytecode()

class Var(object.Object):
    _type = object.Type("Var")
    _immutable_fields_ = ["_rev?"]

    def type(self):
        return Var._type

    def __init__(self, name):
        self._name = name
        self._rev = 0

    def set_root(self, o):
        self._rev += 1
        self._root = o
        return self

    @elidable
    def get_root(self, rev):
        return self._root


    def deref(self):
        rev = promote(self._rev)
        return self.get_root(rev)


class VarRegistry(__builtins__.object):
    def __init__(self):
        self._registry = {}

    def intern_or_make(self, name):
        assert isinstance(name, str)
        v = self._registry.get(name, None)
        if v is None:
            v = Var(name).set_root(nil)
            self._registry[name] = v
        return v

_var_registry = VarRegistry()

def intern_var(name):
    return _var_registry.intern_or_make(name)



def as_var(name):
    var = intern_var(name)
    def with_fn(fn):
        inst = type("W"+fn.__name__, (NativeFn,), {"inner_invoke": fn})()
        var.set_root(inst)
        return inst
    return with_fn
