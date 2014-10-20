py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.protocols as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint, intmask
import rpython.rlib.jit as jit
import pixie.vm.rt as rt

MASK_32 = 0xFFFFFFFF

class Box(py_object):
    def __init__(self):
        self._val = None

class PersistentHashMap(object.Object):
    _type = object.Type(u"pixie.stdlib.PersistentHashMap")

    def type(self):
        return PersistentHashMap._type

    def __init__(self, cnt, root, meta=nil):
        self._cnt = cnt
        self._root = root
        self._meta = meta

    def assoc(self, key, val):
        added_leaf = Box()

        new_root = (BitmapIndexedNode_EMPTY if self._root is None else self._root) \
                   .assoc_inode(r_uint(0), rt.hash(key), key, val, added_leaf)

        if new_root is self._root:
            return self

        return PersistentHashMap(self._cnt if added_leaf._val is None else self._cnt + 1, new_root, self._meta)

    def val_at(self, key, not_found):
        return not_found if self._root is None else self._root.find(r_uint(0), rt.hash(key), key, not_found)





class INode(object.Object):
    _type = object.Type(u"pixie.stdlib.INode")

    def type(self):
        return INode._type

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        pass

    def find(self, shift, hash_val, key, not_found):
        pass

    def reduce_inode(self, f, init):
        pass

def mask(hash, shift):
    return (hash >> shift) & 0x01f

def bitpos(hash, shift):
    return (1 << mask(hash, shift)) & MASK_32



class BitmapIndexedNode(INode):

    def __init__(self, edit,  bitmap, array):
        self._edit = edit
        self._bitmap = bitmap
        self._array = array

    def index(self, bit):
        return bit_count(self._bitmap & (bit - 1))

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        bit = bitpos(hash_val, shift)
        idx = self.index(bit)

        if (self._bitmap & bit) != 0:
            key_or_null = self._array[2 * idx]
            val_or_node = self._array[2 * idx + 1]

            if key_or_null is None:
                assert isinstance(val_or_node, INode)
                n = val_or_node.assoc_inode(shift + 5, hash_val, key, val, added_leaf)
                if n is val_or_node:
                    return self
                return BitmapIndexedNode(None, self._bitmap, clone_and_set(self._array, 2 * idx + 1, n))


            if key_or_null is None or rt.eq(key, key_or_null):
                if val is val_or_node:
                    return self
                return BitmapIndexedNode(None, self._bitmap, clone_and_set(self._array, 2 * idx + 1, val))

            added_leaf._val = added_leaf
            return BitmapIndexedNode(None, self._bitmap,
                clone_and_set2(self._array,
                               2 * idx, None,
                               2 * idx + 1, create_node(shift+ 5, key_or_null, val_or_node, hash_val, key, val)))
        else:
            n = bit_count(self._bitmap)
            if n >= 16:
                nodes = [None] * 32
                jdx = mask(hash_val, shift)
                nodes[jdx] = BitmapIndexedNode_EMPTY.assoc_inode(shift + 5, hash_val, key, val, added_leaf)
                j = 0

                for i in range(32):
                    if (self._bitmap >> i) & 1 != 0:
                        if self._array[j] is None:
                            nodes[i] = self._array[j + 1]
                        else:
                            nodes[i] = BitmapIndexedNode_EMPTY.assoc_inode(shift + 5, rt.hash(self._array[j]),
                                                               self._array[j], self._array[j + 1], added_leaf)
                        j += 1

                return ArrayNode(None, n + 1, nodes)
            else:
                new_array = [None] * (2 * (n + 1))
                list_copy(self._array, 0, new_array, 0, 2 * idx)
                new_array[2 * idx] = key
                added_leaf._val = added_leaf
                new_array[2 * idx + 1] = val
                list_copy(self._array, 2 * idx, new_array, 2 * (idx + 1), 2 * (n - idx))
                return BitmapIndexedNode(None, self._bitmap | bit, new_array)

    def find(self, shift, hash_val, key, not_found):
        bit = bitpos(hash_val, shift)
        if (self._bitmap & bit) == 0:
            return not_found
        idx = self.index(bit)
        key_or_null = self._array[2 * idx]
        val_or_node = self._array[2 * idx + 1]
        if key_or_null is None:
            return val_or_node.find(shift + 5, hash_val, key, not_found)
        if rt.eq(key, key_or_null):
            return val_or_node
        return not_found

    def reduce_inode(self, f, init):
        for x in range(0, len(self._array), 2):
            key_or_none = self._array[x]
            val_or_node = self._array[x + 1]
            if key_or_none is None and val_or_node is not None:
                init = init.reduce_inode(f, init)
            else:
                init = f.invoke([init, rt.map_entry(key_or_none, val_or_node)])
            if rt.reduced_QMARK_(init):
                return init
        return init


