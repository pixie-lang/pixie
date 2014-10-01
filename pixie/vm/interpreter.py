from pixie.vm.object import Object
import pixie.vm.code as code
import pixie.vm.numbers as numbers
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.jit import JitDriver, promote, elidable, elidable_promote, hint, unroll_safe

def get_location(ip, sp, bc):
    return code.BYTECODES[bc[ip]]

jitdriver = JitDriver(greens=["ip", "sp", "bc"], reds=["frame"], virtualizables=["frame"],
                      get_printable_location=get_location)


@elidable
def get_inst_by_idx(bc, idx):
    return bc[idx]

class Frame(object):
    __immutable_fields__ = ["stack"]
    _virtualizable_ = ["stack[*]",
                       "sp",
                       "ip",
                       "bc",
                       "consts",
                       "code_obj",
                       "args[*]",
]
    def __init__(self, code_obj, args=[]):
        self = hint(self, access_directly=True, fresh_virtualizable=True)
        self.code_obj = code_obj
        self.sp = r_uint(0)
        self.ip = r_uint(0)
        self.stack = [None] * 24
        self.args = args
        if code_obj is not None:
            self.unpack_code_obj()

    def unpack_code_obj(self):
        self.bc = self.code_obj.get_bytecode()
        self.consts = self.code_obj.get_consts()

    def get_inst(self):
        assert 0 <= self.ip < len(self.bc)
        inst = get_inst_by_idx(promote(self.bc), promote(self.ip))
        self.ip = self.ip + 1
        return promote(inst)

    def push(self, val):
        #assert val is not None
        assert 0 <= self.sp < len(self.stack)
        #print type(self.sp), self.sp
        self.stack[self.sp] = val
        self.sp += 1

    def pop(self):
        #print type(self.sp), self.sp
        self.sp -= 1
        v = self.stack[self.sp]
        self.stack[self.sp] = None
        return v


    def nth(self, delta):
        assert delta >= 0
        assert self.sp - 1 >= delta
        return self.stack[self.sp - delta - 1]

    def push_nth(self, delta):
        self.push(self.nth(delta))

    def push_arg(self, idx):
        self.push(self.args[idx])

    @unroll_safe
    def push_n(self, args, argc):
        x = argc
        while x != 0:
            self.push(args[x - 1])
            x -= 1

    @unroll_safe
    def pop_n(self, argc):
        args = [None] * argc
        x = r_uint(0)
        while x < argc:
            args[argc - x - 1] = self.pop()
            x += 1
        return args

    def get_const(self, idx):
        return self.consts[idx]

    def push_const(self, idx):
        self.push(self.get_const(idx))

    def jump_rel(self, delta):
        self.ip += delta - 1

def interpret(code_obj, args=[]):
    frame = Frame(code_obj, args)
    while True:
        jitdriver.jit_merge_point(bc=frame.bc,
                                  ip=frame.ip,
                                  sp=frame.sp,
                                  frame=frame)
        inst = frame.get_inst()

        #print code.BYTECODES[inst]

        if inst == code.LOAD_CONST:
            arg = frame.get_inst()
            frame.push_const(arg)
            continue

        if inst == code.INVOKE:
            argc = frame.get_inst()
            fn = frame.nth(argc - 1)

            assert isinstance(fn, code.BaseCode)

            args = frame.pop_n(argc - 1)
            frame.pop()

            frame.push(fn.invoke(args))

            continue

        # if inst == code.TAIL_CALL:
        #     argc = frame.get_inst()
        #     fn = frame.nth(argc - 1)
        #
        #     assert isinstance(fn, code.BaseCode)
        #
        #     args = frame.pop_n(argc - 1)
        #     frame.pop()
        #
        #     return code.TailCall(fn, args)

        if inst == code.ARG:
            arg = frame.get_inst()
            frame.push_arg(arg)

            continue

        if inst == code.RETURN:
            val = frame.pop()

            return val

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

        if inst == code.RECUR:
            argc = frame.get_inst()
            args = frame.pop_n(argc)

            frame = Frame(frame.code_obj, args)

            jitdriver.can_enter_jit(bc=frame.bc,
                                  ip=frame.ip,
                                  sp=frame.sp,
                                  frame=frame)
            continue

        if inst == code.PUSH_SELF:
            frame.push(frame.code_obj)
            continue

        print "NO DISPATCH FOR: " + code.BYTECODES[inst]
        raise Exception()


## Hack to fixup recursive modules
code.interpret = interpret
