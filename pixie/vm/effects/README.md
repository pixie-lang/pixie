## Effects System for Pixie Prototype

### Motivation

While the current Pixie interpreter works well it's pretty much just like any other mutable interpreter. But on the other
hand we have the PyPy JIT generator that allows us to create interpreters modeled almost any way we want. What would a
interpreter look like in a "perfect world"?

For answers to such questions I suggest reading up on the language Eff (http://arxiv.org/pdf/1203.1539v1.pdf). This language
specifies an interesting language design, one that makes a distinction between side-effect-free computations, and effects that
modify the environment or the system. Having an interpreter that makes this distinction has several benefits:

1) Any computation in the system could be hinted to the JIT as being pure, thus removable if the arguments to the computation
are constants.

2) Support for Generators, Exceptions, and Lightweight threads (among other things) could be added via this approach.

3) With the ability to "pause" a thread and with all blocking IO segregated inside effects, the vm could easily integrate
async IO libraries such as libuv, removing the need for a GIL.

4) If foreign functions are considered effects (as they should be) then FFI functions could be called in separate threads,
allowing for parallel execution of C functions.

5) The upcoming STM solution in PyPy works best for computations that do not perform IO. Once again, this effects system
separates code, allowing for better optimizations.

6) If the interpreter is immutable, then really weird things can be done at runtime, including: forking a interpreter, resuming
exceptions, re-running a step in the interpreter, even saving the interpreter's state to disk may be possible.

7) Tail Call Optimization is a side-effect of all of this.

8) Deep generators. It's possible to call `yield` with this approach deep inside collection code. In addition `yield` can be used
as inversion of control for Transducers.

### Approach

In this approach (inspired by eclj https://github.com/brandonbloom/eclj/blob/master/src/eclj/interpret/cps.clj) we (ab)use
thunks to support effects and TCO. An example implementation can be seen in this repository.


### Roadmap

As of today, this POC is finished. It works, and the JIT produces very promising results (on par with the current JIT).
Thus it is now just a matter of refactoring the guts of Pixie to match the new coding styles. Thankfully not much in the
 `.lisp` files of pixie have to change.

 * Collections - Anything that calls into pixie or RT will need to be refactored with `@cps`
 * Reader - Will need to be completely refactored. Calling `rdr.read()` can now be an effect, that change will ripple through
 the rest of the system.
 * Compiler - Completely re-written, the new interpreter is an AST interpreter. This will however drastically simplify the compiler
   as it will no longer have to track stacks, save constants, etc.
 * Interpreter - The AST nodes will replace the interpreter
 * RT - Completely rewritten, but since it uses vars, it should be simple to perform this


### Does this mean we should halt work on Pixie?

No! Development of pixie can still continue, the changes will be merged in as possible to the new development branch.

### CPS Transform

This project contains a very 'touchy' code transformer, known as `@cps`. This will take an RPython function or method and
transform it into an immutable state-machine via CPS transformation. As is expected with this sort of code mangling there
are many caveats to using this transformer, but they are mostly simple to remember:

* Calls to functions or methods that end with `_Ef` are considered to be effect functions (functions that will either
 return Answer, Effect or a Thunk). Thus at every call to such a function the transformer will create a continuation.
* Generators/Iterators should be avoided. A single step of the function may be run many times, thus it is important to clone
  any mutable state.
* The call stack is not persisted across continuations, so be sure that the stack position is 0 at every effect function call.
For example:


    @cps
    def foo(x):
      r = invoke_Ef(x)
      z = invoke_Ef(r)
      return z


Is fine, while the following is not:


    @cps
    def foo(x):
      return invoke_Ef(invoke_Ef(x))


Since the outer `invoke_` will be loaded before the `inner_`.

* Calls to effect functions that immediately return will be turned into tail calls, so prefer this style when possible:

    @cps
    def foo(x):
      return invoke_Ef(x)

* Currently (until this restriction is removed) effect calls that take anything but locals as arguments are not supported.


    @cps
    def foo(x):
      # works
      x = invoke_Ef(something)
      # doesn't work
      x = invoke_Ef(something._zing)

* `break` and `continue` require the stack to operate, and as such are not supported
* Since functions are RPython and internally function locals are converted class fields, locals can only have one type. Unlike
RPython that supports locals with conflicting types as long as they are redefined between usages.