from pixie.vm.effects.effects import Object, Type, Handler, handle_with, ContinuationThunk, Thunk
from pixie.vm.effects.effect_generator import defeffect
from pixie.vm.persistent_instance_hash_map import EMPTY as EMPTY_MAP
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

defeffect("pixie.compiler.Local", "LocalLookup", ["name", "create"])

VALUE_ERROR = keyword(u"VALUE-ERROR")

class WithLocalsAssignment(Handler):
    _immutable_ = True
    def __init__(self, env):
        self._env = env

    def handle(self, effect, k):
        if isinstance(effect, Answer):
            return effect
        if effect.type() is LocalLookup._type:
            nm = effect.get(KW_NAME)
            val = self._env.val_at(nm, None)
            if val is None and effect.get(KW_CREATE) is false:
                return handle_with(self, ContinuationThunk(effect.get(KW_K), nil))
            elif val is None:
                val = rt.wrap(intmask(self._env.count()))
                env = self._env.assoc(nm, val)
                return handle_with(WithLocalsAssignment(env), ContinuationThunk(effect.get(KW_K), val))
            else:
                return handle_with(self, ContinuationThunk(effect.get(KW_K), val))

class InvokeWith(Thunk):
    def __init__(self, comp_f, form):
        self._comp_f = comp_f
        self._w_form = form

    def execute_thunk(self):
        return self._comp_f(self._w_form)

def with_new_env_Ef(f, form):
    return handle_with(WithLocalsAssignment(EMPTY_MAP),
                       InvokeWith(f, form))

def with_env_Ef(f, form, env):
    return handle_with(WithLocalsAssignment(env),
                       InvokeWith(f, form))

@cps
def find_or_make_local_Ef(nm):
    return LocalLookup(nm, true).raise_Ef()

@cps
def find_local_Ef(nm):
    return LocalLookup(nm, false).raise_Ef()



@cps
def compile_if_Ef(form):
    form = rt.next_Ef(form)
    test = rt.first_Ef(form)
    form = rt.next_Ef(form)
    then = rt.first_Ef(form)
    form = rt.next_Ef(form)
    els = rt.first_Ef(form)

    test_comp = compile_itm_Ef(test)
    then_comp = compile_itm_Ef(then)
    else_comp = compile_itm_Ef(els)

    return If(test_comp, then_comp, else_comp)

def multi_fn_from_acc(name, name_idx, acc):
    rest_fn = None

    d = {}
    for x in range(acc.count()):
        arity = acc.nth(x)
        if arity.required_args() < 0:
            rest_fn = arity
        else:
            d[r_uint(arity.required_args())] = arity

    return MultiArityFn(name, d, name_idx, rest_fn)




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

@cps
def add_args_Ef(name, args):
    required_args = -1
    acc = EMPTY_VECTOR

    x = 0
    while x < args.count():

        arg = args.nth(x)

        if arg.str() == u"&":
            required_args = intmask(x)
            x += 1
            continue
        acc = acc.conj(find_or_make_local_Ef(arg))
        x += 1

    return EMPTY_VECTOR.conj(rt.wrap(required_args)).conj(acc)


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

    if name is not None:
        name_idx = find_or_make_local_Ef(name).r_uint_val()
    else:
        name_idx = r_uint(0)

    ret = add_args_Ef(name, args)
    required_args = ret.nth(0).int_val()
    args_vec = ret.nth(1)

    body_comp = compile_implicit_do_Ef(body)
    args_lst = args_vec.to_r_uint_list()


    if required_args == -1:
        return PixieFunction(name, args_lst, body_comp, name_idx)
    else:
        rargs = r_uint(required_args)
        return VariadicFunction(name, args_lst, rargs, body_comp, name_idx)


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

        if name is not None:
            name_idx = find_or_make_local_Ef(name).r_uint_val()
        else:
            name_idx = r_uint(0)

        while form is not nil:
            arity = rt.first_Ef(form)
            args = rt.first_Ef(arity)
            if not isinstance(args, PersistentVector):
                throw_Ef(VALUE_ERROR, u"Argument lists must be vectors")
            body = rt.next_Ef(arity)

            body_fn = compile_fn_body_Ef(None, args_to_kws_Ef(args), body)
            acc = acc.conj(body_fn)
            form = rt.next_Ef(form)




        body_fn = multi_fn_from_acc(name_kw, name_idx, acc)




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
        return compile_implicit_do_Ef(body)

    nm = keyword(bindings.nth(idx).str())
    local_idx = find_or_make_local_Ef(nm).r_uint_val()

    expr = bindings.nth(idx + 1)

    expr_comp = compile_itm_Ef(expr)

    next_idx = idx + 2
    inner_comp = compile_let_binding_Ef(bindings, next_idx, body)

    return Binding(local_idx, expr_comp, inner_comp)





@cps
def compile_let(form):
    form = rt.next_Ef(form)
    bindings = rt.first_Ef(form)

    if not isinstance(bindings, PersistentVector):
        throw_Ef(VALUE_ERROR, u"Bindings must be a vector")

    if not bindings.count() % 2 == 0:
        throw_Ef(VALUE_ERROR, u"Must have an even number of bindings in let")

    form = rt.next_Ef(form)

    return compile_let_binding_Ef(bindings, 0, form)



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
        ast = compile_itm_Ef(result)
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
        form_kw = keyword(form.str())
        local = find_local_Ef(form_kw)
        if local is nil:
            return LookupGlobal(keyword(u"pixie.stdlib"), form_kw)
        else:
            return LookupLocal(local.r_uint_val())

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
    return with_new_env_Ef(compile_itm_Ef, form)

