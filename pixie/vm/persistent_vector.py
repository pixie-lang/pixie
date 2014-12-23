py_object = object
import pixie.vm.object as object
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.stdlib as proto
from pixie.vm.code import extend, as_var
from rpython.rlib.rarithmetic import r_uint, intmask
import rpython.rlib.jit as jit
import pixie.vm.rt as rt


class Node(object.Object):
    _type = object.Type(u"pixie.stdlib.PersistentVectorNode")

    def type(self):
        return Node._type

    def __init__(self, edit, array=None):
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
            assert isinstance(node, Node)
            return node._array

        affirm(False, u"Index out of Range")

    def nth(self, i, not_found=nil):
        if 0 <= i < self._cnt:
            node = self.array_for(r_uint(i))
            return node[i & 0x01f]

        return not_found

    def conj(self, val):
        assert self._cnt < r_uint(0xFFFFFFFF)

        if self._cnt - self.tailoff() < 32:
            new_tail = self._tail[:]
            new_tail.append(val)
            return PersistentVector(self._meta, self._cnt + 1, self._shift, self._root, new_tail)

        root = self._root
        assert isinstance(root, Node)
        tail_node = Node(root._edit, self._tail)
        new_shift = self._shift

        if (self._cnt >> 5) > (r_uint(1) << self._shift):
            root = self._root
            assert isinstance(root, Node)
            new_root = Node(root._edit)
            new_root._array[0] = self._root
            root = self._root
            assert isinstance(root, Node)
            new_root._array[1] = new_path(root._edit, self._shift, tail_node)
            new_shift += 5

        else:
            new_root = self.push_tail(self._shift, self._root, tail_node)

        return PersistentVector(self._meta, self._cnt + 1, new_shift, new_root, [val])

    def push_tail(self, level, parent, tail_node):
        subidx = ((self._cnt - 1) >> level) & 0x01f
        assert isinstance(parent, Node)
        ret = Node(parent._edit, parent._array[:])

        root = self._root
        assert isinstance(root, Node)

        if (level == 5):
            node_to_insert = tail_node
        else:
            child = parent._array[subidx]
            if child is not None:
                node_to_insert = self.push_tail(level - 5, child, tail_node)
            else:
                node_to_insert = new_path(root._edit, level - 5, tail_node)

        ret._array[subidx] = node_to_insert
        return ret

    def pop(self):
        affirm(self._cnt != 0, u"Can't pop an empty vector")

        if self._cnt == 1:
            return EMPTY

        if self._cnt - self.tailoff() > 1:
            size = len(self._tail) - 1
            assert size >= 0  # for translation
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
            assert isinstance(node, Node)
            new_child = self.pop_tail(level - 5, node._array[sub_idx])
            if new_child is None or sub_idx == 0:
                return None
            else:
                root = self._root
                assert isinstance(root, Node)
                ret = Node(root._edit, node._array[:])
                ret._array[sub_idx] = new_child
                return ret

        elif sub_idx == 0:
            return None

        else:
            root = self._root
            assert isinstance(root, Node)
            assert isinstance(node, Node)
            ret = Node(root._edit, node._array[:])
            ret._array[sub_idx] = None
            return ret

    def assoc_at(self, idx, val):
        if idx >= 0 and idx < self._cnt:
            if idx >= self.tailoff():
                new_tail = self._tail[:]
                new_tail[idx & 0x01f] = val
                return PersistentVector(self._meta, self._cnt, self._shift, self._root, new_tail)
            return PersistentVector(self._meta, self._cnt, self._shift, do_assoc(self._shift, self._root, idx, val), self._tail)
        if idx == self._cnt:
            return self.conj(val)
        else:
            object.runtime_error(u"index out of range")


def do_assoc(lvl, node, idx, val):
    assert isinstance(node, Node)
    ret = Node(node._edit, node._array[:])
    if lvl == 0:
        ret._array[idx & 0x01f] = val
    else:
        subidx = (idx >> lvl) & 0x01f
        ret._array[subidx] = do_assoc(lvl - 5, node._array[subidx], idx, val)
    return ret


def new_path(edit, level, node):
    if level == 0:
        return node
    ret = Node(edit)
    ret._array[0] = new_path(edit, level - 5, node)
    return ret


edited = u"edited"


