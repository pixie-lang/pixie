py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm, runtime_error
import pixie.vm.code as code
from pixie.vm.primitives import nil, true, false
import pixie.vm.numbers as numbers
from pixie.vm.cons import cons
from pixie.vm.symbol import symbol, Symbol
from pixie.vm.keyword import keyword, Keyword
import pixie.vm.rt as rt
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR
from pixie.vm.libs.libedit import _readline
from pixie.vm.string import Character, String
from pixie.vm.code import wrap_fn, extend
from pixie.vm.persistent_hash_map import EMPTY as EMPTY_MAP
from pixie.vm.persistent_hash_set import EMPTY as EMPTY_SET
from pixie.vm.persistent_list import EmptyList
import pixie.vm.stdlib as proto
import pixie.vm.compiler as compiler

from rpython.rlib.rbigint import rbigint
from rpython.rlib.rsre import rsre_re as re

LINE_NUMBER_KW = keyword(u"line-number")
COLUMN_NUMBER_KW = keyword(u"column-number")
LINE_KW = keyword(u"line")
FILE_KW = keyword(u"file")

GEN_SYM_ENV = code.intern_var(u"pixie.stdlib.reader", u"*gen-sym-env*")
GEN_SYM_ENV.set_dynamic()
GEN_SYM_ENV.set_value(EMPTY_MAP)

ARG_AMP = symbol(u"&")
ARG_MAX = keyword(u"max-arg")
ARG_ENV = code.intern_var(u"pixie.stdlib.reader", u"*arg-env*")
ARG_ENV.set_dynamic()
ARG_ENV.set_value(nil)

class PlatformReader(object.Object):
    _type = object.Type(u"PlatformReader")

    def read(self):
        assert False

    def unread(self, ch):
        pass

    def reset_line(self):
        return self

class StringReader(PlatformReader):

    def __init__(self, s):
        affirm(isinstance(s, unicode), u"StringReader requires unicode")
        self._str = s
        self._idx = 0

    def read(self):
        if self._idx >= len(self._str):
            raise EOFError()
        ch = self._str[self._idx]
        self._idx += 1
        return ch

    def unread(self, ch):
        self._idx -= 1

class PromptReader(PlatformReader):
    def __init__(self):
        self._string_reader = None


    def read(self):
        if self._string_reader is None:
            result = _readline(str(rt.name(compiler.NS_VAR.deref())) + " => ")
            if result == u"":
                raise EOFError()
            self._string_reader = StringReader(result)

        try:
            return self._string_reader.read()
        except EOFError:
            self._string_reader = None
            return self.read()

    def reset_line(self):
        self._string_reader = None

    def unread(self, ch):
        assert self._string_reader is not None
        self._string_reader.unread(ch)

class LinePromise(object.Object):
    _type = object.Type(u"pixie.stdlib.LinePromise")
    def type(self):
        return LinePromise._type

    def __init__(self):
        self._chrs = []
        self._str = None

    def add_char(self, ch):
        self._chrs.append(ch)

    def finalize(self):
        if self._chrs is not None:
            self._str = u"".join(self._chrs)
            self._chrs = None

    def is_finalized(self):
        return self._chrs is None

    def __repr__(self):
        if self.is_finalized():
            return self._str
        return u"".join(self._chrs)



