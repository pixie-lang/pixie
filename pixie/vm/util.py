from rpython.rlib.rarithmetic import r_uint, LONG_BIT

seed = 0
C1 = 0xcc9e2d51
C2 = 0x1b873593

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
    h1 = h1 * 5 + 0xe6546b64
    return h1

def hash_unencoded_chars(u):
    assert isinstance(u, unicode)
    h1 = seed

    # step through the CharSequence 2 chars at a time
    for i in range(1, len(u), 2):
        k1 = ord(u[i-1]) | ord(u[i])
        k1 = mix_k1(k1)
        h1 = mix_h1(h1, k1)

    # deal with any remaining characters
    if (len(u) & 1) == 1:
        k1 = ord(u[(len(u) - 1)])
        k1 = mix_k1(k1)
        h1 ^= k1

    return fmix(h1, 2 * len(u))


def fmix(h1, length):
    h1 ^= length
    h1 ^= h1 >> 16
    h1 *= 0x85ebca6b
    h1 ^= h1 >> 13
    h1 *= 0xc2b2ae35
    h1 ^= h1 >> 16
    return h1


