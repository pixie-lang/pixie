from pixie.vm.libs.pxic.tags import *
from pixie.vm.object import runtime_error, Object, Type
from rpython.rlib.runicode import unicode_encode_utf_8
from pixie.vm.string import String
from pixie.vm.keyword import Keyword
from pixie.vm.symbol import Symbol
from pixie.vm.numbers import Integer, Float
from pixie.vm.code import Code, Var, NativeFn, Namespace
from pixie.vm.primitives import nil, true, false
from pixie.vm.reader import LinePromise
from rpython.rlib.objectmodel import specialize
from rpython.rlib.rarithmetic import r_uint
import pixie.vm.rt as rt

MAX_INT32 = r_uint(1 << 32)

class Writer(object):
    def __init__(self, wtr, with_cache=False):
        self._wtr = wtr
        self._obj_cache = {}
        self._with_cache = with_cache

    def write(self, s):
        assert isinstance(s, str)
        self._wtr.write(s)

    def flush(self):
        self._wtr.flush()

    def write_cached_obj(self, o, wfn):
        if self._with_cache:
            idx = self._obj_cache.get(o, -1)
            if idx == -1:
                idx = len(self._obj_cache)
                self._obj_cache[o] = idx
                write_tag(NEW_CACHED_OBJ, self)
                wfn(o, self)
            else:
                write_tag(CACHED_OBJ, self)
                write_int_raw(idx, self)
        else:
            return wfn(o, self)

    def write_object(self, o):
        write_object(o, self)

    def finish(self):
        write_tag(EOF, self)
        self._wtr.flush()

class WriterBox(Object):
    _type = Type(u"pixie.stdlib.WriterBox")
    def type(self):
        return WriterBox._type

    def __init__(self, wtr):
        self._pxic_writer = wtr

    def get_pxic_writer(self):
        return self._pxic_writer

def write_tag(tag, wtr):
    assert tag <= 0xFF
    wtr.write(chr(tag))

def write_int_raw(i, wtr):
    #if 0 <= i <= SMALL_INT_MAX:
    #    wtr.write(chr((i & 0xFF) + SMALL_INT_START))
    if 0 <= i <= MAX_INT32:
        wtr.write(chr(i & 0xFF))
        wtr.write(chr((i >> 8) & 0xFF))
        wtr.write(chr((i >> 16) & 0xFF))
        wtr.write(chr((i >> 24) & 0xFF))
    else:
        runtime_error(u"Raw int must be less than MAX_INT32, got: " + unicode(str(i)))

def write_string_raw(si, wtr):
    assert isinstance(si, unicode)
    errors = "?"
    s = unicode_encode_utf_8(si, len(si), errors)
    assert len(s) <= MAX_INT32
    write_int_raw(len(s), wtr)
    wtr.write(s)

def write_int(i, wtr):
    if 0 <= i <= MAX_INT32:
        wtr.write(chr(INT))
        write_int_raw(i, wtr)
    else:
        wtr.write(chr(INT_STRING))
        write_string_raw(unicode(str(i)), wtr)

def write_float(f, wtr):
    write_tag(FLOAT, wtr)
    write_string_raw(unicode(str(f)), wtr)

def write_string(s, wtr):
    write_tag(STRING, wtr)
    write_string_raw(s, wtr)

def write_code(c, wtr):
    assert isinstance(c, Code)
    wtr.write(chr(CODE))

    write_int_raw(len(c._bytecode), wtr)
    for i in c._bytecode:
        write_int_raw(i, wtr)

    write_int_raw(len(c._consts), wtr)
    for const in c._consts:
        write_object(const, wtr)

    write_int_raw(c._stack_size, wtr)


    write_string_raw(c._name, wtr)


class WriteParirFn(NativeFn):
    def __init__(self, wtr):
        self._wtr = wtr

    def invoke(self, args):
        kv = args[1]

        write_object(rt._key(kv), self._wtr)
        write_object(rt._val(kv), self._wtr)

        return nil


