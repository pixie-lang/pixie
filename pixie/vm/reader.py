py_object = object
import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
import pixie.vm.numbers as numbers
from pixie.vm.cons import cons
from pixie.vm.symbol import symbol, Symbol
from pixie.vm.keyword import keyword
import pixie.vm.rt as rt
from pixie.vm.persistent_vector import EMPTY as EMPTY_VECTOR
from pixie.vm.libs.readline import _readline

rt.init()

class PlatformReader(object.Object):
    _type = object.Type(u"PlatformReader")

class StringReader(PlatformReader):

    def __init__(self, s):
        assert isinstance(s, unicode)
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
            self._string_reader = StringReader(_readline(">>") + u"\n")

        try:
            return self._string_reader.read()
        except EOFError:
            self._string_reader = None
            return self.read()

    def unread(self, ch):
        assert self._string_reader is not None
        self._string_reader.unread(ch)


def is_whitespace(ch):
    return ch in u"\r\n\t ," or ch == u""

def is_digit(ch):
    return ch in u"0123456789"

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
                acc = nil
                for x in range(len(lst) - 1, -1, -1):
                    acc = cons(lst[x], acc)
                return acc

            rdr.unread(ch)
            lst.append(read(rdr, True))

class UnmachedListReader(ReaderHandler):
    def invoke(self, rdr, ch):
        raise SyntaxError()

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
        raise SyntaxError()

class QuoteReader(ReaderHandler):
    def invoke(self, rdr, ch):
        itm = read(rdr, True)
        return cons(symbol(u"quote"), cons(itm))

class KeywordReader(ReaderHandler):
    def invoke(self, rdr, ch):
        itm = read(rdr, True)
        assert isinstance(itm, Symbol)

        return keyword(itm._str)

handlers = {u"(": ListReader(),
            u")": UnmachedListReader(),
            u"[": VectorReader(),
            u"]": UnmachedVectorReader(),
            u"'": QuoteReader(),
            u":": KeywordReader()}

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

    return numbers.Integer(int(u"".join(acc)))

def read_symbol(rdr, ch):
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

def read(rdr, error_on_eof):
    try:
        eat_whitespace(rdr)
    except EOFError as ex:
        if error_on_eof:
            raise ex
        return eof



    ch = rdr.read()

    macro = handlers.get(ch, None)
    if macro is not None:
        return macro.invoke(rdr, ch)

    if is_digit(ch) or ch == u"-":
        return read_number(rdr, ch)

    return read_symbol(rdr, ch)



