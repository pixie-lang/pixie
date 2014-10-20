# Pixie

## Intro

Pixie is a lightweight lisp suitable for both general use as well as shell scripting. The language is still in a "pre-alpha" phase and as such changes fairly quickly.
The standard library is heavily inspired by Clojure as well as several other functional programming languages. It is written in RPython (http://pypy.readthedocs.org/en/latest/coding-guide.html) and as such supports a fairly fast GC and an amazingly fast tracing JIT.

## Features

Some planned and implemented features:

* Protocols first implementation
* Transducers at-the-bottom (most primitves are based off of reduce)
* Coroutines for transducer inversion of control (transducer to lazy-seq conversion)
* A "good enough" JIT (implemented, tuning still a WIP, but not bad performance today)
* Easy FFI (TODO)
* Pattern matching (TODO)

## Contributing

Currently there isn't a whole lot that newcomers can help out with, since the entire codebase is in quite a bit of flux, and the main primitives are still under development. However, we do want to have a very open contribution process. If you have a feature you'd like to implement, submit a PR or file an issue and we'll see what we can do.

## Implementation Notes

Although parts of the language may be very close to Clojure (they are both lisps after all), language parity is not a design goal. We will take the features from Clojure or other languages that are suitable to our needs, and feel free to reject those that aren't. Therefore this should not be considered a "Clojure Dialect", but instead a "Clojure inspired lisp".

## Copying

Free use of this software is granted under the terms of the GNU Lesser General Public License (LGPL). For details see the files `COPYING` and `COPYING.LESSER` included with the 0MQ distribution.
