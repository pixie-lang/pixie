import pixie.vm2.interpreter as ast
import pixie.vm2.code as code
from pixie.vm2.keyword import keyword
from pixie.vm2.symbol import symbol
from pixie.vm2.primitives import true, false, nil
from pixie.vm2.array import Array
from pixie.vm2.string import char_cache
import pixie.vm2.rt as rt

class Reader(object):
    def __init__(self, filename):
        self._file = open(filename, "rb")
        self._cache = []

    def __del__(self):
        self._file.close()

    def read(self):
        return ord(self._file.read(1)[0])

    def get_cache_idx(self):
        idx = len(self._cache)
        self._cache.append(None)

        return idx

    def set_cache(self, idx, obj):
        self._cache[idx] = obj

    def get_cache(self, idx):
        return self._cache[idx]



bytecodes = ["CACHED_OBJECT",
             "INT",
             "FLOAT",
             "INT_STRING",
             "STRING",
             "TRUE",
             "FALSE",
             "NIL",
             "VAR",
             "KEYWORD",
             "SYMBOL",
             "NEW_CACHED_OBJECT",
             "DO",
             "INVOKE",
             "VAR",
             "CONST",
             "FN",
             "LOOKUP",
             "IF",
             "LET",
             "META",
             "LINE_META",
             "VAR_CONST",
             "CHAR"]

for idx, x in enumerate(bytecodes):
    globals()[x] = idx


def read_utf8_char(os):
    ch = os.read()

    if ch <= 0x7F:
        n = ch
        bytes = 1
    elif (ch & 0xE0) == 0xC0:
        n = ch & 31
        bytes = 2
    elif (ch & 0xF0) == 0xE0:
        n = ch & 15
        bytes = 3
    elif (ch & 0xF8) == 0xF0:
        n = ch & 7
        bytes = 4
    else:
        raise AssertionError("Bad unicode character " + str(ch))

    i = bytes - 1
    while i > 0:

        i -= 1
        n = (n << 6) | (os.read() & 0x3F)

    return unichr(n)

def read_raw_int(os):
    return os.read() | (os.read() << 8) | (os.read() << 16) | (os.read() << 24)



def read_raw_string(os):
    buf = []
    for x in range(read_raw_int(os)):
        buf.append(read_utf8_char(os))

    return u"".join(buf)

def read_raw_list(os):
    vals = [None] * read_raw_int(os)
    for x in range(len(vals)):
        vals[x] = read_object(os)
    return vals

def read_object(os):
    tag = os.read()

    if tag == DO:
        statements = [None] * read_raw_int(os)
        for x in range(len(statements)):
            statements[x] = read_object(os)

        meta = read_object(os)
        return ast.Do(statements, meta)

    elif tag == INVOKE:
        args = [None] * read_raw_int(os)
        for x in range(len(args)):
            args[x] = read_object(os)

        meta = read_object(os)
        return ast.Invoke(args, meta=meta)

    elif tag == NEW_CACHED_OBJECT:
        idx = os.get_cache_idx()
        o = read_object(os)
        os.set_cache(idx, o)
        return o

    elif tag == VAR:
        ns = read_raw_string(os)
        name = read_raw_string(os)
        return ast.VDeref(code.intern_var(ns, name))


    elif tag == VAR_CONST:
        ns = read_raw_string(os)
        name = read_raw_string(os)
        return ast.Const(code.intern_var(ns, name), nil)

    elif tag == CONST:
        return ast.Const(read_object(os))

    elif tag == CACHED_OBJECT:
        return os.get_cache(read_raw_int(os))

    elif tag == FN:
        name_str = read_raw_string(os)
        name = keyword(name_str)
        args = read_raw_list(os)
        closed_overs = read_raw_list(os)
        body = read_object(os)
        meta = read_object(os)
        return ast.Fn(name=name, args=args, body=body, closed_overs=closed_overs, meta=meta)

    elif tag == LOOKUP:
        return ast.Lookup(read_object(os), read_object(os))

    elif tag == KEYWORD:
        return keyword(read_raw_string(os))

    elif tag == SYMBOL:
        return symbol(read_raw_string(os))

    elif tag == FALSE:
        return false

    elif tag == TRUE:
        return true

    elif tag == NIL:
        return nil

    elif tag == INT:
        return rt.wrap(read_raw_int(os))

    elif tag == INT_STRING:
        s = read_raw_string(os)
        return rt.wrap(int(s))

    elif tag == IF:
        return ast.If(read_object(os),
                      read_object(os),
                      read_object(os),
                      read_object(os))

    elif tag == LET:
        bc = read_raw_int(os)
        names = [None] * bc
        values = [None] * bc
        for idx in range(bc):
            names[idx] = read_object(os)
            values[idx] = read_object(os)

        body = read_object(os)
        meta = read_object(os)
        return ast.Let(names=names, bindings=values, body=body, meta=meta)

    elif tag == META:
        line = read_object(os)
        assert isinstance(line, ast.Meta)
        col = read_raw_int(os)
        return ast.Meta(line._c_line_tuple, col)

    elif tag == LINE_META:
        file = read_raw_string(os)
        line = read_raw_string(os)
        line_number = read_raw_int(os)
        return ast.Meta((line, file, line_number), 0)

    elif tag == STRING:
        str = read_raw_string(os)
        return rt.wrap(str)

    elif tag == CHAR:
        str = read_raw_string(os)
        return char_cache.intern(ord(str[0]))

    raise AssertionError("No valid handler for TAG " + bytecodes[tag])


def read_file(filename):
    return read_object(Reader(filename))


