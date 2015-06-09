from pixie.vm2.code import as_var
from pixie.vm2.object import affirm

from pixie.vm2.numbers import SizeT, Integer
from rpython.rlib.rarithmetic import intmask, r_uint

import pixie.vm2.rt as rt

def to_sizet(x):
    if isinstance(x, SizeT):
        return x
    if isinstance(x, Integer):
        return SizeT(r_uint(x.r_uint_val()))

    affirm(False, u"Expected something that can be converted to a SizeT")

@as_var("bit-count32")
def bit_count(i):
    i = to_sizet(i).r_uint_val()
    i = i - ((i >> 1) & r_uint(0x55555555))
    i = (i & r_uint(0x33333333)) + ((i >> 2) & r_uint(0x33333333))
    return SizeT((((i + (i >> 4) & r_uint(0xF0F0F0F)) * r_uint(0x1010101)) & r_uint(0xffffffff)) >> 24)


@as_var("bit-clear")
def bit_clear(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    return rt.wrap(x.r_uint_val() & ~(r_uint(1) << n.r_uint_val()))

@as_var("bit-set")
def bit_set(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    return rt.wrap(x.r_uint_val() | (r_uint(1) << n.r_uint_val()))

@as_var("bit-flip")
def bit_flip(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    return rt.wrap(x.r_uint_val() ^ (r_uint(1) << n.r_uint_val()))

@as_var("bit-not")
def bit_not(x):
    x = to_sizet(x)
    return rt.wrap(~x.r_uint_val())

@as_var("bit-test")
def bit_test(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    return rt.wrap((x.r_uint_val() & (r_uint(1) << n.r_uint_val())) != r_uint(0))

@as_var("bit-and")
def bit_and(x, y):
    x = to_sizet(x)
    y = to_sizet(y)
    return rt.wrap(x.r_uint_val() & y.r_uint_val())

@as_var("bit-and-not")
def bit_and_not(x, y):
    x = to_sizet(x)
    y = to_sizet(y)
    return rt.wrap(x.r_uint_val() & ~y.r_uint_val())

@as_var("bit-or")
def bit_or(x, y):
    x = to_sizet(x)
    y = to_sizet(y)
    return rt.wrap(x.r_uint_val() | y.r_uint_val())

@as_var("bit-xor")
def bit_xor(x, y):
    x = to_sizet(x)
    y = to_sizet(y)
    return rt.wrap(x.r_uint_val() ^ y.r_uint_val())

@as_var("bit-shift-left")
def bit_shift_left(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    return rt.wrap(x.r_uint_val() << n.r_uint_val())

@as_var("bit-shift-right")
def bit_shift_right(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    affirm(isinstance(x, SizeT) and isinstance(n, SizeT), u"x and n must be of type size-t")
    return rt.wrap(x.r_uint_val() >> n.r_uint_val())

@as_var("unsigned-bit-shift-right")
def unsigned_bit_shift_right(x, n):
    x = to_sizet(x)
    n = to_sizet(n)
    return rt.wrap(intmask(x.r_uint_val() >> n.r_uint_val()))

digits = "0123456789abcdefghijklmnopqrstuvwxyz"

@as_var("bit-str")
def bit_str(x, shift):
    x = to_sizet(x)
    x = x.r_uint_val()
    shift = shift.r_uint_val()

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
