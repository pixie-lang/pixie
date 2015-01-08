from pixie.vm.libs.pxic.tags import *
from pixie.vm.object import runtime_error
from rpython.rlib.runicode import unicode_encode_utf_8, str_decode_utf_8
from pixie.vm.string import String
from pixie.vm.keyword import Keyword, keyword
from pixie.vm.symbol import Symbol, symbol
from pixie.vm.numbers import Integer, Float
from pixie.vm.code import Code, Var, NativeFn, Namespace, intern_var
import pixie.vm.code as code
from pixie.vm.primitives import nil, true, false
from pixie.vm.persistent_hash_map import EMPTY as EMPTY_MAP
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR
from pixie.vm.persistent_list import create_from_list
from pixie.vm.reader import LinePromise
import pixie.vm.rt as rt


class Reader(object):
    def __init__(self, rdr):
        self._rdr = rdr
        self._obj_cache = {}

    def read(self, num=1):
        return self._rdr.read(num)

    def read_cached(self):
        obj = read_obj(self)
        self._obj_cache[len(self._obj_cache)] = obj
        return obj

    def read_cached_obj(self):
        idx = read_raw_integer(self)
        return self._obj_cache[idx]


def read_tag(rdr):
    tag = rdr.read()
    return ord(tag)

def read_raw_integer(rdr):
    return ord(rdr.read()) | (ord(rdr.read()) << 8) | (ord(rdr.read()) << 16) | (ord(rdr.read()) << 24)

def read_raw_string(rdr):
    sz = read_raw_integer(rdr)
    return unicode(rdr.read(sz))

def read_code(rdr):
    sz = read_raw_integer(rdr)
    bytecode = [0] * sz
    for x in range(sz):
        bytecode[x] = read_raw_integer(rdr)

    sz = read_raw_integer(rdr)
    consts = [None] * sz
    for x in range(sz):
        consts[x] = read_obj(rdr)

    stack_size = read_raw_integer(rdr)

    nm = read_raw_string(rdr)

    return Code(nm, bytecode, consts, stack_size, {})


def read_var(rdr):
    ns = read_raw_string(rdr)
    nm = read_raw_string(rdr)
    return intern_var(ns, nm)

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
    return Float(float(read_raw_string(rdr)))

def read_namespace(rdr):
    nm = read_raw_string(rdr)
    return code._ns_registry.find_or_make(nm)

def read_obj(rdr):
    tag = read_tag(rdr)

    if tag == INT:
        return Integer(read_raw_integer(rdr))
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
        lp._str = read_raw_string(rdr)
        return rdr
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


    elif tag == NEW_CACHED_OBJ:
        return rdr.read_cached()
    elif tag == CACHED_OBJ:
        return rdr.read_cached_obj()

    elif tag == EOF:
        from pixie.vm.reader import eof
        return eof
    else:
        runtime_error(u"No dispatch for bytecode: " + unicode(tag_name[tag]))
