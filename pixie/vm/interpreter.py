from pixie.vm.object import Object, affirm, WrappedException, Type
import pixie.vm.code as code
import pixie.vm.numbers as numbers
from pixie.vm.primitives import nil, true, false
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.jit import JitDriver, promote, elidable, elidable_promote, hint, unroll_safe
import rpython.rlib.jit as jit
import rpython.rlib.debug as debug
import pixie.vm.rt as rt

def get_location(ip, sp, is_continuation, bc, base_code):
    return code.BYTECODES[bc[ip]] + " in " + str(base_code._name)

jitdriver = JitDriver(greens=["ip", "sp", "is_continuation", "bc", "base_code"], reds=["frame"], virtualizables=["frame"],
                      get_printable_location=get_location)


@elidable
def get_inst_by_idx(bc, idx):
    return bc[idx]

class Frame(object):
    _virtualizable_ = ["stack[*]",
                       "sp",
                       "ip",
                       "bc",
                       "consts[*]",
                       "code_obj",
                       "debug_points",
                       "args[*]",
                       "base_code",
                       "closed_overs[*]",
                       "finished",
                       "_is_continuation",
                       "self_obj"
    ]
    def __init__(self, code_obj, args, self_obj):
        self = hint(self, access_directly=True, fresh_virtualizable=True)
        self.code_obj = code_obj
        self.self_obj = self_obj
        self.sp = r_uint(0)
        self.ip = r_uint(0)
        self.stack = [None] * code_obj.stack_size()
        self.args = debug.make_sure_not_resized(args)
        self.base_code = code_obj.get_base_code()
        self.debug_points = code_obj.get_debug_points()
        self.finished = False
        self._is_continuation = 0
        if code_obj is not None:
            self.unpack_code_obj()

    def set_continuation(self):
        self._is_continuation = 1

    def is_continuation(self):
        return self._is_continuation == 1


    def unpack_code_obj(self):
        self.bc = self.code_obj.get_bytecode()
        self.consts = self.code_obj.get_consts()
        if isinstance(self.code_obj, code.Closure):
            self.closed_overs = self.code_obj.get_closed_overs()
        else:
            self.closed_overs = []

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
        assert 0 <= self.sp < len(self.stack), u"Stack out of range: " + unicode(str(self.sp))
        v = self.stack[self.sp]
        self.stack[self.sp] = None
        return v


    def nth(self, delta):
        affirm(delta >= 0, u"Invalid nth value, (compiler error)")
        affirm(self.sp - 1 >= delta, u"interpreter nth out of range, (compiler error) ")
        return self.stack[self.sp - delta - 1]

    def push_nth(self, delta):
        self.push(self.nth(delta))

    def push_arg(self, idx):
        affirm(0 <= idx < len(self.args), u"Argument doesn't exist")
        self.push(self.args[r_uint(idx)])

    @unroll_safe
    def push_n(self, args, argc):
        x = r_uint(0)
        while x < argc:
            self.push(args[x])
            x += 1

    @unroll_safe
    def pop_n(self, argc):
        args = [None] * argc
        x = r_uint(0)
        while x < argc:
            args[argc - x - 1] = self.pop()
            x += 1
        return args

    def get_const(self, idx):
        assert 0 <= idx < len(self.consts)
        return self.consts[idx]

    def push_const(self, idx):
        self.push(self.get_const(idx))

    def jump_rel(self, delta):
        self.ip += delta - 1

    def push_closed_over(self, idx):
        assert 0 <= idx < len(self.closed_overs)
        self.push(self.closed_overs[idx])

@jit.unroll_safe
def make_multi_arity(frame, argc):
    d = {}
    required_arity = 0
    rest_fn = None
    for i in range(argc):
        a = frame.get_inst()
        if a & 256:
            affirm(rest_fn is None, u"Can't have multiple rest_fns")
            required_arity = a & 0xFF
            rest_fn = frame.pop()
        else:
            fn = frame.pop()
            d[a] = fn

    return code.MultiArityFn(d, required_arity, rest_fn)