class TransientVector(object.Object):
    _type = object.Type(u"pixie.stdlib.TransientVector")

    def type(self):
        return TransientVector._type

    def __init__(self, cnt, shift, root, tail):
        self._cnt = cnt
        self._shift = shift
        self._root = root
        self._tail = tail

    @staticmethod
    def editable_root(node):
        assert isinstance(node, Node)
        return Node(edited, node._array[:])

    def ensure_editable(self):
        root = self._root
        assert isinstance(root, Node)
        affirm(root._edit is not None, u"Transient used after call to persist!")

    def ensure_node_editable(self, node):
        assert isinstance(node, Node)
        root = self._root
        assert isinstance(root, Node)
        if node._edit is root._edit:
            return node

        root = self._root
        assert isinstance(root, Node)
        return Node(root._edit, node._array[:])

    def tailoff(self):
        if self._cnt < 32:
            return 0
        return ((self._cnt - 1) >> 5) << 5

    def persistent(self):
        self.ensure_editable()

        root = self._root
        assert isinstance(root, Node)

        root._edit = None
        trimmed = [None] * (self._cnt - self.tailoff())
        list_copy(self._tail, 0, trimmed, 0, len(trimmed))
        return PersistentVector(nil, self._cnt, self._shift, self._root, trimmed)

    @staticmethod
    def editable_tail(tl):
        ret = [None] * 32
        list_copy(tl, 0, ret, 0, len(tl))
        return ret

    def conj(self, val):
        self.ensure_editable()
        i = self._cnt

        if i - self.tailoff() < 32:
            self._tail[i & 0x01f] = val
            self._cnt += 1
            return self

        root = self._root
        assert isinstance(root, Node)

        tail_node = Node(root._edit, self._tail)
        self._tail = [None] * 32
        self._tail[0] = val
        new_shift = self._shift

        if (self._cnt >> 5) > (r_uint(1) << self._shift):
            new_root = Node(root._edit)
            new_root._array[0] = self._root
            new_root._array[1] = new_path(root._edit, self._shift, tail_node)
            new_shift += 5

        else:
            new_root = self.push_tail(self._shift, self._root, tail_node)

        self._root = new_root
        self._shift = new_shift
        self._cnt += 1
        return self

    def push_tail(self, level, parent, tail_node):
        parent = self.ensure_node_editable(parent)

        root = self._root
        assert isinstance(root, Node)

        sub_idx = ((self._cnt - 1) >> level) & 0x01f

        ret = parent
        if level == 5:
            node_to_insert = tail_node
        else:
            child = parent._array[sub_idx]
            if child is not None:
                node_to_insert = self.push_tail(level - 5, child, tail_node)
            else:
                node_to_insert = new_path(root._edit, level - 5, tail_node)

        ret._array[sub_idx] = node_to_insert
        return ret

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

    def editable_array_for(self, i):
        if i >= 0 and i < self._cnt:
            if i >= self.tailoff():
                return self._tail
            node = self._root
            level = self._shift
            while level > 0:
                node = self.ensure_node_editable(node._array[(i >> level) & 0x1f])

                level -= 5
            return node._array

        affirm(False, u"Index out of bounds")

    def nth(self, i, not_found=nil):
        self.ensure_editable()
        if 0 <= i < self._cnt:
            node = self.array_for(r_uint(i))
            return node[i & 0x01f]

        return not_found

    def pop(self):
        self.ensure_editable()
        affirm(self._cnt != 0, u"Can't pop and empty vector")

        if self._cnt == 0:
            self._cnt = 0
            return self

        i = self._cnt - 1

        if i & 0x01f > 0:
            self._cnt -= 1
            return self

        new_tail = self.editable_array_for(self._cnt - 1)

        new_root = self.pop_tail(self._shift, self._root)
        new_shift = self._shift

        root = self._root
        assert isinstance(root, Node)

        if new_root is None:
            new_root = Node(root._edit)

        if self._shift > 5 and new_root._array[1] is None:
            new_root = self.ensure_node_editable(new_root._array[0])
            new_shift -= 5

        self._root = new_root
        self._shift = new_shift
        self._cnt -= 1
        self._tail = new_tail

        return self

    def pop_tail(self, level, node):
        node = self.ensure_node_editable(node)
        sub_idx = ((self._cnt - 2) >> level) & 0x01f

        if level > 5:
            new_child = self.pop_tail(level - 5, node._array[sub_idx])
            if new_child is None and sub_idx == 0:
                return None
            else:
                ret = node
                ret._array[sub_idx] = new_child
                return ret

        elif sub_idx == 0:
            return None
        else:
            ret = node
            ret._array[sub_idx] = None
            return ret