class MetaDataReader(PlatformReader):
    """Creates metadata for use by the debug system"""
    def __init__(self, parent_reader, filename=u"<unknown>"):
        assert isinstance(parent_reader, PlatformReader)
        self._parent_reader = parent_reader
        self._line_number = 1
        self._column_number = 0
        self._line = LinePromise()
        self._has_unread = False
        self._prev_line_number = 1
        self._prev_column_number = 0
        self._prev_line = None
        self._prev_chr = u"\0"
        self._filename = filename
        assert isinstance(self._prev_chr, unicode)

    def read(self):
        if self._has_unread:
            self._has_unread = False
            return self._prev_chr
        else:
            self._prev_column_number = self._column_number
            self._prev_line_number = self._line_number
            self._prev_line = self._line
            ch = self._parent_reader.read()
            if self._line.is_finalized():
                self._line = LinePromise()
            if ch == u'\n':
                self._line.finalize()
                self._line_number += 1
                self._column_number = 0
            else:
                self._line.add_char(ch)
                self._column_number += 1

            self._cur_ch = ch
            return ch

    def reset_line(self):
        self._line.finalize()
        self._line_number += 1
        self._column_number = 0
        self._parent_reader.reset_line()
        return self

    def get_metadata(self):
        return rt.hashmap(LINE_KW, rt.wrap(self._line),
                          LINE_NUMBER_KW, rt.wrap(self._line_number),
                          COLUMN_NUMBER_KW, rt.wrap(self._column_number),
                          FILE_KW, rt.wrap(self._filename))


    def unread(self, ch):
        affirm(not self._has_unread, u"Can't unread twice")
        self._has_unread = True
        self._prev_chr = self._cur_ch
#
#
#     def reader_str_state(self):
#         spaces = []
#         for x in range(self._column_number - 1):
#             spaces.append(u" ")
#
#         return u"in " + self._filename + \
#             u" at " + unicode(str(self._line_number)) + u":" + unicode(str(self._column_number)) + u"\n" \
#                + self._line.reader_string_state() + u"\n" + u"".join(spaces) + u"^"



def is_whitespace(ch):
    return ch in u"\r\n\t ," or ch == u""

def is_digit(ch):
    return ch in u"0123456789"

def is_terminating_macro(ch):
    return ch != u"#" and ch != u"'" and ch != u"%" and ch in handlers

def eat_whitespace(rdr):
    while True:
        ch = rdr.read()
        if is_whitespace(ch):
            continue
        rdr.unread(ch)
        return

class ReaderHandler(py_object):
    def invoke(self, rdr, ch):
        pass

class ListReader(ReaderHandler):
    def invoke(self, rdr, ch):
        lst = []
        while True:
            eat_whitespace(rdr)
            ch = rdr.read()
            if ch == u")":
                if len(lst) == 0:
                    return EmptyList()
                acc = nil
                for x in range(len(lst) - 1, -1, -1):
                    acc = cons(lst[x], acc)
                return acc

            rdr.unread(ch)
            lst.append(read(rdr, True))

class UnmachedListReader(ReaderHandler):
    def invoke(self, rdr, ch):
        throw_syntax_error_with_data(rdr, u"Unmatched list close ')'")

class VectorReader(ReaderHandler):
    def invoke(self, rdr, ch):
        acc = EMPTY_VECTOR
        while True:
            eat_whitespace(rdr)
            ch = rdr.read()
            if ch == u"]":
                return acc

            rdr.unread(ch)
            acc = rt.conj(acc, read(rdr, True))

class UnmachedVectorReader(ReaderHandler):
    def invoke(self, rdr, ch):
        throw_syntax_error_with_data(rdr, u"Unmatched vector close ']'")

class MapReader(ReaderHandler):
    def invoke(self, rdr, ch):
        acc = EMPTY_MAP
        while True:
            eat_whitespace(rdr)
            ch = rdr.read()
            if ch == u"}":
                return acc

            rdr.unread(ch)
            k = read(rdr, True)
            v = read(rdr, False)
            acc = rt._assoc(acc, k, v)
        return acc

class UnmachedMapReader(ReaderHandler):
    def invoke(self, rdr, ch):
        affirm(False, u"Unmatched Map brace ")

class QuoteReader(ReaderHandler):
    def invoke(self, rdr, ch):
        itm = read(rdr, True)
        return cons(symbol(u"quote"), cons(itm))