BitmapIndexedNode_EMPTY = BitmapIndexedNode(None, r_uint(0), [])


class ArrayNode(INode):
    def __init__(self, edit, cnt, array):
        self._cnt = cnt
        self._edit = edit
        self._array = array

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        idx = mask(hash_val, shift)
        node = self._array[idx]
        if node is None:
            return ArrayNode(None, self._cnt + 1, clone_and_set(self._array, idx,
                            BitmapIndexedNode_EMPTY.assoc_inode(shift + 5, hash_val, key, val, added_leaf)))

        n = node.assoc_inode(shift + 5, hash_val, key, val, added_leaf)
        if n is node:
            return self
        return ArrayNode(None, self._cnt, clone_and_set(self._array, idx, n))

    def find(self, shift, hash_val, key, not_found):
        idx = mask(hash_val, shift)
        node = self._array[idx]
        if node is None:
            return not_found
        return node.find(shift + 5, hash_val, key, not_found)

    def reduce_inode(self, f, init):
        for x in range(len(self._array)):
            node = self._array[x]
            if node is not None:
                init = node.reduce_inode(f, init)
                if rt.reduced_QMARK_(init):
                    return init

        return init

class HashCollisionNode(INode):
    def __init__(self, edit, hash, array):
        self._hash = hash
        self._edit = edit
        self._array = array

    def assoc_inode(self, shift, hash_val, key, val, added_leaf):
        assert False

    def find(self, shift, hash_val, key, not_found):
        for x in range(0, len(self._array), 2):
            key_or_nil = self._array[x]
            if key_or_nil is not None and rt.eq(key_or_nil, key):
                return self._array[x + 1]

        return not_found

    def reduce_inode(self, f, init):
        for x in range(0, len(self._array), 2):
            key_or_nil = self._array[x]
            if key_or_nil is None:
                continue

            val = self._array[x + 1]
            init = f.invoke([init, val])
            if rt.reduced_QMARK_(init):
                return init
        return init



def create_node(shift, key1, val1, key2hash, key2, val2):
    key1hash = rt.hash(key1)
    if key1hash == key2hash:
        return HashCollisionNode(None, key1hash, [key1, val1, key2, val2])
    added_leaf = Box()
    return BitmapIndexedNode_EMPTY.assoc_inode(shift, key1hash, key1, val1, added_leaf) \
                                  .assoc_inode(shift, key1hash, key1, val1, added_leaf)

def bit_count(i):
    assert isinstance(i, r_uint)
    i = i - ((i >> 1) & 0x55555555)
    i = (i & 0x33333333) + ((i >> 2) & 0x33333333)
    return (((i + (i >> 4) & 0xF0F0F0F) * 0x1010101) & 0xffffffff) >> 24

@jit.unroll_safe
def list_copy(from_lst, from_loc, to_list, to_loc, count):
    from_loc = r_uint(from_loc)
    to_loc = r_uint(to_loc)
    count = r_uint(count)

    i = r_uint(0)
    while i < count:
        to_list[to_loc + i] = from_lst[from_loc+i]
        i += 1
    return to_list

@jit.unroll_safe
def clone_and_set(array, i, a):
    clone = [None] * len(array)

    idx = r_uint(0)
    while idx < len(array):
        clone[idx] = array[idx]

    clone[i] = a
    return clone

@jit.unroll_safe
def clone_and_set2(array, i, a, j, b):
    clone = [None] * len(array)

    idx = r_uint(0)
    while idx < len(array):
        clone[idx] = array[idx]

    clone[i] = a
    clone[j] = b
    return clone


### hook into RT

EMPTY = PersistentHashMap(r_uint(0), None)

@as_var("hashmap")
def hashmap__args(args):
    affirm(len(args) & 0x1 == 0, u"hashmap requires even number of args")

    idx = 0
    acc = EMPTY

    while idx < len(args):
        key = args[idx]
        val = args[idx + 1]

        acc = acc.assoc(key, val)

        idx += 2

    return acc



@extend(proto._val_at, PersistentHashMap)
def _val_at(self, key, not_found):
    assert isinstance(self, PersistentHashMap)
    return self.val_at(key, not_found)

@extend(proto._reduce, PersistentHashMap)
def _reduce(self, f, init):
    assert isinstance(self, PersistentHashMap)
    if self._root is None:
        return init
    val = self._root.reduce_inode(f, init)
    if rt.reduced_QMARK_(val):
        return rt.deref(val)

    return val

@extend(proto._assoc, PersistentHashMap)
def _assoc(self, key, val):
    assert isinstance(self, PersistentHashMap)
    return self.assoc(key, val)

proto.IMap.add_satisfies(PersistentHashMap._type)

@extend(proto._count, PersistentHashMap)
def _count(self):
    assert isinstance(self, PersistentHashMap)
    return rt.wrap(intmask(self._cnt))