@jit.unroll_safe
def list_copy(from_lst, from_loc, to_list, to_loc, count):
    from_loc = r_uint(from_loc)
    to_loc = r_uint(to_loc)
    count = r_uint(count)

    i = r_uint(0)
    while i < count:
        to_list[to_loc + i] = from_lst[from_loc + i]
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


@extend(proto._val_at, PersistentVector)
def _val_at(self, key, not_found):
    assert isinstance(self, PersistentVector)
    if isinstance(key, Integer):
        return self.nth(key.int_val())
    else:
        return not_found


@extend(proto._eq, PersistentVector)
def _eq(self, obj):
    assert isinstance(self, PersistentVector)
    if self is obj:
        return true
    elif isinstance(obj, PersistentVector):
        if self._cnt != obj._cnt:
            return false
        for i in range(0, intmask(self._cnt)):
            if not rt.eq(self.nth(i), obj.nth(i)):
                return false
        return true
    else:
        if obj is nil or not rt.satisfies_QMARK_(proto.ISeqable, obj):
            return false
        seq = rt.seq(obj)
        for i in range(0, intmask(self._cnt)):
            if seq is nil or not rt.eq(self.nth(i), rt.first(seq)):
                return false
            seq = rt.next(seq)
        if seq is not nil:
            return false
        return true


@extend(proto._contains_key, PersistentVector)
def _contains_key(self, key):
    assert isinstance(self, PersistentVector)
    if not isinstance(key, Integer):
        return false
    else:
        return true if key.int_val() >= 0 and key.int_val() < intmask(self._cnt) else false


@extend(proto._conj, PersistentVector)
def _conj(self, v):
    assert isinstance(self, PersistentVector)
    return self.conj(v)


@extend(proto._push, PersistentVector)
def _push(self, v):
    assert isinstance(self, PersistentVector)
    return self.conj(v)


@extend(proto._pop, PersistentVector)
def _pop(self):
    assert isinstance(self, PersistentVector)
    return self.pop()


@extend(proto._assoc, PersistentVector)
def _assoc(self, idx, val):
    assert isinstance(self, PersistentVector)
    affirm(isinstance(idx, Integer), u"key must be an integer")
    return self.assoc_at(r_uint(idx.int_val()), val)


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
            _reduce_driver.jit_merge_point(f=f)

            init = f.invoke([init, array[j]])
            if rt.reduced_QMARK_(init):
                return rt.deref(init)

        step = len(array)
        i += step
    return init


@as_var("vector")
def vector__args(args):
    acc = rt._transient(EMPTY)
    for x in range(len(args)):
        acc = rt._conj_BANG_(acc, args[x])
    return rt._persistent_BANG_(acc)


@extend(proto._transient, PersistentVector)
def _transient(self):
    assert isinstance(self, PersistentVector)
    return TransientVector(self._cnt, self._shift, TransientVector.editable_root(self._root), TransientVector.editable_tail(self._tail))


@extend(proto._persistent_BANG_, TransientVector)
def _persistent(self):
    assert isinstance(self, TransientVector)
    return self.persistent()


@extend(proto._conj_BANG_, TransientVector)
def _conj(self, val):
    assert isinstance(self, TransientVector)
    return self.conj(val)


@extend(proto._pop_BANG_, TransientVector)
def _pop(self):
    assert isinstance(self, TransientVector)
    return self.pop()


@extend(proto._push_BANG_, TransientVector)
def _push(self, val):
    assert isinstance(self, TransientVector)
    return self.conj(val)


@extend(proto._count, TransientVector)
def _count(self):
    assert isinstance(self, TransientVector)
    return rt.wrap(intmask(self._cnt))

proto.IVector.add_satisfies(PersistentVector._type)

EMPTY = PersistentVector(nil, r_uint(0), r_uint(5), EMPTY_NODE, [])
