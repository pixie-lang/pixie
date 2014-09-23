from loki_vm.vm.object import Object
from loki_vm.vm.primitives import nil, true, false, Bool
import loki_vm.vm.numbers as numbers
from loki_vm.vm.cons import cons, Cons, count
import loki_vm.vm.symbol as symbol
import loki_vm.vm.code as code
from rpython.rlib.rarithmetic import r_uint

class Context(object):
    def __init__(self, argc):
        self.bytecode = []
        self.consts = []
        self.locals = [{}]
        self.sp = argc + 3
        self.can_tail_call = False

    def to_code(self):
        return code.Code(self.bytecode, self.consts)

    def push_arg(self, idx):
        self.bytecode.append(code.DUP_NTH)
        self.bytecode.append(r_uint(self.sp - idx))
        self.sp += 1


    def add_local(self, name, arg):
        self.locals.append(self.locals[-1].copy())
        self.locals[-1][name] = arg


    def get_local(self, s_name):
        return self.locals[-1].get(s_name, None)


    def undef_local(self):
        self.locals.pop()

    def push_const(self, v):
        idx = r_uint(len(self.consts))
        self.consts.append(v)
        self.bytecode.append(code.LOAD_CONST)
        self.bytecode.append(idx)
        self.sp += 1

    def label(self):
        lbl = len(self.bytecode)
        self.bytecode.append(r_uint(99))
        return lbl

    def mark(self, lbl):
        self.bytecode[lbl] = r_uint(len(self.bytecode)) - lbl

    def enable_tail_call(self):
        self.can_tail_call = True

    def disable_tail_call(self):
        self.can_tail_call = False

class LocalType(object):
    pass

class Arg(LocalType):
    def __init__(self, idx):
        self.idx = r_uint(idx)

    def emit(self, ctx):
        ctx.push_arg(self.idx)



def compile_form(form, ctx):
    if isinstance(form, Cons):
        return compile_cons(form, ctx)
    if isinstance(form, numbers.Integer):
        ctx.push_const(form)
        return

    if isinstance(form, symbol.Symbol):
        loc = ctx.get_local(form._str)
        if loc is None:
            raise Exception(form._str + " is not bound")
        loc.emit(ctx)
        return

    if isinstance(form, Bool) or form is nil:
        ctx.push_const(form)
        return

    raise Exception("Can't compile ")

def compile_platform_plus(form, ctx):
    form = form.next()
    while form is not nil:
        compile_form(form.first(), ctx)
        form = form.next()

    ctx.bytecode.append(code.ADD)
    ctx.sp -= 1
    return ctx

def compile_platform_eq(form, ctx):
    form = form.next()
    assert count(form) == 2
    while form is not nil:
        compile_form(form.first(), ctx)
        form = form.next()

    ctx.bytecode.append(code.EQ)
    ctx.sp -= 1
    return ctx

def add_args(args, ctx):
    for x in range(count(args)):
        arg = args.first()
        assert isinstance(arg, symbol.Symbol)
        ctx.add_local(arg._str, Arg(x + 1)) # TOS is Code so + 1 for first arg
        args = args.next()



def compile_fn(form, ctx):
    assert isinstance(form, Cons)


    form = form.next()
    if isinstance(form.first(), symbol.Symbol):
        name = form.first()
        form = form.next()
    else:
        name = None

    args = form.first()
    assert isinstance(args, Cons) or args is nil

    body = form.next()
    new_ctx = Context(count(args))
    add_args(args, new_ctx)
    bc = 0

    if name is not None:
        assert isinstance(name, symbol.Symbol)
        new_ctx.add_local(name._str, Arg(0))


    new_ctx.enable_tail_call()
    while body is not nil:
        compile_form(body.first(), new_ctx)
        bc += 1
        body = body.next()

    new_ctx.bytecode.append(code.RETURN)
    ctx.push_const(new_ctx.to_code())


def compile_if(form, ctx):
    form = form.next()
    assert count(form) == 3

    test = form.first()
    form = form.next()
    then = form.first()
    form = form.next()
    els = form.first()

    ctx.disable_tail_call()
    compile_form(test, ctx)
    ctx.bytecode.append(code.COND_BR)
    ctx.sp -= 1
    cond_lbl = ctx.label()

    ctx.enable_tail_call()

    compile_form(then, ctx)
    ctx.bytecode.append(code.JMP)
    ctx.sp -= 1
    else_lbl = ctx.label()

    ctx.mark(cond_lbl)
    compile_form(els, ctx)

    ctx.mark(else_lbl)

builtins = {"platform+": compile_platform_plus,
            "fn": compile_fn,
            "if": compile_if,
            "platform=": compile_platform_eq}

def compile_cons(form, ctx):
    if isinstance(form.first(), symbol.Symbol) and form.first()._str in builtins:
        return builtins[form.first()._str](form, ctx)

    cnt = r_uint(0)
    while form is not nil:
        compile_form(form.first(), ctx)
        cnt += 1
        form = form.next()

    if ctx.can_tail_call:
        ctx.bytecode.append(code.TAIL_CALL)
    else:
        ctx.bytecode.append(code.INVOKE)

    ctx.bytecode.append(cnt)


def compile(form):
    ctx = Context(0)
    compile_form(form, ctx)
    ctx.bytecode.append(code.RETURN)
    return ctx.to_code()