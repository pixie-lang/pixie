from pixie.vm.effects.effects import Object, Type
from pixie.vm.code import wrap_fn
import pixie.vm.rt as rt
from pixie.vm.primitives import nil, true, false
from pixie.vm.persistent_vector import PersistentVector, EMPTY as EMPTY_VECTOR
from pixie.vm.persistent_list import PersistentList
from pixie.vm.symbol import Symbol
from pixie.vm.keyword import keyword
from pixie.vm.effects.effect_transform import cps
from pixie.vm.numbers import Integer
from pixie.vm.ast import *

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

@cps
def compile_fn_Ef(form):
    form = rt.next_Ef(form)
    name = rt.first_Ef(form)
    form = rt.next_Ef(form)
    args = rt.first_Ef(form)
    body = rt.next_Ef(form)

    name_kw = keyword(name.name())
    acc = EMPTY_VECTOR
    idx = 0
    arg = None
    while idx < args.count():
        arg = args.nth(idx)
        acc = acc.conj(keyword(arg.name()))
        idx += 1

    body_comp = compile_implicit_do_Ef(body)

    return FnLiteral(PixieFunction(name_kw, acc, body_comp))

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
        return Do(acc)

_builtins = {u"if": compile_if_Ef,
             u"fn*": compile_fn_Ef}



@cps
def compile_cons_Ef(form):

    fst = rt.first_Ef(form)
    builtin_Ef = ns = name = None
    if isinstance(fst, Symbol):
        ns = fst.namespace()
        if ns == u"pixie.stdlib" or ns is None:
            name = fst.name()
            builtin_Ef = _builtins.get(name, None)
            if builtin_Ef is not None:
                return builtin_Ef(form)

    acc = EMPTY_VECTOR
    while form is not nil:
        result = rt.first_Ef(form)
        ast = compile_Ef(result)
        acc = acc.conj(ast)
        form = rt.next_Ef(form)

    return Invoke(acc.to_list())



@cps
def compile_Ef(form):
    return compile_itm_Ef(form)