import pixie.vm.object as object
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.protocols as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint as r_uint32, intmask, widen
import rpython.rlib.jit as jit



class Node(object.Object):
    _type = object.Type(u"PersistentVectorNode")
    def type(self):
        return Node._type

    def __init__(self, edit, array = None):
        self._edit = edit
        self._array = [None] * 32 if array is None else array


EMPTY_NODE = Node(None)


class PersistentVector(object.Object):
    _type = object.Type(u"PersistentVector")

    def type(self):
        return PersistentVector._type

    def __init__(self, meta, cnt, shift, root, tail):
        self._meta = meta
        self._cnt = cnt
        self._shift = shift
        self._root = root
        self._tail = tail

    def tailoff(self):
        if self._cnt < 32:
            return 0
        return ((self._cnt - 1) >> 5) << 5

    def array_for(self, i):
        if 0 <= i < self._cnt:
            if i >= self.tailoff():
                return self._tail

            node = self._root
            level = self._shift
            while level > 0:
                assert isinstance(node, Node)
                node = node._array[(i >> level) & 0x01f]
                level -= 5
            return node._array

        raise IndexError()

    @jit.dont_look_inside
    def nth(self, i, not_found=nil):
        if 0 <= i < self._cnt:
            node = self.array_for(r_uint32(i))
            return node[i & 0x01f]

        return not_found

    @jit.dont_look_inside
    def conj(self, val):
        assert self._cnt < 0xFFFFFFFF
        i = self._cnt

        if self._cnt - self.tailoff() < 32:
            new_tail = self._tail[:]
            new_tail.append(val)
            return PersistentVector(self._meta, self._cnt + 1, self._shift, self._root, new_tail)

        tail_node = Node(self._root._edit, self._tail)
        new_shift = self._shift

        if (self._cnt >> 5) > (r_uint32(1) << self._shift):
            new_root = Node(self._root._edit)
            new_root._array[0] = self._root
            new_root._array[1] = self.new_path(self._root._edit, self._shift, tail_node)

        else:
            new_root = self.push_tail(self._shift, self._root, tail_node)

        return PersistentVector(self._meta, self._cnt + 1, new_shift, new_root, [val])

    def push_tail(self, level, parent, tail_node):
        subidx = ((self._cnt - 1) >> level) & 0x01f
        ret = Node(parent._edit, parent._array[:])
        if (level == 5):
            node_to_insert = tail_node
        else:
            child = parent._array[subidx]
            if child is not None:
                node_to_insert = self.push_tail(level - 5, child, tail_node)
            else:
                node_to_insert = self.new_path(self._root._edit, level - 5, tail_node)

        ret._array[subidx] = node_to_insert
        return ret

    def new_path(self, edit, level, node):
        if level == 0:
            return node
        ret = Node(edit)
        ret._array[0] = self.new_path(edit, level - 5, node)
        return ret



@extend(proto._count, PersistentVector._type)
def _count(self):
    return Integer(intmask(self._cnt))

@extend(proto._nth, PersistentVector._type)
def _nth(self, idx):
    return self.nth(idx.int_val())

@extend(proto._conj, PersistentVector._type)
def _conj(self, v):
    return self.conj(v)

@as_var("vector")
def vector__args(args):
    acc = EMPTY
    for x in range(len(args)):
        x = acc.conj(args[x])
    return acc




EMPTY = PersistentVector(None, r_uint32(0), r_uint32(5), EMPTY_NODE, [])
