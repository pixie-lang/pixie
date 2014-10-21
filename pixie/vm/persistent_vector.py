py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.stdlib as proto
from  pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint, intmask, widen
import rpython.rlib.jit as jit
import pixie.vm.rt as rt



class Node(object.Object):
    _type = object.Type(u"pixie.stdlib.PersistentVectorNode")
    def type(self):
        return Node._type

    def __init__(self, edit, array = None):
        self._edit = edit
        self._array = [None] * 32 if array is None else array


EMPTY_NODE = Node(None)


class PersistentVector(object.Object):
    _type = object.Type(u"pixie.stdlib.PersistentVector")

    def type(self):
        return PersistentVector._type

    def __init__(self, meta, cnt, shift, root, tail):
        self._meta = meta
        self._cnt = cnt
        self._shift = shift
        self._root = root
        self._tail = tail

    def meta(self):
        return self._meta

    def with_meta(self, meta):
        return PersistentVector(meta, self._cnt, self._shift, self._root, self._tail)

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

        affirm(False, u"Index out of Range")

    def nth(self, i, not_found=nil):
        if 0 <= i < self._cnt:
            node = self.array_for(r_uint(i))
            return node[i & 0x01f]

        return not_found

    def conj(self, val):
        assert self._cnt < 0xFFFFFFFF
        i = self._cnt

        if self._cnt - self.tailoff() < 32:
            new_tail = self._tail[:]
            new_tail.append(val)
            return PersistentVector(self._meta, self._cnt + 1, self._shift, self._root, new_tail)

        tail_node = Node(self._root._edit, self._tail)
        new_shift = self._shift

        if (self._cnt >> 5) > (r_uint(1) << self._shift):
            new_root = Node(self._root._edit)
            new_root._array[0] = self._root
            new_root._array[1] = new_path(self._root._edit, self._shift, tail_node)
            new_shift += 5

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
                node_to_insert = new_path(self._root._edit, level - 5, tail_node)

        ret._array[subidx] = node_to_insert
        return ret



    def pop(self):
        affirm(self._cnt != 0, u"Can't pop an empty vector")

        if self._cnt == 1:
            return EMPTY

        if self._cnt - self.tailoff() > 1:
            size = len(self._tail) - 1
            assert size >= 0 # for translation
            new_tail = self._tail[:size]
            return PersistentVector(self._meta, self._cnt - 1, self._shift, self._root, new_tail)

        new_tail = self.array_for(self._cnt - 2)

        new_root = self.pop_tail(self._shift, self._root)
        new_shift = self._shift
        if new_root is None:
            new_root = EMPTY_NODE

        if self._shift > 5 and new_root._array[1] is None:
            new_root = new_root._array[0]
            new_shift -= 5

        return PersistentVector(self._meta, self._cnt - 1, new_shift, new_root, new_tail)

    def pop_tail(self, level, node):
        sub_idx = ((self._cnt - 1) >> level) & 0x01f
        if level > 5:
            new_child = self.pop_tail(level - 5, node._array[sub_idx])
            if new_child is None or sub_idx == 0:
                return None
            else:
                ret = Node(self._root._edit, node._array[:])
                ret._array[sub_idx] = new_child
                return ret

        elif sub_idx == 0:
            return None

        else:
            ret = Node(self._root._edit, node._array[:])
            ret._array[sub_idx] = None
            return ret

def new_path(self, edit, level, node):
    if level == 0:
        return node
    ret = Node(edit)
    ret._array[0] = self.new_path(edit, level - 5, node)
    return ret

class Edited(py_object):
    pass

edited = Edited

