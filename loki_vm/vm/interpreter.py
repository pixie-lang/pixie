import loki_vm.vm.code as code
import loki_vm.vm.numbers as numbers
from loki_vm.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint, intmask


class Frame(object):
    def __init__(self, code_obj):
        self.code_obj = code_obj
        self.sp = r_uint(0)
        self.ip = r_uint(0)
        self.stack = [None] * 24
        self.unpack_code_obj()

    def unpack_code_obj(self):
        self.consts = self.code_obj._consts
        self.bc = self.code_obj._bytecode

    def get_inst(self):
        inst = self.bc[self.ip]
        self.ip += 1
        return inst

    def push(self, val):
        assert val is not None
        self.stack[self.sp] = val
        self.sp += 1

    def pop(self):
        self.sp -= 1
        v = self.stack[self.sp]
        self.stack[self.sp] = None
        return v

    def nth(self, delta):
        return self.stack[self.sp - delta - 1]

    def push_nth(self, delta):
        self.push(self.nth(delta))

    def descend(self, code_obj, args):
        self.push(self.code_obj)
        self.push(numbers.Integer(intmask(self.ip)))
        self.push(numbers.Integer(intmask(args)))

        self.code_obj = code_obj
        self.unpack_code_obj()
        self.ip = r_uint(0)

    def ascend(self):
        ret_val = self.pop()
        if self.sp == 0:
            return ret_val

        w_args = self.pop()
        assert isinstance(w_args, numbers.Integer)

        w_ip = self.pop()
        assert isinstance(w_ip, numbers.Integer)
        self.code_obj = self.pop()

        for x in range(w_args.r_uint_val() - 1):
            self.pop()

        self.pop()

        self.unpack_code_obj()
        self.push(ret_val)

        self.ip = w_ip.r_uint_val()

    def push_const(self, idx):
        self.push(self.consts[idx])

    def jump_rel(self, delta):
        self.ip += delta - 1




def interpret(code_obj):
    frame = Frame(code_obj)

    while True:
        inst = frame.get_inst()
        print code.BYTECODES[inst]

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

        if inst == code.INVOKE:
            args = frame.get_inst()
            fn = frame.nth(args - 1)

            assert isinstance(fn, code.Code)
            frame.descend(fn, args)

            continue

        if inst == code.TAIL_CALL:
            args = frame.get_inst()
            tmp_args = []
            for x in range(args):
                tmp_args.append(frame.pop())

            code_obj = tmp_args[args - 1]

            old_args_w = frame.pop()
            assert isinstance(old_args_w, numbers.Integer)
            old_ip = frame.pop()
            old_code = frame.pop()

            for x in range(old_args_w.r_uint_val()):
                frame.pop()

            for x in range(args - 1, -1, -1):
                frame.push(tmp_args[x])

            frame.push(old_code)
            frame.push(old_ip)
            frame.push(numbers.Integer(intmask(args)))
            frame.code_obj = code_obj
            frame.unpack_code_obj()
            frame.ip = 0

            continue

        if inst == code.DUP_NTH:
            arg = frame.get_inst()
            frame.push_nth(arg)

            continue

        if inst == code.RETURN:
            v = frame.ascend()
            if v is not None:
                return v
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


        print "NO DISPATCH FOR: " + code.BYTECODES[inst]
        raise Exception()

