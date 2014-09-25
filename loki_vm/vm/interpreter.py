from loki_vm.vm.object import Object
import loki_vm.vm.code as code
import loki_vm.vm.numbers as numbers
from loki_vm.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.jit import JitDriver, promote, elidable, elidable_promote

def get_location(ip, bc):
    return code.BYTECODES[bc[ip]]

jitdriver = JitDriver(greens=["ip", "bc"], reds=["sp", "frame"], virtualizables=["frame"],
                      get_printable_location=get_location)




class FrameMarkerBase(Object):

    def unpack(self, frame):
        raise NotImplementedError()

class FrameMarker(FrameMarkerBase):
    __immutable_fields__ = ["argc", "ip", "code_obj", "bytecode", "consts"]
    def __init__(self, argc, ip, code_obj, bytecode, consts):
        self.argc = argc
        self.ip = ip
        self.code_obj = code_obj
        self.bytecode = bytecode
        self.consts = consts

    def unpack(self, frame):
        frame.code_obj = self.code_obj
        frame.consts = self.consts
        frame.ip = self.ip
        frame.bc = self.bytecode
        frame.argc = self.argc

class InstalledHandler(FrameMarkerBase):
    _immutable_fields_ = ["_handler"]
    def __init__(self, o):
        self._handler = o

    def unpack(self, frame):
        parent = frame.pop()
        parent.unpack(frame)

class Frame(object):
    _virtualizable_ = ["stack[*]", "sp", "ip", "bc"]
    def __init__(self, code_obj):
        self.code_obj = code_obj
        self.sp = r_uint(0)
        self.ip = r_uint(0)
        self.stack = [None] * 24
        self.unpack_code_obj()
        self.argc = 0

    def unpack_code_obj(self):
        if isinstance(self.code_obj, code.StackSlice):
            w_args = self.pop()
            w_ip = self.pop()
            w_code = self.pop()

            assert isinstance(w_args, numbers.Integer) & w_args.int_val() == 2
            arg = self.pop()
            self.pop() # this is the stack slice

            self.push(w_code)
            self.push(w_ip)

        else:
            self.bc = self.code_obj.get_bytecode()
            self.consts = self.code_obj.get_consts()

    def get_inst(self):
        #assert 0 <= self.ip < len(self.bc)
        inst = self.bc[self.ip]
        self.ip = self.ip + 1
        return promote(inst)

    def push(self, val):
        #assert val is not None
        #assert 0 <= self.sp < len(self.stack)
        self.stack[self.sp] = val
        self.sp += 1

    def pop(self):
        self.sp -= 1
        v = self.stack[self.sp]
        self.stack[self.sp] = None
        return v

    def pop_args(self):
        for x in range(self.argc):
            self.pop()

    def nth(self, delta):
        return self.stack[self.sp - delta - 1]

    def push_nth(self, delta):
        self.push(self.nth(delta))

    def push_const(self, idx):
        self.push(self.consts[idx])

    def jump_rel(self, delta):
        self.ip += delta - 1


    def pack_state(self):
        return FrameMarker(self.argc, self.ip, self.code_obj, self.bc, self.consts)

    def slice_stack(self, on):

        for x in range(self.sp - 1, -1, -1):
            o = self.nth(x)
            if isinstance(o, InstalledHandler) and o._handler is on:
                slice = [None] * x
                for y in range(x):
                    slice[x - y - 1] = self.pop()


                return slice

        raise ValueError()



def interpret(code_obj):
    frame = Frame(code_obj)

    while True:
        jitdriver.jit_merge_point(bc=frame.bc,
                                  ip=frame.ip,
                                  sp=frame.sp,
                                  frame=frame)
        inst = frame.get_inst()

        if inst == code.LOAD_CONST:
            arg = frame.get_inst()
            frame.push_const(arg)
            continue

        if inst == code.ADD:
            a = frame.pop()
            b = frame.pop()

            r = numbers.add(a, b)
            frame.push(r)
            continue

        if inst == code.INSTALL:
            fn = frame.pop()
            handler = frame.pop()

            frame.push(frame.pack_state())
            frame.push(InstalledHandler(handler))
            frame.push(fn)
            fn.invoke(frame, 1)

            continue

        if inst == code.INVOKE:
            args = frame.get_inst()
            fn = frame.nth(args - 1)

            assert isinstance(fn, code.BaseCode)

            fn.invoke(frame, args)

            continue

        if inst == code.TAIL_CALL:
            args = frame.get_inst()
            fn = frame.nth(args - 1)

            assert isinstance(fn, code.BaseCode)

            fn.tail_call(frame, args)

            jitdriver.can_enter_jit(bc=frame.bc,
                                    frame=frame,
                                    sp=frame.sp,
                                    ip=frame.ip)
            continue

        if inst == code.DUP_NTH:
            arg = frame.get_inst()
            frame.push_nth(arg)

            continue

        if inst == code.RETURN:
            val = frame.pop()

            frame.pop_args()

            if frame.sp == 0:
                return val
            marker = frame.pop()

            assert isinstance(marker, FrameMarkerBase)

            marker.unpack(frame)

            frame.push(val)

            continue

        if inst == code.COND_BR:
            v = frame.pop()
            loc = frame.get_inst()
            if v is not nil and v is not false:
                continue
            frame.jump_rel(loc)
            continue

        if inst == code.JMP:
            ip = frame.get_inst()
            frame.jump_rel(ip)
            continue

        if inst == code.EQ:
            a = frame.pop()
            b = frame.pop()
            frame.push(numbers.eq(a, b))
            continue

        if inst == code.MAKE_CLOSURE:
            argc = frame.get_inst()

            lst = [None] * argc

            for idx in range(argc - 1, -1, -1):
                lst[idx] = frame.pop()

            cobj = frame.pop()
            closure = code.Closure(cobj, lst)
            frame.push(closure)

            continue

        if inst == code.CLOSED_OVER:
            assert isinstance(frame.code_obj, code.Closure)
            idx = frame.get_inst()
            frame.push(frame.code_obj._closed_overs[idx])
            continue

        if inst == code.SET_VAR:
            val = frame.pop()
            var = frame.pop()

            assert isinstance(var, code.Var)
            var.set_root(val)
            frame.push(var)
            continue

        if inst == code.POP:
            frame.pop()
            continue

        if inst == code.DEREF_VAR:
            var = frame.pop()
            assert isinstance(var, code.Var)
            frame.push(var.deref())
            continue

        print "NO DISPATCH FOR: " + code.BYTECODES[inst]
        raise Exception()

