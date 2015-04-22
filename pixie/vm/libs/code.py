## This file contains functions for introspecting Code objects

import pixie.vm.rt as rt
from pixie.vm.object import affirm, runtime_error
from pixie.vm.code import as_var
import pixie.vm.code as code
from pixie.vm.keyword import keyword
from pixie.vm.persistent_hash_map import EMPTY as EMPTY_MAP
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR, vector__args as vector
from rpython.rlib.rarithmetic import intmask


acc = EMPTY_MAP

for idx in range(len(code.BYTECODES)):
    bc = unicode(code.BYTECODES[idx])
    as_var(u"pixie.code", bc)(rt.wrap(idx))

    acc = acc.assoc(keyword(bc), rt.wrap(idx))

as_var(u"pixie.code", u"bytecodes")(acc)


@as_var(u"pixie.code", u"introspect")
def introspect(code_obj):
    """Disassembles a code object into a hashmap"""

    acc = EMPTY_MAP


    if isinstance(code_obj, code.Code):
        acc = acc.assoc(keyword(u"type"), keyword(u"code"))
        acc = acc.assoc(keyword(u"arity"), rt.wrap(intmask(code_obj._arity)))


        bc_acc = EMPTY_VECTOR
        for x in code_obj._bytecode:
            bc_acc = bc_acc.conj(rt.wrap(intmask(x)))

        acc = acc.assoc(keyword(u"bytecode"), bc_acc)

        acc = acc.assoc(keyword(u"name"), rt.wrap(code_obj._name))


        consts_acc = EMPTY_VECTOR
        for x in code_obj._consts:
            consts_acc = consts_acc.conj(x)

        acc = acc.assoc(keyword(u"consts"), consts_acc)

        acc = acc.assoc(keyword(u"stack-size"), rt.wrap(intmask(code_obj._stack_size)))

        debug_acc = EMPTY_MAP
        for loc in code_obj._debug_points:
            val = code_obj._debug_points[loc]

            debug_acc = debug_acc.assoc(rt.wrap(intmask(loc)), val)


        acc = acc.assoc(keyword(u"debug-points"), debug_acc)

        acc = acc.assoc(keyword(u"meta"), code_obj._meta)

    elif isinstance(code_obj, code.MultiArityFn):
        acc = acc.assoc(keyword(u"type"), keyword(u"multi"))

        acc = acc.assoc(keyword(u"name"), rt.wrap(code_obj._name))

        acc = acc.assoc(keyword(u"required-arity"), rt.wrap(intmask(code_obj._required_arity)))

        if code_obj._rest_fn:
            acc = acc.assoc(keyword(u"rest-fn"), introspect.invoke([code_obj._rest_fn]))

        acc = acc.assoc(keyword(u"meta"), code_obj._meta)

        arities_acc = EMPTY_MAP

        for arity in code_obj._arities:
            f = code_obj._arities[arity]

            arities_acc = arities_acc.assoc(rt.wrap(intmask(arity)), introspect.invoke([f]))

        acc = acc.assoc(keyword(u"arities"), arities_acc)

    elif isinstance(code_obj, code.VariadicCode):
        acc = acc.assoc(keyword(u"type"), keyword(u"variadic"))

        acc = acc.assoc(keyword(u"required-arity"), rt.wrap(intmask(code_obj._required_arity)))

        acc = acc.assoc(keyword(u"code"), introspect.invoke([code_obj._code]))

        acc = acc.assoc(keyword(u"meta"), code_obj._meta)

    elif isinstance(code_obj, code.NativeFn):
        acc = acc.assoc(keyword(u"type"), keyword(u"native"))


        acc = acc.assoc(keyword(u"name"), rt.wrap(code_obj._fn_name))

    elif isinstance(code_obj, code.PolymorphicFn):
        acc = acc.assoc(keyword(u"type"), keyword(u"polymorphic"))

        acc = acc.assoc(keyword(u"name"), rt.wrap(code_obj._name))

        proto_vec = EMPTY_VECTOR
        for x in code_obj._protos:
            proto_vec = proto_vec.conj(x)

        acc = acc.assoc(keyword(u"protos"), proto_vec)

        acc = acc.assoc(keyword(u"protocol"), code_obj._protocol)

        proto_map = EMPTY_MAP
        for k, v in code_obj._dict.iteritems():
            proto_map = proto_map.assoc(k, introspect.invoke([v]))

        acc = acc.assoc(keyword(u"dict"), proto_map)

        if not isinstance(code_obj._default_fn, code.DefaultProtocolFn):
            acc = acc.assoc(keyword(u"default-fn"), introspect.invoke([code_obj._default_fn]))

    elif isinstance(code_obj, code.DoublePolymorphicFn):
        acc = acc.assoc(keyword(u"type"), keyword(u"double-polymorphic"))

        acc = acc.assoc(keyword(u"name"), rt.wrap(code_obj._name))

        acc = acc.assoc(keyword(u"protocol"), code_obj._protocol)

        proto_map = EMPTY_MAP
        for tp1, d in code_obj._dict.iteritems():
            for tp2, v in d.iteritems():
                proto_map = proto_map.assoc(vector.invoke([tp1, tp2]), introspect.invoke([v]))

        acc = acc.assoc(keyword(u"dict"), proto_map)

        if not isinstance(code_obj._default_fn, code.DefaultProtocolFn):
            acc = acc.assoc(keyword(u"default-fn"), introspect.invoke([code_obj._default_fn]))

    elif isinstance(code_obj, code.Closure):
        acc = acc.assoc(keyword(u"type"), keyword(u"closure"))
        acc = acc.assoc(keyword(u"code"), introspect.invoke([code_obj._code]))

        closed_overs = EMPTY_VECTOR
        for x in code_obj._closed_overs:
            closed_overs = closed_overs.conj(x)

        acc = acc.assoc(keyword(u"closed-overs"), closed_overs)

        acc = acc.assoc(keyword(u"meta"), code_obj._meta)

    else:
        runtime_error(u"Invalid fn type")

    acc = acc.assoc(keyword(u"inst"), code_obj)

    return acc