class KeywordReader(ReaderHandler):
    def invoke(self, rdr, ch):
        itm = read(rdr, True)
        affirm(isinstance(itm, Symbol), u"Can't keyword quote a non-symbol")

        return keyword(rt.name(itm))

class LiteralStringReader(ReaderHandler):
    def invoke(self, rdr, ch):
        acc = []

        # TODO: implement escape characters
        while True:
            try:
                v = rdr.read()
            except EOFError:
                raise Exception("unmatched quote")
            
            if v == "\"":
                return rt.wrap(u"".join(acc))
            elif v == "\\":
                #inside escape... TODO handle everything.
                try:
                    v = rdr.read()
                    if v == "\"":
                        acc.append("\"")
                    elif v == "\\":
                        acc.append("\\")
                    elif v == "n":
                        acc.append("\n")
                    elif v == "r":
                        acc.append("\r")
                    elif v == "t":
                        acc.append("\t")
                    else:
                        raise Exception("unhandled escape character")
                except EOFError:
                    raise Exception("eof after escape character")
            else:
                acc.append(v)

def read_token(rdr):
    acc = u""
    while True:
        ch = rdr.read()
        if is_whitespace(ch) or is_terminating_macro(ch):
            rdr.unread(ch)
            return acc
        acc += ch

def read_unicode_char(rdr, token, offset, length, base):
    if len(token) != offset + length:
        throw_syntax_error_with_data(rdr, u"Invalid unicode character: \\" + token)
    c = 0
    for i in range(offset, offset + length):
        d = int(str(token[i:i+1]), base)
        c = c * base + d
    return c

class LiteralCharacterReader(ReaderHandler):
    def invoke(self, rdr, ch):
        token = read_token(rdr)
        if len(token) == 1:
            return Character(ord(token[0]))
        elif token == u"newline":
            return Character(ord("\n"))
        elif token == u"space":
            return Character(ord(" "))
        elif token == u"tab":
            return Character(ord("\t"))
        elif token == u"backspace":
            return Character(ord("\b"))
        elif token == u"formfeed":
            return Character(ord("\f"))
        elif token == u"return":
            return Character(ord("\r"))
        elif token.startswith("u"):
            c = read_unicode_char(rdr, token, 1, 4, 16)
            if c >= 0xd800 and c <= 0xdfff:
                throw_syntax_error_with_data(rdr, u"Invalid character constant: \\" + token)
            return Character(c)
        elif token.startswith("o"):
            l = len(token) - 1
            if l > 3:
                throw_syntax_error_with_data(rdr, u"Invalid octal escape sequence: \\" + token)
            c = read_unicode_char(rdr, token, 1, l, 8)
            if c > 0377:
                throw_syntax_error_with_data(rdr, u"Octal escape sequences must be in range [0, 377]")
            return Character(c)
        else:
            throw_syntax_error_with_data(rdr, u"Unsupported character: \\" + token)

class DerefReader(ReaderHandler):
    def invoke(self, rdr, ch):
        return rt.cons(symbol(u"-deref"), rt.cons(read(rdr, True), nil))


QUOTE = symbol(u"quote")
UNQUOTE = symbol(u"unquote")
UNQUOTE_SPLICING = symbol(u"unquote-splicing")
APPLY = symbol(u"apply")
CONCAT = symbol(u"concat")
SEQ = symbol(u"seq")
LIST = symbol(u"list")

def is_unquote(form):
    return True if rt.satisfies_QMARK_(rt.ISeq.deref(), form) \
                   and rt.eq(rt.first(form), UNQUOTE) \
           else False

def is_unquote_splicing(form):
    return True if rt.satisfies_QMARK_(rt.ISeq.deref(), form) \
                   and rt.eq(rt.first(form), UNQUOTE_SPLICING) \
           else False