def write_map(mp, wtr):
    write_tag(MAP, wtr)
    write_int_raw(rt.count(mp), wtr)

    rt._reduce(mp, WriteParirFn(wtr), nil)

class WriteItem(NativeFn):
    def __init__(self, wtr):
        self._wtr = wtr

    def invoke(self, args):
        itm = args[1]

        write_object(itm, self._wtr)

        return nil


def write_vector(vec, wtr):
    write_tag(VECTOR, wtr)
    write_int_raw(rt.count(vec), wtr)

    rt._reduce(vec, WriteItem(wtr), nil)

def write_seq(s, wtr):
    write_tag(SEQ, wtr)
    write_int_raw(rt.count(s), wtr)

    s = rt.seq(s)

    while s is not nil:
        write_object(rt.first(s), wtr)
        s = rt.next(s)




#   def __init__(self, name, bytecode, consts, stack_size, debug_points, meta=nil):
#        BaseCode.__init__(self)
#        self._bytecode = bytecode
#        self._consts = consts
#        self._name = name
#        self._stack_size = stack_size
#        self._debug_points = debug_points
#        self._meta = meta

def write_var(var, wtr):
    assert isinstance(var, Var)
    write_tag(VAR, wtr)
    write_string_raw(var._ns, wtr)
    write_string_raw(var._name, wtr)
    write_tag(TRUE if var.is_dynamic() else FALSE, wtr)


def write_keyword(kw, wtr):
    assert isinstance(kw, Keyword)
    write_tag(KEYWORD, wtr)
    write_string_raw(kw._str, wtr)

def write_symbol(sym, wtr):
    assert isinstance(sym, Symbol)
    write_tag(SYMBOL, wtr)
    write_string_raw(sym._str, wtr)

def write_line_promise(o, wtr):
    assert isinstance(o, LinePromise)
    write_tag(LINE_PROMISE, wtr)
    o.finalize()
    write_string_raw(o._str, wtr)

def write_namespace(o, wtr):
    assert isinstance(o, Namespace)
    write_tag(NAMESPACE, wtr)
    write_string_raw(o._name, wtr)


def write_object(obj, wtr):
    wtr.flush()
    if isinstance(obj, String):
        write_string(rt.name(obj), wtr)
    elif isinstance(obj, Integer):
        write_int(obj.int_val(), wtr)
    elif isinstance(obj, Float):
        write_float(obj.float_val(), wtr)
    elif isinstance(obj, Code):
        write_code(obj, wtr)
    elif obj is nil:
        wtr.write(chr(NIL))
    elif isinstance(obj, Var):
        #wtr.write_cached_obj(obj, write_var)
        write_var(obj, wtr)
    elif rt.satisfies_QMARK_(rt.IMap.deref(), obj):
        write_map(obj, wtr)
    elif rt.satisfies_QMARK_(rt.IVector.deref(), obj):
        write_vector(obj, wtr)
    elif rt.satisfies_QMARK_(rt.ISeq.deref(), obj):
        write_seq(obj, wtr)
    elif isinstance(obj, Keyword):
        wtr.write_cached_obj(obj, write_keyword)
    elif isinstance(obj, LinePromise):
        wtr.write_cached_obj(obj, write_line_promise)
    elif obj is true:
        write_tag(TRUE, wtr)
    elif obj is false:
        write_tag(FALSE, wtr)
    elif isinstance(obj, Symbol):
        write_symbol(obj, wtr)
    elif isinstance(obj, Namespace):
        wtr.write_cached_obj(obj, write_namespace)
    else:
        from pixie.vm.libs.pxic.util import write_handlers
        handler = write_handlers.get(obj.type(), None)
        if handler is None:
            runtime_error(u"Object is not supported by pxic writer: " + rt.name(rt.str(obj.type())))
        else:
            write_tag(TAGGED, wtr)
            write_string_raw(obj.type().name(), wtr)
            write_object(handler.invoke([obj]), wtr)