class TransientVector(object.Object):
    _type = object.Type("pixie.stdlib.TransientVector")

    def __init__(self, cnt, shift, root, tail):
        self._cnt = cnt
        self._shift = shift
        self._root = root
        self._tail = tail


    def editable_root(self, node):
        return Node(edited, node._array[:])

    def ensure_editable(self):
        affirm(self._root._edit is not None, u"Transient used after call to persist!")

    def ensure_node_editable(self, node):
        if node._edit is self._root._edit:
            return node

        return Node(self._root._edit, node._array[:])

    def tailoff(self):
        if self._cnt < 32:
            return 0
        return ((self._cnt - 1) >> 5) << 5

    def persistent(self):
        self.ensure_editable()

        self._root._edit = None
        trimmed = [None] * (self._cnt - self.tailoff())
        list_copy(self._tail, 0, trimmed, 0, len(trimmed))
        return PersistentVector(nil, self._cnt, self._shift, self._root, trimmed)

    def editable_tail(self, tl):
        ret = [None] * 32
        list_copy(tl, 0, rt, 0, len(tl))
        return ret

    def conj(self, val):
        self.ensure_editable()
        i = self._cnt

        if i - self.tailoff() < 32:
            self._tail[i & 0x01f] = val
            self._cnt += 1
            return self

        tail_node = Node(self._root._edit, self._tail)
        self._tail = [None] * 32
        self._tail[0] = val
        new_shift = self._shift

        if (self._cnt >> 5) > (r_uint(1) << self._shift):
            new_root = Node(self._root._edit)
            new_root._array[0] = self._root
            new_root._array[1] = new_path(self._root._edit, self._shift, tail_node)
            new_shift += 1

        else:
            new_root = self.push_tail(self._shift, self._root, tail_node)

        self._root = new_root
        self._shift = new_shift
        self._cnt += 1
        return self

    def push_tail(self, level, parent, tail_node):
        parent = self.ensure_node_editable(parent)

        sub_idx = ((self._cnt - 1) >> level) & 0x01f

        ret = parent
        if level == 5:
            node_to_insert = tail_node
        else:
            child = parent._array[sub_idx]
            if child is not None:
                node_to_insert = self.push_tail(level - 5, child, tail_node)
            else:
                node_to_insert = new_path(level-5, child, tail_node)

        ret._array[sub_idx] = node_to_insert
        return ret



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



@extend(proto._count, PersistentVector)
def _count(self):
    assert isinstance(self, PersistentVector)
    return rt.wrap(intmask(self._cnt))

@extend(proto._nth, PersistentVector)
def _nth(self, idx):
    assert isinstance(self, PersistentVector)
    return self.nth(idx.int_val())

@extend(proto._conj, PersistentVector)
def _conj(self, v):
    assert isinstance(self, PersistentVector)
    return self.conj(v)

@extend(proto._push, PersistentVector)
def _push(self, v):
    assert isinstance(self, PersistentVector)
    return self.conj(v)

@extend(proto._pop, PersistentVector)
def _push(self):
    assert isinstance(self, PersistentVector)
    return self.pop()

@extend(proto._meta, PersistentVector)
def _meta(self):
    assert isinstance(self, PersistentVector)
    return self.meta()

@extend(proto._with_meta, PersistentVector)
def _with_meta(self, meta):
    assert isinstance(self, PersistentVector)
    return self.with_meta(meta)


_reduce_driver = jit.JitDriver(name="pixie.stdlib.PersistentVector_reduce",
                              greens=["f"],
                              reds="auto")

@extend(proto._reduce, PersistentVector)
def _reduce(self, f, init):
    assert isinstance(self, PersistentVector)
    i = 0
    while i < self._cnt:
        array = self.array_for(i)
        for j in range(len(array)):
            item = array[j]
            _reduce_driver.jit_merge_point(f=f)

            init = f.invoke([init, array[j]])
            if rt.reduced_QMARK_(init):
                return rt.deref(init)

        step = len(array)
        i += step
    return init


@as_var("vector")
def vector__args(args):
    acc = EMPTY
    for x in range(len(args)):
        acc = acc.conj(args[x])
    return acc


proto.IVector.add_satisfies(PersistentVector._type)

EMPTY = PersistentVector(nil, r_uint(0), r_uint(5), EMPTY_NODE, [])