class SyntaxQuoteReader(ReaderHandler):
    def invoke(self, rdr, ch):
        form = read(rdr, True)

        with code.bindings(GEN_SYM_ENV, EMPTY_MAP):
            result = self.syntax_quote(form)

        return result

    @staticmethod
    def syntax_quote(form):
        if isinstance(form, Symbol) and compiler.is_compiler_special(form):
            ret = rt.list(QUOTE, form)

        elif isinstance(form, Symbol):
            if rt.namespace(form) is None and rt.name(form).endswith("#"):
                gmap = rt.deref(GEN_SYM_ENV)
                affirm(gmap is not nil, u"Gensym literal used outside a syntax quote")
                gs = rt.get(gmap, form)
                if gs is nil:
                    gs = rt.symbol(rt.str(form, rt.wrap(u"__"), rt.gensym()))
                    GEN_SYM_ENV.set_value(rt.assoc(gmap, form, gs))
                form = gs
            else:
                var = rt.resolve_in(compiler.NS_VAR.deref(), form)
                if var is nil:
                    form = rt.symbol(rt.str(rt.wrap(rt.name(rt.deref(compiler.NS_VAR))), rt.wrap(u"/"), form))
                else:
                    form = rt.symbol(rt.str(rt.wrap(rt.namespace(var)), rt.wrap(u"/"), rt.str(rt.wrap(rt.name(var)))))
            ret = rt.list(QUOTE, form)
        elif is_unquote(form):
            ret = rt.first(rt.next(form))
        elif is_unquote_splicing(form):
            raise Exception("Unquote splicing not used inside list")
        elif rt.vector_QMARK_(form) is true:
            ret = rt.list(APPLY, CONCAT, SyntaxQuoteReader.expand_list(form))
        elif form is not nil and rt.seq_QMARK_(form) is true:
            ret = rt.list(APPLY, LIST, rt.cons(CONCAT, SyntaxQuoteReader.expand_list(rt.seq(form))))
        else:
            ret = rt.list(QUOTE, form)
        return ret

    @staticmethod
    def expand_list(form):
        return rt.reduce(expand_list_rfn, EMPTY_VECTOR, form)

@wrap_fn
def expand_list_rfn(ret, item):
    if is_unquote(item):
        ret = rt.conj(ret, rt.vector(rt.first(rt.next(item))))
    elif is_unquote_splicing(item):
        ret = rt.conj(ret, rt.first(rt.next(item)))
    else:
        ret = rt.conj(ret, rt.vector(SyntaxQuoteReader.syntax_quote(item)))
    return ret

class UnquoteReader(ReaderHandler):
    def invoke(self, rdr, ch):
        ch = rdr.read()
        sym = UNQUOTE
        if ch == "@":
            sym = UNQUOTE_SPLICING
        else:
            rdr.unread(ch)

        form = read(rdr, True)
        return rt.list(sym, form)

class MetaReader(ReaderHandler):
    def invoke(self, rdr, ch):
        meta = read(rdr, True)
        obj = read(rdr, True)

        if isinstance(meta, Keyword):
            meta = rt.hashmap(meta, true)

        if isinstance(meta, Symbol):
            meta = rt.hashmap(keyword(u"tag"), meta)

        if rt.satisfies_QMARK_(rt.IMeta.deref(), obj):
            return rt.with_meta(obj, rt.merge(meta, rt.meta(obj)))

        return obj

