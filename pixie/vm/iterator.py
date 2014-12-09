from pixie.vm.object import Object, Type, runtime_error
from pixie.vm.code import extend, as_var
from pixie.vm.primitives import true, false, nil
import pixie.vm.stdlib as proto
import pixie.vm.rt as rt


class EmptyIterator(Object):
    _type = Type(u"pixie.vm.Iterator")

    def type(self):
        return EmptyIterator._type


    def __init__(self):
        pass

    def move_next(self):
        runtime_error(u"Empty Iterator")

    def at_end(self):
        return True


empty_iterator = EmptyIterator()

@extend(proto._at_end_QMARK_, EmptyIterator)
def _at_end(_):
    return true


class NativeIterator(Object):
    _type = Type(u"pixie.vm.NativeIterator")

    def type(self):
        return NativeIterator._type

    def __init__(self):
        pass

@extend(proto._at_end_QMARK_, NativeIterator)
def _at_end(self):
    return rt.wrap(self.at_end())


@extend(proto._move_next_BANG_, NativeIterator)
def _move_next(self):
    return self.move_next()


@extend(proto._current, NativeIterator)
def _current(self):
    return self.current()


class MapIterator(NativeIterator):
    def __init__(self, fn, iter):
        self._w_fn = fn
        self._w_iter = iter
        if not iter.at_end():
            self._w_current = self._w_fn.invoke([self._w_iter.current()])

    def move_next(self):
        self._w_iter.move_next()

        if not self._w_iter.at_end():
            self._w_current = self._w_fn.invoke([self._w_iter.current()])
        else:
            self._w_current = nil

    def current(self):
        return self._w_current

    def at_end(self):
        return self._w_iter.at_end()

