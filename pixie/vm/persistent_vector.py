from pixie.vm.effects.effects import Object, Type, handle_with, InvokeThunk
from pixie.vm.effects.effect_transform import cps
from pixie.vm.effects.generators import yield_Ef, generator_handler
from pixie.vm.code import as_global, extend, mark_satisfies, wrap_fn
from pixie.vm.object import affirm
from pixie.vm.primitives import nil, true, false
from pixie.vm.numbers import Integer
import pixie.vm.stdlib as proto
from rpython.rlib.rarithmetic import r_uint, intmask, widen
from pixie.vm.keyword import keyword
import rpython.rlib.jit as jit
import pixie.vm.rt as rt



class Node(Object):
    _type = Type(u"pixie.stdlib.PersistentVectorNode")
    _immutable_fields_ = ["_edit", "_array[*]"]
    def type(self):
        return Node._type

    def __init__(self, edit, array=None):
        self._edit = edit
        self._array = [None] * 32 if array is None else array

    def array(self):
        return self._array


EMPTY_NODE = Node(None)

@mark_satisfies("pixie.stdlib.IVector")
class PersistentVector(Object):
    _type = Type(u"pixie.stdlib.PersistentVector")
    _immutable_fields_ = ["_tail[*]", "_cnt", "_meta", "_shift", "_root"]

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

    def count(self):
        return self._cnt

    @jit.unroll_safe
    def array_for(self, i):
        if 0 <= i < self._cnt:
            if i >= self.tailoff():
                return self._tail

            node = self._root
            level = self._shift
            while level > 0:
                assert isinstance(node, Node)
                node = node.array()[(i >> level) & 0x01f]
                level -= 5
            return node.array()

        affirm(False, u"Index out of Range")

    def nth(self, i, not_found=nil):
        if 0 <= i < self._cnt:
            node = self.array_for(r_uint(i))
            return node[i & 0x01f]

        return not_found

    def conj(self, val):
        assert self._cnt < r_uint(0xFFFFFFFF)
        i = self._cnt

        if self._cnt - self.tailoff() < 32:
            new_tail = clone_append(self._tail, val)
            return PersistentVector(self._meta, self._cnt + 1, self._shift, self._root, new_tail)

        tail_node = Node(self._root._edit, self._tail)
        new_shift = self._shift

        if (self._cnt >> 5) > (r_uint(1) << self._shift):
            new_root = Node(self._root._edit)
            new_root.array()[0] = self._root
            new_root.array()[1] = new_path(self._root._edit, self._shift, tail_node)
            new_shift += 5

        else:
            new_root = self.push_tail(self._shift, self._root, tail_node)

        return PersistentVector(self._meta, self._cnt + 1, new_shift, new_root, [val])

    def push_tail(self, level, parent, tail_node):
        subidx = ((self._cnt - 1) >> level) & 0x01f
        ret = Node(parent._edit, copy_array(parent.array()))
        if (level == 5):
            node_to_insert = tail_node
        else:
            child = parent.array()[subidx]
            if child is not None:
                node_to_insert = self.push_tail(level - 5, child, tail_node)
            else:
                node_to_insert = new_path(self._root._edit, level - 5, tail_node)

        ret.array()[subidx] = node_to_insert
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

        if self._shift > 5 and new_root.array()[1] is None:
            new_root = new_root.array()[0]
            new_shift -= 5

        return PersistentVector(self._meta, self._cnt - 1, new_shift, new_root, new_tail)

    def pop_tail(self, level, node):
        sub_idx = ((self._cnt - 1) >> level) & 0x01f
        if level > 5:
            new_child = self.pop_tail(level - 5, node.array()[sub_idx])
            if new_child is None or sub_idx == 0:
                return None
            else:
                ret = Node(self._root._edit, copy_array(node.array()))
                ret.array()[sub_idx] = new_child
                return ret

        elif sub_idx == 0:
            return None

        else:
            ret = Node(self._root._edit, copy_array(node.array()))
            ret.array()[sub_idx] = None
            return ret

    def to_list(self):
        lst = [None] * self._cnt

        x = 0
        while x < len(lst):
            lst[x] = self.nth(x)
            x += 1

        return lst

    def to_str(self):

        acc = []
        for x in range(self._cnt):
            itm = self.nth(x)
            acc.append(unichr(itm.char_val()))

        return rt.wrap(u"".join(acc))

    def to_persistent_list(self):
        from pixie.vm.persistent_list import EmptyList, PersistentList
        if self._cnt == 0:
            return EmptyList()

        i = r_uint(self._cnt)
        acc = nil
        while i > 0:
            acc = PersistentList(self.nth(i - 1), acc, self._cnt - i + 1, nil)
            i -= 1
        return acc

def new_path(edit, level, node):
    if level == 0:
        return node
    ret = Node(edit)
    ret.array()[0] = new_path(edit, level - 5, node)
    return ret

def copy_array(arr):
    new_arr = [None] * len(arr)

    idx = 0
    while idx < len(arr):
        new_arr[idx] = arr[idx]
        idx += 1

    return new_arr