class ArgReader(ReaderHandler):
    def invoke(self, rdr, ch):
        if ARG_ENV.deref() is nil:
            return read_symbol(rdr, ch)

        ch = rdr.read()
        rdr.unread(ch)
        if is_whitespace(ch) or is_terminating_macro(ch):
            return ArgReader.register_next_arg(1)

        n = read(rdr, True)
        if rt.eq(n, ARG_AMP):
            return ArgReader.register_next_arg(-1)
        if not isinstance(n, numbers.Integer):
            throw_syntax_error_with_data(rdr, u"%-arg must be %, %<integer> or %&")
        return ArgReader.register_next_arg(n.int_val())

    @staticmethod
    def register_next_arg(n):
        arg_env = ARG_ENV.deref()
        max_arg = rt.get(arg_env, ARG_MAX)
        if n > max_arg.int_val():
            arg_env = rt.assoc(arg_env, ARG_MAX, rt.wrap(n))

        arg = rt.get(arg_env, rt.wrap(n), nil)
        if arg is nil:
            arg = ArgReader.gen_arg(n)
            arg_env = rt.assoc(arg_env, rt.wrap(n), arg)
        ARG_ENV.set_value(arg_env)
        return arg

    @staticmethod
    def gen_arg(n):
        s = unicode(str(n))
        if n == -1:
            s = u"_rest"
        return rt.gensym(rt.wrap(u"arg" + s + u"__"))

class FnReader(ReaderHandler):
    def invoke(self, rdr, ch):
        if ARG_ENV.deref() is not nil:
            throw_syntax_error_with_data(rdr, u"Nested #()s are not allowed")

        try:
            ARG_ENV.set_value(rt.assoc(EMPTY_MAP, ARG_MAX, rt.wrap(-1)))

            rdr.unread(ch)
            form = read(rdr, True)

            args = EMPTY_VECTOR
            percent_args = ARG_ENV.deref()
            max_arg = rt.get(percent_args, ARG_MAX)

            for i in range(1, max_arg.int_val() + 1):
                arg = rt.get(percent_args, rt.wrap(i))
                if arg is nil:
                    arg = ArgReader.gen_arg(i)
                args = rt.conj(args, arg)

            rest_arg = rt.get(percent_args, rt.wrap(-1))
            if rest_arg is not nil:
                args = rt.conj(args, ARG_AMP)
                args = rt.conj(args, rest_arg)

            return rt.cons(symbol(u"fn*"), rt.cons(args, rt.cons(form, nil)))
        finally:
            ARG_ENV.set_value(nil)

class SetReader(ReaderHandler):
    def invoke(self, rdr, ch):
        acc = EMPTY_SET
        while True:
            eat_whitespace(rdr)
            ch = rdr.read()
            if ch == u"}":
                return acc

            rdr.unread(ch)
            acc = acc.conj(read(rdr, True))

dispatch_handlers = {
    u"{":  SetReader(),
    u"(": FnReader()
}

class DispatchReader(ReaderHandler):
    def invoke(self, rdr, ch):
        ch = rdr.read()
        handler = dispatch_handlers[ch]
        if handler is None:
            raise Exception("unknown dispatch #" + ch)
        return handler.invoke(rdr, ch)

class LineCommentReader(ReaderHandler):
    def invoke(self, rdr, ch):
        self.skip_line(rdr)
        return read(rdr, True)

    def skip_line(self, rdr):
        while True:
            ch = rdr.read()
            if ch == u"\n":
                return
            elif ch == u"\r":
                ch2 = rdr.read()
                if ch2 == u"\n":
                    return

handlers = {u"(": ListReader(),
            u")": UnmachedListReader(),
            u"[": VectorReader(),
            u"]": UnmachedVectorReader(),
            u"{": MapReader(),
            u"}": UnmachedMapReader(),
            u"'": QuoteReader(),
            u":": KeywordReader(),
            u"\"": LiteralStringReader(),
            u"\\": LiteralCharacterReader(),
            u"@": DerefReader(),
            u"`": SyntaxQuoteReader(),
            u"~": UnquoteReader(),
            u"^": MetaReader(),
            u"#": DispatchReader(),
            u";": LineCommentReader(),
            u"%": ArgReader()
}

# inspired by https://github.com/clojure/tools.reader/blob/9ee11ed/src/main/clojure/clojure/tools/reader/impl/commons.clj#L45
#                           sign      hex                    oct      radix                           decimal  biginteger
#                           1         2      3               4        5                 6             7        8
int_matcher = re.compile(u'^([-+]?)(?:(0[xX])([0-9a-fA-F]+)|0([0-7]+)|([1-9][0-9]?)[rR]([0-9a-zA-Z]+)|([0-9]*))(N)?$')

