import loki_vm.vm.object as object
from loki_vm.vm.primitives import nil, true, false
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

    @elidable
    def get_consts(self):
        raise NotImplementedError()

    @elidable
    def get_bytecode(self):
        raise NotImplementedError()




class NativeFn(BaseCode):
    _type = object.Type("NativeFn")

    def __init__(self):
        BaseCode.__init__(self)

    def type(self):
        return NativeFn._type

    def invoke(self, frame, argc):
        args = [None] * (argc - 1)
        for x in range(argc - 2, -1, -1):
            args[x] = frame.pop()

        frame.pop()
        frame.push(self.inner_invoke(args))

    def inner_invoke(self):
        raise NotImplementedError()

    def tail_call(self, frame, argc):
        self.invoke(frame, argc)


class StackSlice(BaseCode):
    _type = object.Type("StackSlice")

    def type(self):
        return StackSlice._type

    def __init__(self, slice):
        BaseCode.__init__(self)
        self._slice = slice

    def tail_call(self, frame, argc):
        assert argc == 2

        arg = frame.pop()
        slice = frame.pop()

        frame.pop_args()

        for x in range(len(self._slice)):
            frame.push(self._slice[x])

        marker = frame.pop()
        marker.unpack(frame)
        frame.push(arg)





class Code(BaseCode):
    _type = object.Type("Code")
    _immutable_fields_ = ["_consts", "_bytecode"]

    def type(self):
        return Code._type

    def __init__(self, bytecode, consts):
        BaseCode.__init__(self)
        self._bytecode = bytecode
        self._consts = consts

    def invoke(self, frame, argc):
        if self._is_effect:
            pass
        args = [None] * argc
        for x in range(argc):
            args[x] = frame.pop()

        f = frame.pack_state()

        frame.push(f)

        for x in range(argc - 1, -1, -1):
            frame.push(args[x])

        frame.code_obj = self
        frame.argc = argc
        frame.consts = self._consts
        frame.bc = self._bytecode
        frame.ip = 0

    def tail_call(self, frame, argc):
        args = [None] * argc

        # get args
        for x in range(argc):
            args[x] = frame.pop()

        if self._is_effect:
            handler = args[-2]
            frame.push(frame.pack_state())
            slice = frame.slice_stack(handler)

            for x in range(argc -1, -1, -1):
                frame.push(args[x])

            frame.push(StackSlice(slice))
            argc += 1
            pass

        else:
            # remove current frame args
            frame.pop_args()

            # replace args
            for x in range(argc - 1, -1, -1):
                frame.push(args[x])

        # reset frame to our state
        frame.code_obj = self
        frame.argc = argc
        frame.consts = self._consts
        frame.bc = self._bytecode
        frame.ip = 0

    @elidable
    def get_consts(self):
        return self._consts

    @elidable
    def get_bytecode(self):
        return self._bytecode

class Closure(BaseCode):
    _type = object.Type("Closure")
    def type(self):
        return Closure._type

    def __init__(self, code, closed_overs):
        BaseCode.__init__(self)
        self._code = code
        self._closed_overs = closed_overs

    def invoke(self, frame, argc):
        self._code.invoke(frame, argc)
        frame.code_obj = self

    def tail_call(self, frame, argc):
        self._code.tail_call(frame, argc)
        frame.code_obj = self

    @elidable
    def get_closed_over(self, idx):
        return self._closed_overs[idx]

    @elidable
    def get_consts(self):
        return self._code.get_consts()

    @elidable
    def get_bytecode(self):
        return self._code.get_bytecode()

class Var(object.Object):
    type = object.Type("Var")
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
        class FnWrapper(NativeFn):
            def inner_invoke(self, args):
                return fn(*args)
        var.set_root(FnWrapper())
        return fn
    return with_fn