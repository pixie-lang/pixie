import loki_vm.vm.object as object
from loki_vm.vm.primitives import nil, true, false
import loki_vm.vm.numbers as numbers
from loki_vm.vm.cons import cons
from loki_vm.vm.symbol import symbol



class PlatformReader(object.Object):
    _type = object.Type("PlatformReader")


class StringReader(PlatformReader):

    def __init__(self, str):
        self._str = str
        self._idx = 0

    def read(self):
        if self._idx >= len(self._str):
            return ""
        ch = self._str[self._idx]
        self._idx += 1
        return ch

    def unread(self, ch):
        self._idx -= 1



def is_whitespace(ch):
    return ch in "\r\n\t ," or ch == ""

def is_digit(ch):
    return ch in "0123456789"

def eat_whitespace(rdr):
    while True:
        ch = rdr.read()
        if is_whitespace(ch):
            continue
        rdr.unread(ch)
        return


class ReaderHandler(object.Object):
    def invoke(self, rdr, ch):
        pass

class ListReader(ReaderHandler):
    def invoke(self, rdr, ch):
        lst = []
        while True:
            eat_whitespace(rdr)
            ch = rdr.read()
            if ch == ")":
                acc = nil
                for x in range(len(lst) - 1, -1, -1):
                    acc = cons(lst[x], acc)
                return acc

            rdr.unread(ch)
            lst.append(read(rdr, True))

class UnmachedListReader(ReaderHandler):
    def invoke(self, rdr, ch):
        raise SyntaxError();

handlers = {"(": ListReader(),
            ")": UnmachedListReader()}

def read_number(rdr, ch):
    acc = [ch]
    while True:
        ch = rdr.read()
        if is_whitespace(ch) or ch in handlers:
            rdr.unread(ch)
            break
        acc.append(ch)
    return numbers.Integer(int("".join(acc)))

def read_symbol(rdr, ch):
    acc = [ch]
    while True:
        ch = rdr.read()
        if is_whitespace(ch) or ch in handlers:
            rdr.unread(ch)
            break
        acc.append(ch)
    sym_str = "".join(acc)
    if sym_str == "true":
        return true
    if sym_str == "false":
        return false
    if sym_str == "nil":
        return nil
    return symbol(sym_str)

def read(rdr, error_on_eof):
    eat_whitespace(rdr)

    ch = rdr.read()

    macro = handlers.get(ch, nil)
    if macro is not nil:
        return macro.invoke(rdr, ch)

    if is_digit(ch) or ch == "-":
        return read_number(rdr, ch)

    return read_symbol(rdr, ch)



