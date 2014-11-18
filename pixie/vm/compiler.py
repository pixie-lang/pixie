from pixie.vm.effects.effects import Object, Type
from pixie.vm.code import wrap_fn
from pixie.vm.effects.effect_transform import cps
from pixie.vm.numbers import Integer
from pixie.vm.ast import *

@cps
def compile_itm_Ef(form):
    if isinstance(form, Integer):
        return Constant(form)

@cps
def compile_Ef(form):
    return compile_itm_Ef(form)