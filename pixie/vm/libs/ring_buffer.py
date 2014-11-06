from rpython.rlib.rarithmetic import r_uint

class RingBuffer(object):
    def __init__(self, size):
        assert isinstance(size, r_uint)
        self._array = [None] * size
        self._array_len = size
        self._length = size
        self._head = 0
        self._tail = 0

    def pending(self):
        return self._array_len - self._length

    def pop(self):
        if not self._length == 0:
            x = self._array[self._tail]
            self._array[self._tail] = None
            self._tail = (self._tail + 1) % self._array_len
            self._length -= 1
            return x
        return None

    def push(self, x):
        self._array[self._head] = x
        self._head = (self._head + 1) % self._array_len
        self._length += 1

    def unbounded_push(self, x):
        if self._length - 1 == 0:
            self.resize()
        self.push(x)

    def resize(self):
        new_arr_size = self._array_len * 2
        new_arr = [None] * new_arr_size

        if self._tail < self._head:
            array_copy(self._array, self._tail, new_arr, 0, self._length)
            self._tail = 0
            self._head = self._length
            self._array = new_arr
            self._array_len = new_arr_size

        elif self._tail > self._head:
            array_copy(self._array, self._tail, new_arr, 0, self._array_len - self._tail)
            array_copy(self._array, 0, new_arr, self._array_len - self._tail, self._head)
            self._tail = 0
            self._head = self._length
            self._array = new_arr
            self._array_len = new_arr_size

        else:
            self._tail = 0
            self._head = 0
            self._array = new_arr
            self._array_len = new_arr_size


def array_copy(src, src_pos, dest, dest_pos, count):
    x = r_uint(0)
    while x < count:
        dest[dest_pos + x] = src[src_pos + x]
        x += 1