def clone_append(arr, val):
    new_arr = [None] * (len(arr) + 1)

    idx = 0
    while idx < len(arr):
        new_arr[idx] = arr[idx]
        idx += 1

    new_arr[len(arr)] = val

    return new_arr

#
# edited = u"edited"
#
# class TransientVector(object.Object):
#     _type = object.Type(u"pixie.stdlib.TransientVector")
#
#     def type(self):
#         return TransientVector._type
#
#     def __init__(self, cnt, shift, root, tail):
#         self._cnt = cnt
#         self._shift = shift
#         self._root = root
#         self._tail = tail
#
#     @staticmethod
#     def editable_root(node):
#         return Node(edited, node._array[:])
#
#     def ensure_editable(self):
#         affirm(self._root._edit is not None, u"Transient used after call to persist!")
#
#     def ensure_node_editable(self, node):
#         if node._edit is self._root._edit:
#             return node
#
#         return Node(self._root._edit, node._array[:])
#
#
#     def tailoff(self):
#         if self._cnt < 32:
#             return 0
#         return ((self._cnt - 1) >> 5) << 5
#
#     def persistent(self):
#         self.ensure_editable()
#
#         self._root._edit = None
#         trimmed = [None] * (self._cnt - self.tailoff())
#         list_copy(self._tail, 0, trimmed, 0, len(trimmed))
#         return PersistentVector(nil, self._cnt, self._shift, self._root, trimmed)
#
#     @staticmethod
#     def editable_tail(tl):
#         ret = [None] * 32
#         list_copy(tl, 0, ret, 0, len(tl))
#         return ret
#
#     def conj(self, val):
#         self.ensure_editable()
#         i = self._cnt
#
#         if i - self.tailoff() < 32:
#             self._tail[i & 0x01f] = val
#             self._cnt += 1
#             return self
#
#         tail_node = Node(self._root._edit, self._tail)
#         self._tail = [None] * 32
#         self._tail[0] = val
#         new_shift = self._shift
#
#         if (self._cnt >> 5) > (r_uint(1) << self._shift):
#             new_root = Node(self._root._edit)
#             new_root._array[0] = self._root
#             new_root._array[1] = new_path(self._root._edit, self._shift, tail_node)
#             new_shift += 5
#
#         else:
#             new_root = self.push_tail(self._shift, self._root, tail_node)
#
#         self._root = new_root
#         self._shift = new_shift
#         self._cnt += 1
#         return self
#
#     def push_tail(self, level, parent, tail_node):
#         parent = self.ensure_node_editable(parent)
#
#         sub_idx = ((self._cnt - 1) >> level) & 0x01f
#
#         ret = parent
#         if level == 5:
#             node_to_insert = tail_node
#         else:
#             child = parent._array[sub_idx]
#             if child is not None:
#                 node_to_insert = self.push_tail(level - 5, child, tail_node)
#             else:
#                 node_to_insert = new_path(self._root._edit, level-5, tail_node)
#
#         ret._array[sub_idx] = node_to_insert
#         return ret
#
#     def array_for(self, i):
#         if 0 <= i < self._cnt:
#             if i >= self.tailoff():
#                 return self._tail
#
#             node = self._root
#             level = self._shift
#             while level > 0:
#                 assert isinstance(node, Node)
#                 node = node._array[(i >> level) & 0x01f]
#                 level -= 5
#             return node._array
#
#         affirm(False, u"Index out of Range")
#
#     def editable_array_for(self, i):
#         if i >= 0 and i < self._cnt:
#             if i >= self.tailoff():
#                 return self._tail
#             node = self._root
#             level = self._shift
#             while level > 0:
#                 node = self.ensure_node_editable(node._array[(i >> self._level) & 0x1f])
#
#                 level -= 5
#             return node._array
#
#         affirm(False, u"Index out of bounds")
#
#     def nth(self, i, not_found=nil):
#         self.ensure_editable()
#         if 0 <= i < self._cnt:
#             node = self.array_for(r_uint(i))
#             return node[i & 0x01f]
#
#         return not_found
#
#     def pop(self):
#         self.ensure_editable()
#         affirm(self._cnt != 0, u"Can't pop and empty vector")
#
#         if self._cnt == 0:
#             self._cnt = 0
#             return self
#
#         i = self._cnt - 1
#
#         if i & 0x01f > 0:
#             self._cnt -= 1
#             return self
#
#         new_tail = self.editable_array_for(self._cnt - 2)
#
#         new_root = self.pop_tail(self._shift, self._root)
#         new_shift = self._shift
#
#         if new_root is None:
#             new_root = Node(self._root._edit)
#
#         if self._shift > 5 and new_root._array[1] is None:
#             new_root = self.ensure_node_editable(new_root._array[0])
#             new_shift -= 5
#
#         self._root = new_root
#         self._shift = new_shift
#         self._cnt -= 1
#         self._tail = new_tail
#
#         return self
#
#     def pop_tail(self, level, node):
#         node = self.ensure_node_editable(node)
#         sub_idx = ((self._cnt - 2) >> level) & 0x01f
#
#         if level > 5:
#             new_child = self.pop_tail(level - 5, node._array[sub_idx])
#             if new_child is None and sub_idx == 0:
#                 return None
#             else:
#                 ret = node
#                 ret._array[sub_idx] = new_child
#                 return ret
#
#         elif sub_idx == 0:
#             return None
#         else:
#             ret = node
#             ret._array[sub_idx] = None
#             return ret
#




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