class ShallowContinuation(Object):
    _type = Type(u"pixie.stdlib.ShallowContinuation")

    def __init__(self, frame, val):
        assert isinstance(frame, Frame)
        self._frame = frame
        self._val = val

    def type(self):
        return ShallowContinuation._type


    def is_finished(self):
        return self._frame.finished

    def invoke(self, args):
        affirm(len(args) == 1, u"Generators only take one argument")
        self._frame.push(args[0])
        val = interpret(frame=self._frame)
        self._val = val
        return self._val

def interpret(code_obj=None, args=[], self_obj = None, frame=None):

    if frame is None:
        assert code_obj is not None
        frame = Frame(code_obj, args, self_obj or code_obj)



    while True:
        jitdriver.jit_merge_point(bc=frame.bc,
                                  ip=frame.ip,
                                  sp=frame.sp,
                                  base_code=frame.base_code,
                                  frame=frame,
                                  is_continuation=frame._is_continuation)
        inst = frame.get_inst()

        if inst == code.LOAD_CONST:
            arg = frame.get_inst()
            frame.push_const(arg)
            continue

        if inst == code.INVOKE:
            debug_ip = frame.ip
            argc = frame.get_inst()
            fn = frame.nth(argc - 1)

            #assert isinstance(fn, code.BaseCode), "Expected callable, got " + str(fn)



            args = frame.pop_n(argc - 1)
            frame.pop()
            try:
                frame.push(fn.invoke(args))
                continue
            except WrappedException as ex:
                dp = frame.debug_points.get(debug_ip - 1, None)
                if dp:
                    ex._ex._trace.append(dp)
                raise

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
            frame.finished = True
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
            frame.push_closed_over(idx)
            continue

        if inst == code.SET_VAR:
            val = frame.pop()
            var = frame.pop()

            affirm(isinstance(var, code.Var), u"Can't set the value of a non-var")
            var.set_root(val)
            frame.push(var)
            continue

        if inst == code.POP:
            frame.pop()
            continue

        if inst == code.DEREF_VAR:
            debug_ip = frame.ip
            var = frame.pop()
            if not isinstance(var, code.Var):
                affirm(False, u"Can't deref " + var.type()._name)
            try:
                frame.push(var.deref())
                continue
            except WrappedException as ex:
                dp = frame.debug_points.get(debug_ip - 1, None)
                if dp:
                    ex._ex._trace.append(dp)
                raise


        if inst == code.RECUR:
            argc = frame.get_inst()
            args = frame.pop_n(argc)

            frame = Frame(frame.code_obj, args, frame.self_obj)

            jitdriver.can_enter_jit(bc=frame.bc,
                                  ip=frame.ip,
                                  sp=frame.sp,
                                  base_code=frame.base_code,
                                  frame=frame,
                                  is_continuation=frame._is_continuation)
            continue

        if inst == code.PUSH_SELF:
            frame.push(frame.self_obj)
            continue

        if inst == code.DUP_NTH:
            n = frame.nth(frame.get_inst())
            frame.push(n)
            continue

        if inst == code.POP_UP_N:
            val = frame.pop()
            num = frame.get_inst()
            frame.pop_n(num)
            frame.push(val)
            continue

        if inst == code.LOOP_RECUR:
            argc = frame.get_inst()
            stack_depth = frame.get_inst()
            ip = frame.get_inst()

            args = frame.pop_n(argc)
            frame.pop_n(stack_depth)
            frame.pop_n(argc)
            frame.push_n(args, argc)
            frame.ip = ip


            jitdriver.can_enter_jit(bc=frame.bc,
                                  ip=frame.ip,
                                  sp=frame.sp,
                                  base_code=frame.base_code,
                                  frame=frame,
                                  is_continuation=frame._is_continuation)
            continue

        if inst == code.MAKE_MULTI_ARITY:
            frame.push(make_multi_arity(frame, frame.get_inst()))

            continue

        if inst == code.MAKE_VARIADIC:
            code_object = frame.pop()
            required_arity = frame.get_inst()
            frame.push(code.VariadicCode(code_object, required_arity))

            continue

        if inst == code.YIELD:
            if not frame.is_continuation():
                frame.set_continuation()
                #frame = jit.hint(frame, force_virtualizable=True)
                k = ShallowContinuation(frame, frame.pop())
                return k
            else:
                return frame.pop()


        affirm(False, u"NO DISPATCH FOR: " + unicode(code.BYTECODES[inst]))
        raise Exception()


## Hack to fixup recursive modules
code.interpret = interpret
