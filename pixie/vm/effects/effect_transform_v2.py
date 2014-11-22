#from byteplay import *
from rpython.translator.translator import TranslationContext
from rpython.translator.unsimplify import insert_empty_startblock, split_block
from rpython.flowspace.model import Variable, Constant
from rpython.flowspace.operation import GetAttr
import pixie.vm.rt as rt
import types
from pixie.vm.effects.effects import Object

"""
Why write our own bytcode transformer when we can leverage PyPy's. This code would replace the existing transformer, and
would work the following way: a) we'd parse a function using RPython's translator. b) we walk the graph splitting blocks
on effect functions, and tracking the new links. c) we stitch the function back together, this time with state machine
saving, after each effect call.
"""


def stop_Ef(x, k):
    pass

stop_Ef._effect = True

def foo(x):
    y = stop_Ef(x)
    idx = 0
    while idx < 10:
        x = rt._str_Ef(x if y else 4).int_val().foo_Ef() + y
        idx += 1

    return x



ctx = TranslationContext()
graph = ctx.buildflowgraph(foo)

effect_links = set()

for block in list(graph.iterblocks()):
    for index in range(len(block.operations)-1, -1, -1):
        hlop = block.operations[index]
        if hlop.opname == "simple_call":
            is_xform = False
            if isinstance(hlop.args[0], Variable):
                resolved = None
                for j in block.operations:
                    if j.result == hlop.args[0]:
                        resolved = j
                        break
                assert resolved, "Function crossed block bounaries"
                if isinstance(resolved, GetAttr):
                    if resolved.args[1].value.endswith("_Ef"):
                        is_xform = True
                    pass

            elif isinstance(hlop.args[0], Constant):
                fn = hlop.args[0].value
                if getattr(fn, "_is_effect", None):
                    is_xform = True
                elif fn.__name__.endswith("_Ef"):
                    is_xform = True

            if is_xform:
                if index + 1 == len(block.operations):
                    assert len(block.exits) == 1
                    effect_links.add(block.exits[0])
                else:
                    newlink = split_block(None, block, index + 1)
                    effect_links.add(newlink)

            pass
        if hlop.opname == 'yield_':
            [v_yielded_value] = hlop.args
            del block.operations[index]
            newlink = split_block(None, block, index)

graph.view()
sb = x.startblock
process_blocks(foo)