float_matcher = re.compile(u'^([-+]?[0-9]+(\.[0-9]*)?([eE][-+]?[0-9]+)?)$')
ratio_matcher = re.compile(u'^([-+]?[0-9]+)/([0-9]+)$')

def parse_int(m):
    sign = 1
    if m.group(1) == u'-':
        sign = -1

    radix = 10

    if m.group(7):
        num = m.group(7)
    elif m.group(2):
        radix = 16
        num = m.group(3)
    elif m.group(4):
        radix = 8
        num = m.group(4)
    elif m.group(5):
        radix = int(m.group(5))
        num = m.group(6)
    else:
        return None

    if m.group(8):
        return rt.wrap(rbigint.fromstr(str(m.group(1) + num), radix))
    else:
        return rt.wrap(sign * int(str(num), radix))

def parse_float(m):
    return rt.wrap(float(str(m.group(0))))

def parse_ratio(m):
    n = rt.wrap(int(str(m.group(1))))
    d = rt.wrap(int(str(m.group(2))))
    return rt._div(n, d)

def parse_number(s):
    m = int_matcher.match(s)
    if m:
        return parse_int(m)
    else:
        m = float_matcher.match(s)
        if m:
            return parse_float(m)
        else:
            m = ratio_matcher.match(s)
            if m:
                return parse_ratio(m)
            else:
                return None

def read_number(rdr, ch):
    acc = [ch]
    try:
        while True:
            ch = rdr.read()
            if is_whitespace(ch) or ch in handlers:
                rdr.unread(ch)
                break
            acc.append(ch)
    except EOFError:
        pass

    joined = u"".join(acc)
    parsed = parse_number(joined)
    if parsed is not None:
        return parsed
    return Symbol(joined)

def read_symbol(rdr, ch):
    acc = [ch]
    try:
        while True:
            ch = rdr.read()
            if is_whitespace(ch) or is_terminating_macro(ch):
                rdr.unread(ch)
                break
            acc.append(ch)
    except EOFError:
        pass

    sym_str = u"".join(acc)
    if sym_str == u"true":
        return true
    if sym_str == u"false":
        return false
    if sym_str == u"nil":
        return nil
    return symbol(sym_str)

class EOF(object.Object):
    _type = object.Type(u"EOF")


eof = EOF()




def throw_syntax_error_with_data(rdr, txt):
    assert isinstance(txt, unicode)
    if isinstance(rdr, MetaDataReader):
        meta = rdr.get_metadata()
    else:
        meta = nil

    data = rt.interpreter_code_info(meta)
    err = object.RuntimeException(rt.wrap(txt))
    err._trace.append(data)
    raise object.WrappedException(err)


def read(rdr, error_on_eof):
    try:
        eat_whitespace(rdr)
    except EOFError as ex:
        if error_on_eof:
            runtime_error("Unexpected EOF while reading")
        return eof



    ch = rdr.read()
    if isinstance(rdr, MetaDataReader):
        meta = rdr.get_metadata()
    else:
        meta = nil

    macro = handlers.get(ch, None)
    if macro is not None:
        itm = macro.invoke(rdr, ch)

    elif is_digit(ch):
        itm = read_number(rdr, ch)

    elif ch == u"-":
        ch2 = rdr.read()
        if is_digit(ch2):
            rdr.unread(ch2)
            itm = read_number(rdr, ch)

        else:
            rdr.unread(ch2)
            itm = read_symbol(rdr, ch)

    else:
        itm = read_symbol(rdr, ch)

    if rt.has_meta_QMARK_(itm):
        itm = rt.with_meta(itm, rt.merge(meta, rt.meta(itm)))

    return itm



