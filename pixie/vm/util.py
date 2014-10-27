from rpython.rlib.rarithmetic import r_uint, LONG_BIT, intmask, LONG_MASK
from pixie.vm.object import affirm

seed = 0
C1 = r_uint(0xcc9e2d51)
C2 = r_uint(0x1b873593)



def rotr(value, shift):
    return (value >> shift) | (value << (LONG_BIT - shift))

def rotl(value, shift):
    return (value << shift) | (value >> (LONG_BIT - shift))

def hash_int(input):
    if input == 0:
        return r_uint(0)
    k1 = mix_k1(input)
    h1 = mix_h1(seed, k1)

    return fmix(h1, 4)

def mix_k1(k1):
    k1 *= C1
    k1 = rotl(k1, 15)
    k1 *= C2
    return k1

def mix_h1(h1, k1):
    h1 ^= k1
    h1 = rotl(h1, 13)
    h1 = h1 * 5 + r_uint(0xe6546b64)
    return h1

def hash_unencoded_chars(u):
    #assert isinstance(u, unicode)
    h1 = seed

    # step through the CharSequence 2 chars at a time
    for i in range(1, len(u), 2):
        k1 = r_uint(ord(u[i-1]) | ord(u[i]))
        k1 = mix_k1(k1)
        h1 = mix_h1(h1, k1)

    # deal with any remaining characters
    if (len(u) & 1) == 1:
        k1 = r_uint(ord(u[(len(u) - 1)]))
        k1 = mix_k1(k1)
        h1 ^= k1

    return fmix(h1, 2 * len(u))


def fmix(h1, length):
    h1 ^= length
    h1 ^= h1 >> 16
    h1 *= r_uint(0x85ebca6b)
    h1 ^= h1 >> 13
    h1 *= r_uint(0xc2b2ae35)
    h1 ^= h1 >> 16
    return h1


def mix_coll_hash(hash, count):
    h1 = seed
    k1 = mix_k1(hash)
    h1 = mix_h1(h1, k1)
    return fmix(h1, count)



from pixie.vm.object import Object, Type
import pixie.vm.code as code
from pixie.vm.code import as_var
import pixie.vm.rt as rt
import pixie.vm.numbers as numbers

class HashingState(Object):
    _type = Type(u"pixie.stdlib.HashingState")

    def type(self):
        return HashingState._type

    def __init__(self):
        self._n = r_uint(0)
        self._hash = r_uint(1)

    def update_hash_ordered(self, itm):
        self._n += 1
        self._hash = 31 * self._hash + rt.hash(itm)
        return self

    def update_hash_unordered(self, itm):
        self._n += 1
        self._hash += rt.hash(itm)
        return self

    def finish(self):
        return rt.wrap(intmask(mix_coll_hash(self._hash, self._n)))


@as_var("new-hash-state")
def new_hash_state():
    return HashingState()

@as_var("update-hash-ordered!")
def update_hash_ordered(acc, val):
    affirm(isinstance(acc, HashingState), u"Expected HashingState as first argument")
    return acc.update_hash_ordered(val)

@as_var("update-hash-unordered!")
def update_hash_ordered(acc, val):
    affirm(isinstance(acc, HashingState), u"Expected HashingState as first argument")
    return acc.update_hash_unordered(val)

@as_var("finish-hash-state")
def finish_hash_state(acc):
    affirm(isinstance(acc, HashingState), u"Expected HashingState as first argument")
    return acc.finish()

@as_var("hash-int")
def _hash_int(acc):
    return rt.wrap(intmask(hash_int(acc.r_uint_val())))

