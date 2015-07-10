from pixie.vm.libs.pxic.tags import *
from pixie.vm.object import runtime_error, get_type_by_name
from rpython.rlib.runicode import str_decode_utf_8
from pixie.vm.string import String
from pixie.vm.keyword import Keyword, keyword
from pixie.vm.symbol import Symbol, symbol
from pixie.vm.numbers import Integer, Float, BigInteger
from pixie.vm.code import Code, Var, NativeFn, Namespace, intern_var
import pixie.vm.code as code
from pixie.vm.primitives import nil, true, false
from pixie.vm.persistent_hash_map import EMPTY as EMPTY_MAP
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR
from pixie.vm.persistent_list import create_from_list
from pixie.vm.reader import LinePromise
from rpython.rlib.rarithmetic import r_uint, intmask
from rpython.rlib.rbigint import rbigint
from pixie.vm.libs.pxic.util import read_handlers
import pixie.vm.rt as rt


class Reader(object):
    def __init__(self, rdr):
        self._rdr = rdr
        self._obj_cache = {}
        self._str_cache = {}

    def read(self, num=r_uint(1)):
        return self._rdr.read(intmask(num))

    def read_and_cache(self):
        idx = len(self._obj_cache)
        self._obj_cache[idx] = None # To match cache size growth of writer
        obj = read_obj(self)
        self._obj_cache[idx] = obj
        return obj

    def read_cached_string(self):
        sz = read_raw_integer(self)
        if sz >= MAX_STRING_SIZE:
            return self._str_cache[sz - MAX_STRING_SIZE]
        else:
            s, pos = str_decode_utf_8(self.read(sz), sz, "?")
            self._str_cache[len(self._str_cache)] = s
            return s

    def read_cached_obj(self):
        idx = read_raw_integer(self)
        return self._obj_cache[idx]


def read_tag(rdr):
    tag = rdr.read()
    return ord(tag[0])

def read_raw_integer(rdr):
    return r_uint(ord(rdr.read()[0]) | (ord(rdr.read()[0]) << 8) | (ord(rdr.read()[0]) << 16) | (ord(rdr.read()[0]) << 24))

def read_raw_bigint(rdr):
    nchars = read_raw_integer(rdr)
    n = rbigint.fromint(0)
    for i in range(nchars):
        a = rbigint.fromint(ord(rdr.read()[0]))
        a = a.lshift(8*i)
        n = n.add(a)
    return n

def read_raw_string(rdr):
    s = rdr.read_cached_string()
    return s

def read_code(rdr):
    sz = read_raw_integer(rdr)
    bytecode = [r_uint(0)] * sz
    for x in range(sz):
        bytecode[x] = read_raw_integer(rdr)

    sz = read_raw_integer(rdr)
    consts = [None] * sz
    for x in range(sz):
        consts[x] = read_obj(rdr)

    stack_size = read_raw_integer(rdr)

    nm = read_raw_string(rdr)

    arity = read_raw_integer(rdr)

    dps = read_raw_integer(rdr)
    debug_points = {}
    for x in range(dps):
        idx = read_raw_integer(rdr)
        debug_points[idx] = read_obj(rdr)

    return Code(nm, arity, bytecode, consts, stack_size, debug_points)


def read_var(rdr):
    ns = read_raw_string(rdr)
    nm = read_raw_string(rdr)
    is_dynamic = read_tag(rdr)
    var = intern_var(ns, nm)
    if is_dynamic is TRUE:
        var.set_dynamic()
    return var

def read_map(rdr):
    cnt = read_raw_integer(rdr)
    acc = EMPTY_MAP
    for x in range(cnt):
        acc = rt._assoc(acc, read_obj(rdr), read_obj(rdr))

    return acc

def read_vector(rdr):
    cnt = read_raw_integer(rdr)
    acc = EMPTY_VECTOR
    for x in range(cnt):
        acc = rt._conj(acc, read_obj(rdr))

    return acc

def read_seq(rdr):
    cnt = read_raw_integer(rdr)
    lst = [None] * cnt
    for x in range(cnt):
        lst[x] = read_obj(rdr)

    return create_from_list(lst)

def read_float(rdr):
    return Float(float(str(read_raw_string(rdr))))

def read_namespace(rdr):
    nm = read_raw_string(rdr)
    return code._ns_registry.find_or_make(nm)

def read_interpreter_code_info(rdr):
    from pixie.vm.object import InterpreterCodeInfo
    line = read_obj(rdr)
    line_number = read_raw_integer(rdr)
    column_number = read_raw_integer(rdr)
    file = read_raw_string(rdr)
    return InterpreterCodeInfo(line, intmask(line_number), intmask(column_number), file)

def read_obj(rdr):
    tag = read_tag(rdr)

    if tag == INT:
        return Integer(intmask(read_raw_integer(rdr)))
    elif tag == BIGINT:
        return BigInteger(read_raw_bigint(rdr))
    elif tag == CODE:
        return read_code(rdr)
    elif tag == NIL:
        return nil
    elif tag == VAR:
        return read_var(rdr)
    elif tag == STRING:
        return String(read_raw_string(rdr))
    elif tag == KEYWORD:
        return keyword(read_raw_string(rdr))
    elif tag == SYMBOL:
        return symbol(read_raw_string(rdr))
    elif tag == LINE_PROMISE:
        lp = LinePromise()
        lp._chrs = None
        lp._str = read_raw_string(rdr)
        return lp
    elif tag == MAP:
        return read_map(rdr)
    elif tag == TRUE:
        return true
    elif tag == FALSE:
        return false
    elif tag == NIL:
        return nil
    elif tag == VECTOR:
        return read_vector(rdr)
    elif tag == SEQ:
        return read_seq(rdr)
    elif tag == FLOAT:
        return read_float(rdr)
    elif tag == NAMESPACE:
        return read_namespace(rdr)
    elif tag == INT_STRING:
        return Integer(int(read_raw_string(rdr)))
    elif tag == BIGINT_STRING:
        return BigInteger(rbigint.fromstr(str(read_raw_string(rdr))))


    elif tag == NEW_CACHED_OBJ:
        return rdr.read_and_cache()
    elif tag == CACHED_OBJ:
        return rdr.read_cached_obj()

    elif tag == EOF:
        from pixie.vm.reader import eof
        return eof

    elif tag == CODE_INFO:
        return read_interpreter_code_info(rdr)

    elif tag == TAGGED:
        tp_name = read_raw_string(rdr)
        tp = get_type_by_name(tp_name)
        handler = read_handlers.get(tp, None)
        if handler is None:
            runtime_error(u"No type handler for " + tp_name)

        obj = read_obj(rdr)
        return handler.invoke([obj])
    else:
        runtime_error(u"No dispatch for bytecode: " + unicode(tag_name[tag]))

    return nil