@extend("pixie.stdlib.-count", PersistentVector)
def _count(self):
    return rt.wrap(intmask(self.count()))

@extend("pixie.stdlib.-nth", PersistentVector)
def _nth(self, idx):
    return self.nth(r_uint(idx.int_val()))

@extend("pixie.stdlib.-val-at", PersistentVector)
def _val_at(self, key, not_found):
    if isinstance(key, Integer):
        return self.nth(r_uint(key.int_val()))
    else:
        return not_found

KW_ISEQABLE = keyword("pixie.stdlib.ISeqable")
KW_IVECTOR = keyword("pixie.stdlib.IVector")

@extend("pixie.stdlib.-eq", PersistentVector)
def _eq(self, obj):
    if isinstance(self, PersistentVector):
        if self.count() != obj.count():
            return false
        i = 0
        while i < self.count():
            if not rt.eq_Ef(self.nth(i), obj.nth(i)):
                return false
            i += 1
        return true
    elif rt.satisfies_QMARK__Ef(KW_IVECTOR):
        if self.count() != rt.count_Ef(obj).r_uint_val():
            return false
        i = 0
        while i < self.count():
            if not rt.eq_Ef(self.nth(i), rt.nth_Ef(self, rt.wrap(i))):
                return false
            i += 1
        return true
    else:
        if not rt.satisfies_QMARK__Ef(KW_ISEQABLE, obj):
            return false
        seq = rt.seq_Ef(obj)
        i = 0
        while i < self.count():
            if seq is nil or not rt.eq_Ef(self.nth(i), rt.first_Ef(seq)):
                return false
            seq = rt.next_Ef(seq)
            i += 1
        if seq is not nil:
            return false
        return true

@wrap_fn()
def iterator_inner(self):
    i = 0
    while i < self._cnt:
        array = self.array_for(i)
        j = 0
        while j < len(array):
            item = array[j]
            yield_Ef(item)
            j += 1

        step = len(array)
        i += step
    return nil

@extend("pixie.stdlib.-iterator", PersistentVector, transform=False)
def _iterator(self):
    return handle_with(generator_handler,
                       InvokeThunk(iterator_inner, self))

#
# @extend(proto._contains_key, PersistentVector)
# def _contains_key(self, key):
#     if not isinstance(key, Integer):
#         return false
#     else:
#         return true if key.int_val() >= 0 and key.int_val() < intmask(self._cnt) else false
#
# @extend(proto._conj, PersistentVector)
# def _conj(self, v):
#     assert isinstance(self, PersistentVector)
#     return self.conj(v)
#
# @extend(proto._push, PersistentVector)
# def _push(self, v):
#     assert isinstance(self, PersistentVector)
#     return self.conj(v)
#
# @extend(proto._pop, PersistentVector)
# def _push(self):
#     assert isinstance(self, PersistentVector)
#     return self.pop()
#
# @extend(proto._meta, PersistentVector)
# def _meta(self):
#     assert isinstance(self, PersistentVector)
#     return self.meta()
#
# @extend(proto._with_meta, PersistentVector)
# def _with_meta(self, meta):
#     assert isinstance(self, PersistentVector)
#     return self.with_meta(meta)
#
#
# _reduce_driver = jit.JitDriver(name="pixie.stdlib.PersistentVector_reduce",
#                               greens=["f"],
#                               reds="auto")
#
# @extend(proto._reduce, PersistentVector)
# def _reduce(self, f, init):
#     assert isinstance(self, PersistentVector)
#     i = 0
#     while i < self._cnt:
#         array = self.array_for(i)
#         for j in range(len(array)):
#             item = array[j]
#             _reduce_driver.jit_merge_point(f=f)
#
#             init = f.invoke([init, array[j]])
#             if rt.reduced_QMARK_(init):
#                 return rt.deref(init)
#
#         step = len(array)
#         i += step
#     return init
#
#
# @as_var("vector")
# def vector__args(args):
#     acc = rt._transient(EMPTY)
#     for x in range(len(args)):
#         acc = rt._conj_BANG_(acc, args[x])
#     return rt._persistent_BANG_(acc)
#
# @extend(proto._transient, PersistentVector)
# def _transient(self):
#     assert isinstance(self, PersistentVector)
#     return TransientVector(self._cnt, self._shift, TransientVector.editable_root(self._root), TransientVector.editable_tail(self._tail))
#
# @extend(proto._persistent_BANG_, TransientVector)
# def _persistent(self):
#     assert isinstance(self, TransientVector)
#     return self.persistent()
#
# @extend(proto._conj_BANG_, TransientVector)
# def _conj(self, val):
#     assert isinstance(self, TransientVector)
#     return self.conj(val)
#
# proto.IVector.add_satisfies(PersistentVector._type)

EMPTY = PersistentVector(nil, r_uint(0), r_uint(5), EMPTY_NODE, [])
