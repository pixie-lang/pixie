from pixie.vm2.object import Object, Type, Continuation, stack_cons
from pixie.vm2.primitives import nil, false
from pixie.vm2.array import Array
import pixie.vm2.code as code
from pixie.vm2.code import BaseCode

import rpython.rlib.jit as jit

class AST(Object):
    _immutable_fields_ = ["_c_meta"]
    should_enter_jit = False
    def __init__(self, meta):
        self._c_meta = meta


class InterpretK(Continuation):
    _immutable_ = True
    def __init__(self, ast, locals):
        self._c_ast = ast
        self._c_locals = locals

    def call_continuation(self, val, stack):
        ast = jit.promote(self._c_ast)
        return ast.interpret(val, self._c_locals, stack)

class Const(AST):
    _immutable_fields_ = ["_c_val"]
    _type = Type(u"pixie.interpreter.Const")
    def __init__(self, val, meta=nil):
        AST.__init__(self, meta)
        self._c_val = val

    def interpret(self, _, locals, stack):
        return jit.promote(self._c_val), stack

class Locals(object):
    _immutable_ = True
    def __init__(self, name, value, next):
        self._c_value = value
        self._c_name = name
        self._c_next = next

    @staticmethod
    @jit.unroll_safe
    def get_local(self, name):
        if self is None:
            return nil
        c = self
        while c._c_name is not name:
            c = c._c_next
        return c._c_value

class Lookup(AST):
    _immutable_fields_ = ["_c_name"]
    def __init__(self, name, meta=nil):
        AST.__init__(self, meta)
        self._c_name = name

    def interpret(self, _, locals, stack):
        return Locals.get_local(locals, self._c_name), stack


class Fn(AST):
    _immutable_fields_ = ["_c_name", "_c_args", "_c_body", "_c_closed_overs"]
    def __init__(self, name, args, body, meta=nil):
        AST.__init__(self, meta)
        self._c_name = name
        self._c_args = args
        self._c_body = body

    @jit.unroll_safe
    def interpret(self, _, locals, stack):
        return InterpretedFn(self._c_name, self._c_args, self._c_body), stack

class InterpretedFn(code.BaseCode):
    _immutable_fields_ = ["_c_arg_names", "_c_locals", "_c_fn_ast"]
    def __init__(self, name, arg_names, ast):
        self._c_arg_names = arg_names
        if name is not nil:
            self._c_locals = Locals(name, self, None)
        else:
            self._c_locals = None
        self._c_fn_ast = ast

    @jit.unroll_safe
    def invoke_k(self, args, stack):
        # TODO: Check arg count
        locals = jit.promote(self._c_locals)
        for idx in range(len(self._c_arg_names)):
            locals = Locals(self._c_arg_names[idx], args[idx], locals)

        return nil, stack_cons(stack, InterpretK(self._c_fn_ast, locals))


class Invoke(AST):
    _immutable_fields_ = ["_c_args", "_c_fn"]
    def __init__(self, args, meta=nil):
        AST.__init__(self, meta)
        self._c_args = args

    def interpret(self, _, locals, stack):
        stack = stack_cons(stack, InvokeK(self))
        stack = stack_cons(stack, ResolveAllK(self._c_args, locals, []))
        stack = stack_cons(stack, InterpretK(self._c_args[0], locals))
        return nil, stack

class InvokeK(Continuation):
    _immutable_ = True
    def __init__(self, ast):
        self._c_ast = ast

    def call_continuation(self, val, stack):
        assert isinstance(val, Array)
        fn = val._list[0]
        args = val._list[1:]
        return fn.invoke_k(args, stack)



class TailCall(AST):
    _immutable_fields_ = ["_c_args", "_c_fn"]
    def __init__(self, args, meta=nil):
        AST.__init__(self, meta)
        self._c_args = args

    def interpret(self, _, locals, stack):
        stack = stack_cons(stack, TailCallK(self))
        stack = stack_cons(stack, ResolveAllK(self._c_args, locals, []))
        stack = stack_cons(stack, InterpretK(self._c_args[0], locals))
        return nil, stack

class TailCallK(InvokeK):
    _immutable_ = True
    should_enter_jit = True
    def __init__(self, ast):
        InvokeK.__init__(self, ast)

class ResolveAllK(Continuation):
    _immutable_ = True
    def __init__(self, args, locals, acc):
        self._c_args = args
        self._c_locals = locals
        self._c_acc = acc

    @jit.unroll_safe
    def append_to_acc(self, val):
        acc = [None] * (len(self._c_acc) + 1)
        for x in range(len(self._c_acc)):
            acc[x] = self._c_acc[x]
        acc[len(self._c_acc)] = val
        return acc

    def call_continuation(self, val, stack):
        if len(self._c_acc) + 1 < len(self._c_args):
            stack = stack_cons(stack, ResolveAllK(self._c_args, self._c_locals, self.append_to_acc(val)))
            stack = stack_cons(stack, InterpretK(self._c_args[len(self._c_acc) + 1], self._c_locals))
        else:
            return Array(self.append_to_acc(val)), stack

        return val, stack




class If(AST):
    _immutable_fields_ = ["_c_test", "_c_then", "_c_else"]
    def __init__(self, test, then, els, meta=nil):
        AST.__init__(self, meta)
        self._c_test = test
        self._c_then = then
        self._c_else = els

    def interpret(self, val, locals, stack):
        stack = stack_cons(stack, IfK(self, locals))
        stack = stack_cons(stack, InterpretK(self._c_test, locals))
        return nil, stack

class IfK(Continuation):
    _immutable_ = True
    def __init__(self, ast, locals):
        self._c_ast = ast
        self._c_locals = locals

    def call_continuation(self, val, stack):
        ast = self._c_ast
        assert isinstance(self._c_ast, If)
        if val is nil or val is false:
            stack = stack_cons(stack, InterpretK(ast._c_else, self._c_locals))
        else:
            stack = stack_cons(stack, InterpretK(ast._c_then, self._c_locals))
        return nil, stack


class Do(AST):
    _immutable_fields_ = ["_c_body_asts"]
    def __init__(self, args, meta=nil):
        AST.__init__(self, meta)
        self._c_body_asts = args

    @jit.unroll_safe
    def interpret(self, val, locals, stack):
        return val, stack_cons(stack, DoK(self._c_body_asts, locals))


class DoK(Continuation):
    _immutable_ = True
    def __init__(self, do_asts, locals, idx=0):
        self._c_locals = locals
        self._c_body_asts = do_asts
        self._c_idx = idx

    def call_continuation(self, val, stack):
        if self._c_idx + 1 < len(self._c_body_asts):
            stack = stack_cons(stack, DoK(self._c_body_asts, self._c_locals, self._c_idx + 1))
            stack = stack_cons(stack, InterpretK(self._c_body_asts[self._c_idx], self._c_locals))
            return nil, stack
        else:
            stack = stack_cons(stack, InterpretK(self._c_body_asts[self._c_idx], self._c_locals))
            return nil, stack
