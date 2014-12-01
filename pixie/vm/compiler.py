from pixie.vm.effects.effects import Object, Type
from pixie.vm.code import wrap_fn
import pixie.vm.rt as rt
from pixie.vm.primitives import nil, true, false
from pixie.vm.persistent_vector import PersistentVector, EMPTY as EMPTY_VECTOR
from pixie.vm.persistent_list import PersistentList
from pixie.vm.symbol import Symbol
from pixie.vm.keyword import keyword, Keyword
from pixie.vm.effects.effect_transform import cps
from pixie.vm.effects.environment import throw_Ef
from rpython.rlib.rarithmetic import intmask
from pixie.vm.numbers import Integer
from pixie.vm.ast import *
import pixie.vm.ast as ast


VALUE_ERROR = keyword(u"VALUE-ERROR")

@cps
def compile_if_Ef(form):
    form = rt.next_Ef(form)
    test = rt.first_Ef(form)
    form = rt.next_Ef(form)
    then = rt.first_Ef(form)
    form = rt.next_Ef(form)
    els = rt.first_Ef(form)

    test_comp = compile_Ef(test)
    then_comp = compile_Ef(then)
    else_comp = compile_Ef(els)

    return If(test_comp, then_comp, else_comp)

def multi_fn_from_acc(name, acc):
    rest_fn = None
    d = {}
    for x in range(acc.count()):
        arity = acc.nth(x)
        if arity.required_args() < 0:
            rest_fn = arity
        else:
            d[r_uint(arity.required_args())] = arity

    return MultiArityFn(name, d, rest_fn)




@cps
def args_to_kws_Ef(args):
    acc = EMPTY_VECTOR
    idx = 0
    while idx < args.count():
        arg = args.nth(idx)
        if not isinstance(arg, Symbol):
            throw_Ef(VALUE_ERROR, u"Argument names must be symbols")

        acc = acc.conj(keyword(arg.name()))
        idx += 1

    return acc

def add_args(name, args):
    required_args = -1
    acc = EMPTY_VECTOR

    for x in range(args.count()):
        arg = args.nth(x)

        if arg.str() == u"&":
            required_args = intmask(x)
            continue

        acc = acc.conj(arg)

    return required_args, acc


@cps
def compile_implicit_do_Ef(body):
    acc = EMPTY_VECTOR
    while body is not nil:
        arg = rt.first_Ef(body)
        result = compile_itm_Ef(arg)
        acc = acc.conj(result)
        body = rt.next_Ef(body)

    if acc.count() == 1:
        return acc.nth(0)
    else:
        return Do(acc.to_list())

@cps
def compile_fn_body_Ef(name, args, body):

    required_args, args_vec = add_args(name, args)

    body_comp = compile_implicit_do_Ef(body)
    args_lst = args_vec.to_list()

    if required_args == -1:
        return PixieFunction(name, args_lst, body_comp)
    else:
        rargs = r_uint(required_args)
        return VariadicFunction(name, args_lst, rargs, body_comp)


@cps
def compile_fn_Ef(form):
    form = rt.next_Ef(form)
    name = rt.first_Ef(form)
    if isinstance(name, Symbol):
        form = rt.next_Ef(form)
        name_kw = keyword(name.name())
    else:
        name_kw = None
    args = rt.first_Ef(form)


    body = body_fn = None
    if isinstance(args, PersistentVector):
        body = rt.next_Ef(form)
        acc = args_to_kws_Ef(args)
        body_fn = compile_fn_body_Ef(name_kw, acc, body)
    else:
        acc = EMPTY_VECTOR
        while form is not nil:
            arity = rt.first_Ef(form)
            args = rt.first_Ef(arity)
            if not isinstance(args, PersistentVector):
                throw_Ef(VALUE_ERROR, u"Argument lists must be vectors")
            body = rt.next_Ef(arity)

            body_fn = compile_fn_body_Ef(None, args_to_kws_Ef(args), body)
            acc = acc.conj(body_fn)
            form = rt.next_Ef(form)

        body_fn = multi_fn_from_acc(name_kw, acc)




    return FnLiteral(body_fn)






@cps
def compile_def(form):
    form = rt.next_Ef(form)
    name = rt.first_Ef(form)
    form = rt.next_Ef(form)
    expr = rt.first_Ef(form)

    expr_comp = compile_itm_Ef(expr)

    if not isinstance(name, Symbol):
        throw_Ef(VALUE_ERROR, u"Def name must be a symbol")

    return Def(keyword(u"pixie.stdlib"), keyword(name.str()), expr_comp)

@cps
def compile_do(form):
    form = rt.next_Ef(form)
    return compile_implicit_do_Ef(form)

@cps
def compile_let_binding_Ef(bindings, idx, body):
    if idx == bindings.count():
        return body

    nm = keyword(bindings.nth(idx).str())
    expr = bindings.nth(idx + 1)

    expr_comp = compile_itm_Ef(expr)

    next_idx = idx + 2
    inner_comp = compile_let_binding_Ef(bindings, next_idx, body)

    return Binding(nm, expr_comp, inner_comp)





@cps
def compile_let(form):
    form = rt.next_Ef(form)
    bindings = rt.first_Ef(form)

    if not isinstance(bindings, PersistentVector):
        throw_Ef(VALUE_ERROR, u"Bindings must be a vector")

    if not bindings.count() % 2 == 0:
        throw_Ef(VALUE_ERROR, u"Must have an even number of bindings in let")

    form = rt.next_Ef(form)

    body_comp = compile_implicit_do_Ef(form)

    return compile_let_binding_Ef(bindings, 0, body_comp)



_builtins = {u"if": compile_if_Ef,
             u"fn*": compile_fn_Ef,
             u"def": compile_def,
             u"do": compile_do,
             u"let*": compile_let}

def invoke_builtin_Ef(bi_Ef, form):
    return bi_Ef(form)

@cps
def compile_cons_Ef(form):

    fst = rt.first_Ef(form)
    if isinstance(fst, Symbol):
        ns = fst.namespace()
        if ns == u"pixie.stdlib" or ns is None:
            name = fst.name()
            builtin_Ef = _builtins.get(name, None)
            if builtin_Ef is not None:
                return invoke_builtin_Ef(builtin_Ef, form)

    acc = EMPTY_VECTOR
    while form is not nil:
        result = rt.first_Ef(form)
        ast = compile_Ef(result)
        acc = acc.conj(ast)
        form = rt.next_Ef(form)

    return Invoke(acc.to_list())

@cps
def compile_vector_Ef(form):
    acc = EMPTY_VECTOR
    idx = 0
    cnt = rt.count_Ef(form).int_val()
    while idx < cnt:
        val = rt._nth_Ef(form, rt.wrap(idx))
        acc = acc.conj(compile_itm_Ef(val))
        idx += 1

    return ast.Vector(acc.to_list())

KW_IVECTOR = keyword(u"pixie.stdlib.IVector")

@cps
def compile_itm_Ef(form):
    if isinstance(form, Integer):
        return Constant(form)

    if isinstance(form, PersistentList):
        # TODO, switch this to a statisfies? call
        return compile_cons_Ef(form)

    if isinstance(form, Symbol):
        return Lookup(keyword(u"pixie.stdlib"), keyword(form.str()))

    if form is true:
        return Constant(true)

    if form is false:
        return Constant(false)

    if form is nil:
        return Constant(nil)

    if isinstance(form, Keyword):
        return Constant(form)

    if rt.satisfies_QMARK__Ef(KW_IVECTOR, form) is true:
        return compile_vector_Ef(form)

    #assert False



@cps
def compile_Ef(form):
    return compile_itm_Ef(form)

