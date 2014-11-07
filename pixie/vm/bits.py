from pixie.vm.code import as_var
from pixie.vm.object import affirm

from pixie.vm.numbers import Integer

import pixie.vm.rt as rt

@as_var("bit-clear")
def bit_clear(x, n):
    affirm(isinstance(x, Integer) and isinstance(n, Integer), u"x and n must be Integers")
    return rt.wrap(x.int_val() & ~(1 << n.int_val()))

@as_var("bit-set")
def bit_set(x, n):
    affirm(isinstance(x, Integer) and isinstance(n, Integer), u"x and n must be Integers")
    return rt.wrap(x.int_val() | (1 << n.int_val()))

@as_var("bit-flip")
def bit_flip(x, n):
    affirm(isinstance(x, Integer) and isinstance(n, Integer), u"x and n must be Integers")
    return rt.wrap(x.int_val() ^ (1 << n.int_val()))

@as_var("bit-not")
def bit_not(x):
    affirm(isinstance(x, Integer), u"x must be an Integer")
    return rt.wrap(~x.int_val())

@as_var("bit-test")
def bit_test(x, n):
    affirm(isinstance(x, Integer) and isinstance(n, Integer), u"x and n must be Integers")
    return rt.wrap((x.int_val() & (1 << n.int_val())) != 0)

@as_var("bit-and")
def bit_and(x, y):
    affirm(isinstance(x, Integer) and isinstance(y, Integer), u"x and y must be Integers")
    return rt.wrap(x.int_val() & y.int_val())

@as_var("bit-and-not")
def bit_and_not(x, y):
    affirm(isinstance(x, Integer) and isinstance(y, Integer), u"x and y must be Integers")
    return rt.wrap(x.int_val() & ~y.int_val())

@as_var("bit-or")
def bit_or(x, y):
    affirm(isinstance(x, Integer) and isinstance(y, Integer), u"x and y must be Integers")
    return rt.wrap(x.int_val() | y.int_val())

@as_var("bit-xor")
def bit_xor(x, y):
    affirm(isinstance(x, Integer) and isinstance(y, Integer), u"x and y must be Integers")
    return rt.wrap(x.int_val() ^ y.int_val())

@as_var("bit-shift-left")
def bit_shift_left(x, n):
    affirm(isinstance(x, Integer) and isinstance(n, Integer), u"x and n must be Integers")
    return rt.wrap(x.int_val() << n.int_val())

@as_var("bit-shift-right")
def bit_shift_right(x, n):
    affirm(isinstance(x, Integer) and isinstance(n, Integer), u"x and n must be Integers")
    return rt.wrap(x.int_val() >> n.int_val())

# unsigned-bit-shift-right (sets sign bit to zero)

digits = "0123456789abcdefghijklmnopqrstuvwxyz"

@as_var("bit-str")
def bit_str(x, shift):
    affirm(isinstance(x, Integer) and isinstance(shift, Integer), u"x and shift must be Integers")
    x = x.int_val()
    shift = shift.int_val()

    buf = ['_'] * 32
    char_pos = 32
    radix = 1 << shift
    mask = radix - 1
    while True:
        char_pos -= 1
        buf[char_pos] = digits[x & mask]
        x = x >> shift
        if x == 0:
            break

    res = ""
    for i in range(char_pos, char_pos + 32 - char_pos):
        res += buf[i]
    return rt.wrap(res)
