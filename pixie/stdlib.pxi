(in-ns :pixie.stdlib)

(def libc (ffi-library pixie.platform/lib-c-name))


(def exit (ffi-fn libc "exit" [CInt] CInt))
(def puts (ffi-fn libc "puts" [CCharP] CInt))


(def sh (ffi-fn libc "system" [CCharP] CInt))
(def printf (ffi-fn libc "printf" [CCharP] CInt :variadic? true))
(def getenv (ffi-fn libc "getenv" [CCharP] CCharP))

(def libedit (ffi-library (str "libedit." pixie.platform/so-ext)))
(def readline (ffi-fn libedit "readline" [CCharP] CCharP))
(def rand (ffi-fn libc "rand" [] CInt))
(def srand (ffi-fn libc "srand" [CInt] CInt))
(def fopen (ffi-fn libc "fopen" [CCharP CCharP] CVoidP))
(def fread (ffi-fn libc "fread" [CVoidP CInt CInt CVoidP] CInt))
(def mkdtemp (ffi-fn libc "mkdtemp" [CCharP] CCharP))
(def mkdir (ffi-fn libc "mkdir" [CCharP] CCharP))
(def rmdir (ffi-fn libc "rmdir" [CCharP] CCharP))
(def rm (ffi-fn libc "remove" [CCharP] CCharP))

(def libm (ffi-library (str "libm." pixie.platform/so-ext)))
(def atan2 (ffi-fn libm "atan2" [CDouble CDouble] CDouble))
(def lround (ffi-fn libm "lround" [CDouble] CInt))


(def reset! -reset!)

(def program-arguments [])

(def fn (fn* [& args]
             (cons 'fn* args)))
(set-macro! fn)

(def let (fn* [& args]
              (cons 'let* args)))
(set-macro! let)

(def loop (fn* [& args]
               (cons 'loop* args)))
(set-macro! loop)

(def identity
  (fn ^{:doc "The identity function. Returns its argument."
        :added "0.1"}
    identity
    [x]
    x))

(def conj
  (fn ^{:doc "Adds elements to the collection. Elements are added to the end except in the case of Cons lists."
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    conj
    ([] [])
    ([coll] coll)
    ([coll item] (-conj coll item))
    ([coll item & args]
       (reduce -conj (-conj coll item) args))))

(def conj!
  (fn ^{:doc "Adds elements to the transient collection. Elements are added to the end except in the case of Cons lists."
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    conj!
    ([] (-transient []))
    ([coll] (-persistent! coll))
    ([coll item] (-conj! coll item))
    ([coll item & args]
       (reduce -conj! (-conj! coll item) args))))

(def disj (fn ^{:doc "Removes elements from the collection."
                :signatures [[] [coll] [coll item]]
                :added "0.1"}
            disj
            ([] [])
            ([coll] coll)
            ([coll item] (-disj coll item))
            ([coll item & items]
               (reduce -disj (-disj coll item) items))))

(comment (def disj! (fn ^{:doc "Removes elements from the transient collection."
                          :signatures [[] [coll] [coll item] [coll item & items]]
                          :added "0.1"}
                      disj!
                      ([] (-transient []))
                      ([result] (-persistent! result))
                      ([result item] (-disj! result item))
                      ([coll item & items]
                         (reduce -disj! (-disj! coll item) items)))))

(def pop
  (fn ^{:doc "Pops elements off a stack."
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    pop
    ([coll] (-pop coll))))

(def push
  (fn ^{:doc "Pushes an element on to a stack."
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    push
    ([coll x] (-push coll x))))

(def pop!
  (fn ^{:doc "Pops elements off a transient stack."
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    pop!
    ([coll] (-pop! coll))))

(def push!
  (fn ^{:doc "Pushes an element on to a transient stack."
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    push!
    ([coll x] (-push! coll x))))

(def transient (fn [coll] (-transient coll)))

(def persistent! (fn [coll] (-persistent! coll)))

(def transduce (fn transduce
                 ([f coll]
                    (let [result (-reduce coll f (f))]
                      (f result)))

                 ([xform rf coll]
                    (let [f (xform rf)
                          result (-reduce coll f (f))]
                      (f result)))
                 ([xform rf init coll]
                    (let [f (xform rf)
                          result (-reduce coll f init)]
                      (f result)))))

(def map (fn ^{:doc "Creates a transducer that applies f to every input element."
               :signatures [[f] [f coll]]
               :added "0.1"}
           map
           ([f]
             (fn [xf]
                (fn
                  ([] (xf))
                  ([result] (xf result))
                  ([result item] (xf result (f item))))))
           ([f coll]
            (lazy-seq*
              (fn []
                (let [s (seq coll)]
                  (if s
                    (cons (f (first s))
                          (map f (rest s)))
                    nil)))))
           ([f & colls]
              (let [step (fn step [cs]
                           (lazy-seq*
                             (fn []
                               (let [ss (map seq cs)]
                                 (if (every? identity ss)
                                   (cons (map first ss) (step (map rest ss)))
                                   nil)))))]
                (map (fn [args] (apply f args)) (step colls))))))

(def reduce (fn
             ([rf col]
              (reduce rf (rf) col))
             ([rf init col]
              (-reduce col rf init))))

(def instance? (fn ^{:doc "Checks if x is an instance of t.

                           When t is seqable, checks if x is an instance of
                           any of the types contained therein."
                     :signatures [[t x]]}
                 instance? [t x]
                 (if (-satisfies? ISeqable t)
                   (let [ts (seq t)]
                     (if (not ts) false
                       (if (-instance? (first ts) x)
                         true
                         (instance? (rest ts) x))))
                   (-instance? t x))))

(def satisfies? (fn ^{:doc "Checks if x satisfies the protocol p.

                            When p is seqable, checks if x satisfies all of
                            the protocols contained therein."
                      :signatures [[t x]]}
                  satisfies? [p x]
                  (if (-satisfies? ISeqable p)
                    (let [ps (seq p)]
                      (if (not ps) true
                        (if (not (-satisfies? (first ps) x))
                          false
                          (satisfies? (rest ps) x))))
                    (-satisfies? p x))))

(def into (fn ^{:doc "Add the elements of `from` to the collection `to`."
                :signatures [[to from] [to xform from]]
                :added "0.1"}
            ([to from]
             (if (satisfies? IToTransient to)
               (persistent! (reduce conj! (transient to) from))
               (reduce conj to from)))
            ([to xform from]
             (if (satisfies? IToTransient to)
               (transduce xform conj! (transient to) from)
               (transduce xform conj to from)))))

(def interpose
  (fn ^{:doc "Returns a transducer that inserts `val` in between elements of a collection."
        :signatures [[val] [val coll]]
        :added "0.1"}
    interpose
    ([val] (fn [xf]
             (let [first? (atom true)]
               (fn
                 ([] (xf))
                 ([result] (xf result))
                 ([result item] (if @first?
                                  (do (reset! first? false)
                                      (xf result item))
                                  (xf (xf result val) item)))))))
    ([val coll]
       (transduce (interpose val) conj coll))))

(def preserving-reduced
  (fn preserving-reduced [rf]
    (fn pr-inner [a b]
      (let [ret (rf a b)]
        (if (reduced? ret)
          (reduced ret)
          ret)))))

(def cat
  (fn ^{:doc "A transducer that concatenates elements of a collection."
        :added "0.1"}
    cat
    [rf]
    (let [rrf (preserving-reduced rf)]
      (fn cat-inner
        ([] (rf))
        ([result] (rf result))
        ([result input]
           (reduce rrf result input))))))

(def mapcat
  (fn ^{:doc "Maps f over the elements of coll and concatenates the result."
        :added "0.1"}
    mapcat
    ([f]
       (comp (map f) cat))
    ([f coll]
       (transduce (mapcat f) conj coll))))

(def seq-reduce (fn seq-reduce
                  [coll f init]
                  (loop [init init
                         coll (seq coll)]
                    (if (reduced? init)
                      @init
                      (if (seq coll)
                        (recur (f init (first coll))
                               (seq (next coll)))
                        init)))))

(def indexed-reduce
  (fn indexed-reduce
    [coll f init]
    (let [max (count coll)]
      (loop [init init
             i 0]
        (if (reduced? init)
          @init
          (if (-eq i max)
            init
            (recur (f init (nth coll i nil)) (+ i 1))))))))

(def rest (fn ^{:doc "Returns the elements after the first element, or () if there are no more elements."
                :signatures [[coll]]
                :added "0.1"}
            [coll]
            (let [next (next coll)]
              (if next next '()))))

;; Make all Function types extend IFn
(extend -invoke Code -invoke)
(extend -invoke NativeFn -invoke)
(extend -invoke VariadicCode -invoke)
(extend -invoke MultiArityFn -invoke)
(extend -invoke Closure -invoke)
(extend -invoke Var -invoke)
(extend -invoke PolymorphicFn -invoke)
(extend -invoke DoublePolymorphicFn -invoke)

(extend -reduce Cons seq-reduce)
(extend -reduce PersistentList seq-reduce)
(extend -reduce LazySeq seq-reduce)


(comment (extend -reduce Array indexed-reduce))

(extend -reduce Buffer indexed-reduce)
(extend -reduce String indexed-reduce)

(extend -str Bool
  (fn [x]
    (if (identical? x true)
      "true"
      "false")))
(extend -repr Bool -str)

(extend -str Nil (fn [x] "nil"))
(extend -repr Nil -str)
(extend -reduce Nil (fn [self f init] init))
(extend -hash Nil (fn [self] 100000))
(extend -with-meta Nil (fn [self _] nil))
(extend -deref Nil (fn [_] nil))
(extend -contains-key Nil (fn [_ _] false))

(extend -hash Integer hash-int)

(extend -eq Integer -num-eq)
(extend -eq Float -num-eq)
(extend -eq Ratio -num-eq)

(def ordered-hash-reducing-fn
  (fn ordered-hash-reducing-fn
    ([] (new-hash-state))
    ([state] (finish-hash-state state))
    ([state itm] (update-hash-ordered! state itm))))

(def unordered-hash-reducing-fn
  (fn unordered-hash-reducing-fn
    ([] (new-hash-state))
    ([state] (finish-hash-state state))
    ([state itm] (update-hash-unordered! state itm))))

(def string-builder
  (fn ^{:doc "Creates a reducing function that builds a string based on calling str on the transduced collection."}
    ([] (-string-builder))
    ([sb] (str sb))
    ([sb item] (conj! sb item))))

(extend -str PersistentVector
  (fn [v]
    (str "[" (transduce (interpose " ") string-builder v) "]")))
(extend -repr PersistentVector
  (fn [v]
    (str "[" (transduce (comp (map -repr) (interpose " ")) string-builder v) "]")))

(extend -str Cons
  (fn [v]
    (str "(" (transduce (interpose " ") string-builder v) ")")))
(extend -repr Cons
  (fn [v]
    (str "(" (transduce (comp (map -repr) (interpose " ")) string-builder v) ")")))

(extend -hash Cons
        (fn [v]
          (transduce ordered-hash-reducing-fn v)))

(extend -str PersistentList
  (fn [v]
    (str "(" (transduce (interpose " ") string-builder v) ")")))
(extend -repr PersistentList
  (fn [v]
    (str "(" (transduce (comp (map -repr) (interpose " ")) string-builder v) ")")))

(extend -hash PersistentList
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))


(extend -str LazySeq
  (fn [v]
    (str "(" (transduce (interpose " ") string-builder v) ")")))
(extend -repr LazySeq
  (fn [v]
    (str "(" (transduce (comp (map -repr) (interpose " ")) string-builder v) ")")))

(extend -hash PersistentVector
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))

(extend -hash PersistentHashSet
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))



(add-marshall-handlers PersistentHashSet
  (fn [obj] (vec obj))
  (fn [obj] (apply hash-set obj)))

(extend -hash PersistentHashMap
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))



(extend -hash EmptyList (fn [v] 5555555))

(extend -hash Bool
  (fn [v]
    (if v
      1111111
      3333333)))

(def = -eq)

(extend -seq PersistentVector
  (fn vector-seq
   ([self]
    (vector-seq self 0))
   ([self x]
    (if (= x (count self))
      nil
      (cons (nth self x) (lazy-seq* (fn [] (vector-seq self (+ x 1)))))))))

(extend -seq String
  (fn string-seq
   ([self]
    (string-seq self 0))
   ([self x]
    (if (= x (count self))
      nil
      (cons (nth self x) (lazy-seq* (fn [] (string-seq self (+ x 1)))))))))

(def concat
  (fn ^{:doc "Concatenates its arguments."
        :signatures [[& args]]
        :added "0.1"}
    concat
    [& args] (transduce cat conj args)))

(def key (fn [x] (-key x)))
(def val (fn [x] (-val x)))

(def defn (fn ^{:doc "Defines a new function."
                :signatures [[nm doc? meta? & body]]}
            defn
            [nm & rest]
            (let [meta (if (meta nm) (meta nm) {})
                  meta (if (instance? String (first rest))
                         (assoc meta :doc (first rest))
                         meta)
                  rest (if (instance? String (first rest)) (next rest) rest)
                  meta (if (satisfies? IMap (first rest))
                         (merge meta (first rest))
                         meta)
                  rest (if (satisfies? IMap (first rest)) (next rest) rest)
                  meta (if (-contains-key meta :signatures)
                         meta
                         (merge meta {:signatures
                                      (if (satisfies? IVector (first rest))
                                        [(first rest)]
                                        (transduce (map first) conj rest))}))
                  nm (with-meta nm meta)]
              `(def ~nm (fn ~nm ~@rest)))))
(set-macro! defn)

(defn defmacro
  {:doc "Defines a new macro."
   :added "0.1"}
  [nm & rest]
  `(do (defn ~nm ~@rest)
       (set-macro! ~nm)
       ~nm))
(set-macro! defmacro)

(defmacro defn-
  {:doc "Define a new non-public function. Otherwise the same as defn."
   :signatures [[nm doc? meta? & body]]
   :added "0.1"}
  [nm & rest]
  (let [nm (with-meta nm (assoc (meta nm) :private true))]
    (cons `defn (cons nm rest))))

(defn not
  {:doc "Inverts the input, if a truthy value is supplied, returns false, otherwise
returns true."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (if x false true))

(defn +
  {:doc "Adds the arguments, returning 0 if no arguments."
   :signatures [[& args]]
   :added "0.1"}
  ([] 0)
  ([x] x)
  ([x y] (-add x y))
  ([x y & args]
      (reduce -add (-add x y) args)))

(defn -
  ([] 0)
  ([x] (-sub 0 x))
  ([x y] (-sub x y))
  ([x y & args]
      (reduce -sub (-sub x y) args)))

(defn *
  ([] 1)
  ([x] x)
  ([x y] (-mul x y))
  ([x y & args]
      (reduce -mul (-mul x y) args)))

(defn unchecked-add
  {:doc "Adds the arguments, returning 0 if no arguments."
   :signatures [[& args]]
   :added "0.1"}
  ([] 0)
  ([x] x)
  ([x y] (-unchecked-add x y))
  ([x y & args]
      (reduce -unchecked-add (-unchecked-add x y) args)))

(defn unchecked-subtract
  ([] 0)
  ([x] (-unchecked-subtract 0 x))
  ([x y] (-unchecked-subtract x y))
  ([x y & args]
      (reduce -unchecked-subtract (-unchecked-subtract x y) args)))

(defn unchecked-multiply
  ([] 1)
  ([x] x)
  ([x y] (-unchecked-multiply x y))
  ([x y & args]
      (reduce -unchecked-multiply (-unchecked-multiply x y) args)))

(defn /
  ([x] (-div 1 x))
  ([x y] (-div x y))
  ([x y & args]
      (reduce -div (-div x y) args)))

(defn quot [num div]
  (-quot num div))

(defn rem [num div]
  (-rem num div))

(defn rand-int
  {:doc "Returns a random integer between 0 (inclusive) and n (exclusive)."}
  [n]
  (if (zero? n)
    0
    (rem (rand) n)))

(defn =
  {:doc "Returns true if all the arguments are equivalent. Otherwise, returns false. Uses
-eq to perform equality checks."
   :signatures [[& args]]
   :added "0.1"}
  ([x] true)
  ([x y] (eq x y))
  ([x y & rest] (if (eq x y)
                  (apply = y rest)
                  false)))

(defn not=
  {:doc "Returns true if one (or more) of the arguments are not equivalent to the others. Uses
-eq to perform equality checks."
   :signatures [[& args]]
   :added "0.1"}
  ([x] false)
  ([x y] (not (eq x y)))
  ([x y & rest] (not (apply = x y rest))))

(defn <
  ([x] true)
  ([x y] (-lt x y))
  ([x y & rest] (if (-lt x y)
                  (apply < y rest)
                  false)))

(defn >
  ([x] true)
  ([x y] (-gt x y))
  ([x y & rest] (if (-gt x y)
                  (apply > y rest)
                  false)))

(defn <=
  ([x] true)
  ([x y] (-lte x y))
  ([x y & rest] (if (-lte x y)
                  (apply <= y rest)
                  false)))

(defn >=
  ([x] true)
  ([x y] (-gte x y))
  ([x y & rest] (if (-gte x y)
                  (apply >= y rest)
                  false)))

(defn pos?
  {:doc "Returns true if x is greater than zero."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (> x 0))

(defn neg?
  {:doc "Returns true if x is less than zero."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (< x 0))

(defn zero?
  {:doc "Returns true if x is equal to zero."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (= x 0))

(defn inc
  {:doc "Increments x by one."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (+ x 1))

(defn dec
  {:doc "Decrements x by one."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (- x 1))

(defn unchecked-inc
  {:doc "Increments x by one."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (unchecked-add x 1))

(defn unchecked-dec
  {:doc "Decrements x by one."
   :signatures [[x]]
   :added "0.1"}
  [x]
  (unchecked-subtract x 1))

(defn empty?
  {:doc "Returns true if the collection has no items, otherwise false."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? ICounted coll)
    (zero? (count coll))
    (not (seq coll))))

(defn not-empty?
  {:doc "Returns true if the collection has items, otherwise false."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (seq coll) true false))

(defn even?
  {:doc "Returns true if n is even."
   :signatures [[n]]
   :added "0.1"}
  [n]
  (zero? (rem n 2)))

(defn odd?
  {:doc "Returns true of n is odd."
   :signatures [[n]]
   :added "0.1"}
  [n]
  (= (rem n 2) 1))

(defn nth
  {:doc "Returns the element at the idx.  If the index is not found it will return an error.
         However, if you specify a not-found parameter, it will substitute that instead."
   :signatures [[coll idx] [coll idx not-found]]
   :added "0.1"}
  ([coll idx] (-nth coll idx))
  ([coll idx not-found] (-nth-not-found coll idx not-found)))

(defn first
  {:doc "Returns the first item in coll, if coll implements IIndexed nth will be used to retrieve
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 0 nil)
    (-first coll)))

(defn second
  {:doc "Returns the second item in coll, if coll implements IIndexed nth will be used to retrieve
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 1 nil)
    (first (next coll))))

(defn third
  {:doc "Returns the third item in coll, if coll implements IIndexed nth will be used to retrieve
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 2 nil)
    (first (next (next coll)))))

(defn fourth
  {:doc "Returns the fourth item in coll, if coll implements IIndexed nth will be used to retrieve
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 3 nil)
    (first (next (next (next coll))))))

(defn assoc
  {:doc "Associates the key with the value in the collection."
   :signatures [[m] [m k v] [m k v & kvs]]
   :added "0.1"}
  ([m] m)
  ([m k v]
     (-assoc m k v))
  ([m k v & rest]
     (apply assoc (-assoc m k v) rest)))

(defn dissoc
  {:doc "Removes the value associated with the keys from the collection."
   :signatures [[m] [m & ks]]
   :added "0.1"}
  ([m] m)
  ([m & ks]
    (reduce -dissoc m ks)))

(defn contains?
  {:doc "Checks if there is a value associated with key in the collection.

Does *not* check for the presence of a value in the collection, only whether
there's a value associated with the key. Use `some` for checking for values."
   :examples [["(contains? {:a 1} :a)" nil true]
              ["(contains? {:a 1} :b)" nil false]
              ["(contains? #{:a :b :c} :a)" nil true]
              ["(contains? [:a :b :c] 0)" nil true]
              ["(contains? [:a :b :c] 4)" nil false]
              ["(contains? [:a :b :c] :a)" nil false]]
   :signatures [[coll key]]
   :added "0.1"}
  [coll key]
  (-contains-key coll key))

(defn hash-set [& args]
  {:doc "Creates a hash-set from the arguments of the function."
   :added "0.1"}
  (set args))

(defn vec
  {:doc "Converts a reducable collection into a vector using the (optional) transducer."
   :signatures [[coll] [xform coll]]
   :added "0.1"}
  ([coll]
     (transduce conj! coll))
  ([xform coll]
     (transduce xform conj! coll)))

(defn get-val [inst]
  (get-field inst :val))

(defn comp
  {:doc "Composes the given functions, applying the last function first."
   :examples [["((comp inc first) [41 2 3])" nil 42]]
   :signatures [[f] [f & fs]]
   :added "0.1"}
  ([] identity)
  ([f] f)
  ([f1 f2]
     (fn [& args]
       (f1 (apply f2 args))))
  ([f1 f2 f3]
     (fn [& args]
       (f1 (f2 (apply f3 args)))))
  ([f1 f2 f3 & fs]
     (fn [& args]
       (apply (transduce comp (apply list f1 f2 f3 fs)) args))))

(defmacro cond
  {:doc "Checks if any of the tests is truthy, if so, stops and returns the value of the corresponding body."
   :signatures [[] [test then & clauses]]
   :added "0.1"}
  ([] nil)
  ([test then & clauses]
      `(if ~test
         ~then
         (cond ~@clauses))))

(defmacro try [& body]
  (loop [catch nil
         catch-sym nil
         body-items []
         finally nil
         body (seq body)]
    (let [form (first body)]
      (if form
        (if (not (seq? form))
          (recur catch catch-sym (conj body-items form) finally (next body))
          (let [head (first form)]
            (cond
             (= head 'catch) (if catch
                               (throw [:pixie.stdlib/SyntaxException
                                       "Can only have one catch clause per try"])
                               (recur (next (next form)) (first (next form)) body-items finally (next body)))
             (= head 'finally) (if finally
                                 (throw [:pixie.stdlib/SyntaxException
                                         "Can only have one finally clause per try"])
                                 (recur catch catch-sym body-items (next form) (next body)))
             :else (recur catch catch-sym (conj body-items form) finally (next body)))))
        (let [catch-data (cond
                                 (keyword? catch-sym) (let [sym (first catch)]
                                                        (assert (symbol? sym) (str "Invalid catch binding form"
                                                                                   catch))
                                                        [`[(if (= ~catch-sym (ex-data ~sym))
                                                             (do ~@(next catch))
                                                             (throw ~sym))]
                                                         sym])
                                 (seq? catch-sym) (let [sym (first catch)]
                                                        (assert (symbol? sym) (str "Invalid catch binding form"
                                                                                   catch))
                                                        [`[(if ~catch-sym
                                                             (do ~@(next catch))
                                                             (throw ~sym))]
                                                         sym])
                                 :else [catch catch-sym])]
          `(-try-catch
            (fn [] ~@body-items)
            ~(if catch
               `(fn [~(nth catch-data 1)] ~@(nth catch-data 0))
               `(fn [] nil))

            (fn [] ~@finally)))))))

#_(defn .
  {:doc "Access the field named by the symbol.

If further arguments are passed, invokes the method named by symbol, passing the object and arguments."
   :signatures [[obj sym] [obj sym & args]]
   :added "0.1"}
  ([obj sym]
     (get-field obj sym))
  ([obj sym & args]
     (apply (get-field obj sym) obj args)))

(defn true? [v] (identical? v true))
(defn false? [v] (identical? v false))

(defn number? [v] (instance? Number v))
(defn integer? [v] (instance? Integer v))
(defn float? [v] (instance? Float v))
(defn ratio? [v] (instance? Ratio v))

(defn char? [v] (instance? Character v))
(defn string? [v] (instance? String v))
(defn keyword? [v] (instance? Keyword v))

(defn list? [v] (instance? [PersistentList Cons] v))
(defn set? [v] (instance? PersistentHashSet v))
(defn map? [v] (satisfies? IMap v))
(defn fn? [v] (satisfies? IFn v))
(defn coll? [v] (satisfies? IPersistentCollection v))

(defn indexed? [v] (satisfies? IIndexed v))
(defn counted? [v] (satisfies? ICounted v))

(defn map-entry? [v] (satisfies? IMapEntry v))

(defn last
  {:doc "Returns the last element of the collection, or nil if none."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (cond
    (satisfies? IIndexed coll)
    (when (pos? (count coll))
      (nth coll (dec (count coll))))

    (satisfies? ISeq coll)
    (if (next coll)
      (recur (next coll))
      (first coll))

    (satisfies? ISeqable coll)
    (recur (seq coll))))

(defn butlast
  {:doc "Returns all elements but the last from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (loop [res []
         coll coll]
    (if (next coll)
      (recur (conj res (first coll)) (next coll))
      (seq res))))

(defn complement
  {:doc "Given a function, returns a new function which takes the same arguments
         but returns the opposite truth value."}
  [f]
  (assert (fn? f) "Complement must be passed a function")
  (fn
    ([] (not (f)))
    ([x] (not (f x)))
    ([x y] (not (f x y)))
    ([x y & more] (not (apply f x y more)))))

(defn constantly [x]
  {:doc "Returns a function that always returns x, no matter what it is called with."
   :examples [["(let [f (constantly :me)] [(f 1) (f \"foo\") (f :abc) (f nil)])"
               nil [:me :me :me :me]]]}
  (fn [& _] x))

(extend -count MapEntry (fn [self] 2))
(extend -nth MapEntry (fn map-entry-nth [self idx]
                          (cond (= idx 0) (-key self)
                                (= idx 1) (-val self))))
(extend -nth-not-found MapEntry (fn map-entry-nth [self idx not-found]
                                  (cond (= idx 0) (-key self)
                                        (= idx 1) (-val self)
                                        :else not-found)))
(extend -eq MapEntry (fn [self other]
                       (cond
                         (map-entry? other) (and (= (-key self)
                                                    (-key other))
                                                 (= (-val self)
                                                    (-val other)))
                         (vector? other) (= [(-key self) (-val self)]
                                            other)
                         :else (= (seq self) other))))

(extend -reduce MapEntry indexed-reduce)

(extend -str MapEntry
  (fn [v]
    (str "[" (transduce (interpose " ") string-builder v) "]")))
(extend -repr MapEntry
  (fn [v]
    (str "[" (transduce (comp (map -repr) (interpose " ")) string-builder v) "]")))

(extend -hash MapEntry
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))

(extend -seq MapEntry
  (fn [self]
    (list (-key self) (-val self))))

(defn select-keys
  {:doc "Returns a map containing only the entries of `m` where the entry's key is in `key-seq`."}
  [m key-seq]
  (with-meta
    (transduce
     (comp (filter (fn [k] (contains? m k)))
           (map (fn [k] [k (get m k)])))
     conj {} key-seq)
    (meta m)))

(defn keys
  {:doc "If called with no arguments, returns a transducer that will extract the key from each map entry. If passed
   a collection, will assume that it is a hashmap and return a vector of all keys from the collection."
   :signatures [[] [coll]]
   :added "0.1"}
  ([] (map key))
  ([m]
     (transduce (map key) conj! m)))

(defn vals
  {:doc "If called with no arguments, returns a transducer that will extract the key from each map entry. If passed
   a collection, will assume that it is a hashmap and return a vector of all keys from the collection."
   :signatures [[] [coll]]
   :added "0.1"}
  ([] (map val))
  ([m]
     (transduce (map val) conj! m)))

(extend -seq PersistentHashMap
        (fn [m]
          (reduce conj nil m)))

(extend -str PersistentHashMap
        (fn [v]
          (let [entry->str (map (fn [e] (vector (key e) " " (val e))))]
            (str "{" (transduce (comp entry->str (interpose [", "]) cat) string-builder v) "}"))))
(extend -repr PersistentHashMap
        (fn [v]
          (let [entry->str (map (fn [e] (vector (-repr (key e)) " " (-repr (val e)))))]
            (str "{" (transduce (comp entry->str (interpose [", "]) cat) string-builder v) "}"))))

(extend -hash PersistentHashMap
        (fn [v]
          (transduce cat unordered-hash-reducing-fn v)))

(extend -seq PersistentHashSet
        (fn [s]
          (reduce conj nil s)))

(extend -str PersistentHashSet
        (fn [s]
          (str "#{" (transduce (interpose " ") string-builder s) "}")))
(extend -repr PersistentHashSet
        (fn [s]
          (str "#{" (transduce (comp (map -repr) (interpose " ")) string-builder s) "}")))

(extend -empty Cons (fn [_] '()))
(extend -empty LazySeq (fn [_] '()))
(extend -empty PersistentList (fn [_] '()))
(extend -empty EmptyList (fn [_] '()))
(extend -empty PersistentVector (fn [_] []))
(extend -empty Array (fn [_] (make-array 0)))
(extend -empty PersistentHashMap (fn [_] {}))
(extend -empty PersistentHashSet (fn [_] #{}))

(extend -conj PersistentHashMap
        (fn [coll x]
            (cond
             (instance? MapEntry x)
             (assoc coll (key x) (val x))

             (instance? PersistentVector x)
             (if (= (count x) 2)
                 (assoc coll (nth x 0 nil) (nth x 1 nil))
                 (throw
                  [:pixie.stdlib/InvalidArgumentException
                   "Vector arg to map conj must be a pair"]))

             (satisfies? ISeqable x)
             (reduce conj coll (-seq x))

             :else
             (throw
              [:pixie.stdlib/InvalidArgumentException
               (str (type x) " cannot be conjed to a map")]))))

(extend -conj Cons
        (fn [coll x]
          (cons x coll)))

(extend -conj LazySeq
        (fn [coll x]
          (cons x coll)))

(defn empty
  {:doc "Returns an empty collection of the same type, or nil."
   :added "0.1"}
  [coll]
  (if (satisfies? IEmpty coll)
    (-empty coll)
    nil))

(extend -str Keyword
  (fn [k]
    (if (namespace k)
      (str ":" (namespace k) "/" (name k))
      (str ":" (name k)))))
(extend -repr Keyword -str)

(extend -repr Symbol -str)

(defn get
  {:doc "Gets an element from a collection implementing ILookup. Returns nil or the default value if not found."
   :added "0.1"}
  ([mp k]
     (get mp k nil))
  ([mp k not-found]
   (-val-at mp k not-found)))

(extend -invoke Keyword (fn
                          ([k m not-found]
                           (-val-at m k not-found))
                          ([k m]
                           (-val-at m k nil))))
(extend -invoke PersistentHashMap get)
(extend -invoke PersistentHashSet get)


(defn get-in
  {:doc "Gets a value from a nested collection at the \"path\" given by the keys."
   :examples [["(get-in {:a [{:b 42}]} [:a 0 :b])" nil 42]]
   :signatures [[m ks] [m ks not-found]]
   :added "0.1"}
  ([m ks]
     (reduce get m ks))
  ([m ks not-found]
     (loop [sentinel 'x
            m m
            ks (seq ks)]
       (if ks
         (let [m (get m (first ks) sentinel)]
           (if (identical? sentinel m)
             not-found
             (recur sentinel m (next ks))))
         m))))

(defn assoc-in
  {:doc "Associates a value in a nested collection given by the path.

Creates new maps if the keys are not present."
   :examples [["(assoc-in {} [:a :b :c] 42)" nil {:a {:b {:c 42}}}]]
   :added "0.1"}
  ([m ks v]
     (let [ks (seq ks)
           k  (first ks)
           ks (next ks)]
       (if ks
         (assoc m k (assoc-in (get m k) ks v))
         (assoc m k v)))))

(defn update-in
  {:doc "Updates a value in a nested collection."
   :examples [["(update-in {:a {:b {:c 41}}} [:a :b :c] inc)" nil {:a {:b {:c 42}}}]]
   :added "0.1"}
  [m ks f & args]
  (let [f (fn [m] (apply f m args))
        update-inner-f (fn update-inner-f
                         ([m f k]
                            (assoc m k (f (get m k))))
                         ([m f k & ks]
                            (assoc m k (apply update-inner-f (get m k) f ks))))]
    (apply update-inner-f m f ks)))

(def subs pixie.string.internal/substring)

(defmacro assert
  ([test]
     `(if ~test
        nil
        (throw [:pixie.stdlib/AssertionException
                "Assert failed"])))
  ([test msg]
     `(if ~test
        nil
        (throw [:pixie.stdlib/AssertionException
                (str "Assert failed: " ~msg)]))))

(defmacro resolve
  {:doc "Resolves the var associated with the symbol in the current namespace."
   :added "0.1"}
  [sym]
  `(resolve-in (this-ns-name) ~sym))

(defmacro binding [bindings & body]
  (let [bindings (apply hashmap bindings)
        set-vars (reduce (fn [res binding]
                           (conj res `(set! (resolve (quote ~(key binding))) ~(val binding))))
                         []
                         bindings)]
    `(do (push-binding-frame!)
         ~@set-vars
         (let [ret (do ~@body)]
           (pop-binding-frame!)
           ret))))

(defmacro ns [nm & body]
  (let [bmap (reduce (fn [m b]
                       (update-in m [(first b)] (fnil conj []) (rest b)))
                     {}
                     body)
        requires
        (do
          (assert (>= 1 (count (:require bmap)))
                  "Only one :require block can be defined per namespace")
            (map (fn [r] `(require ~@r)) (first (:require bmap))))

        old-style-requires
        (map (fn [r] `(require ~@r))
             (bmap 'require))]
    `(do (in-ns ~(keyword (name nm)))
         ~@requires
         ~@old-style-requires)))

(defn symbol? [x]
  (identical? Symbol (type x)))


(defmacro lazy-seq [& body]
  `(lazy-seq* (fn [] ~@body)))

(def Protocol @(resolve (symbol "/Protocol")))

(defn protocol? [x]
  (instance? Protocol x))

(defmacro deftype
  {:doc "Defines a custom type."
   :examples [["(deftype Person [name]
  IObject
  (-str [self]
    (str \"<Person \" (pr-str name) \">\")))"]
              ["(str (->Person \"James\"))" nil "<Person \"James\">"]]
   :added "0.1"}
  [nm fields & body]
  (let [ctor-name (symbol (str "->" (name nm)))
        fields (transduce (map (comp keyword name)) conj fields)
        field-syms (transduce (map (comp symbol name)) conj fields)
        mk-body (fn [body]
                  (let [fn-name (first body)
                        _ (assert (symbol? fn-name) "protocol override must have a name")
                        args (second body)
                        _ (assert (or (vector? args)
                                      (seq? args)) "protocol override must have arguments")
                        self-arg (first args)
                        _ (assert (symbol? self-arg) "protocol override must have at least one `self' argument")

                        rest (next (next body))
                        body (reduce
                              (fn [body f]
                                `[(local-macro [~(symbol (name f))
                                                 (get-field ~self-arg ~(keyword (name f)))]
                                                ~@body)])
                              rest
                              fields)]
                    `(fn ~(symbol (str fn-name "_" nm)) ~args ~@body)))
        bodies (reduce
                (fn [res body]
                  (cond
                   (symbol? body) (cond
                                   (= body 'Object) [body (second res) (third res)]
                                   (protocol? @(resolve-in *ns* body)) [@(resolve-in *ns* body)
                                                                        (second res)
                                                                        (conj (third res) body)]
                                   :else (throw
                                          [:pixie.stdlib/AssertionException
                                           (str "can only extend protocols or Object, not " body " of type " (type body))]))
                   (seq? body) (let [proto (first res) tbs (second res) pbs (third res)]
                                 (if (protocol? proto)
                                   [proto tbs (conj pbs body)]
                                   [proto (conj tbs body) pbs]))))
                [nil [] []]
                body)
        type-bodies (second bodies)
        proto-bodies (third bodies)
        all-fields (reduce (fn [r tb] (conj r (keyword (name (first tb))))) fields type-bodies)
        type-decl `(def ~nm (create-type ~(keyword (name nm)) ~all-fields))
        inst (gensym)
        ctor `(defn ~ctor-name ~field-syms
                (new ~nm
                     ~@field-syms
                     ~@(transduce (map (fn [type-body]
                                         (mk-body type-body)))
                                  conj
                                  type-bodies)))
        proto-bodies (transduce
                      (map (fn [body]
                             (cond
                              (symbol? body) `(satisfy ~body ~nm)
                              (seq? body) `(extend ~(first body) ~nm ~(mk-body body))
                              :else (assert false "Unknown body element in deftype, expected symbol or seq"))))
                      conj
                      proto-bodies)]
    `(do ~type-decl
         ~ctor
         ~@proto-bodies)))

(defn -make-record-assoc-body [cname fields]
  (let [k-sym (gensym "k")
        v-sym (gensym "v")
        this-sym (gensym "this")
        result `(-assoc [~this-sym ~k-sym ~v-sym]
                 (case ~k-sym
                   ~@(mapcat
                      (fn [k]
                        [k `(~cname ~@(mapv (fn [x]
                                             (if (= x k)
                                               v-sym
                                               `(get-field ~this-sym ~x)))
                                           fields))])
                      fields)
                   (throw [:pixie.stdlib/NotImplementedException
                           (str "Can't assoc to a unknown field: " ~k-sym)])))]
    result))

(defmacro defrecord
  {:doc "Defines a record type.

Similar to `deftype`, but supports construction from a map using `map->Type`
and implements IAssociative, ILookup and IObject."
   :added "0.1"}
  [nm field-syms & body]
  (let [ctor-name (symbol (str "->" (name nm)))
        map-ctor-name (symbol (str "map" (name ctor-name)))
        fields (transduce (map (comp keyword name)) conj field-syms)
        type-from-map `(defn ~map-ctor-name [m]
                         (apply ~ctor-name (map #(get m %) ~fields)))
        meta-gs (gensym "meta")
        default-bodies ['IAssociative
                        (-make-record-assoc-body ctor-name fields)

                        `(-contains-key [self k]
                                        (contains? ~(set fields) k))
                        `(-dissoc [self k]
                                  (throw [:pixie.stdlib/NotImplementedException
                                          "dissoc is not supported on defrecords"]))
                        'ILookup
                        (let [self-nm (gensym "self")
                              k-nm (gensym "k")]
                          `(-val-at [~self-nm ~k-nm not-found#]
                                    (case ~k-nm
                                      ~@(mapcat
                                         (fn [k]
                                           [k `(get-field ~self-nm ~k-nm)])
                                         fields)
                                      not-found#)))

                        'IReduce
                        `(-reduce [self# f# init#]
                                   (loop [fields# ~fields
                                          acc# init#]
                                     (if-let [field# (first fields#)]
                                       (let [acc# (f# acc# (map-entry field#
                                                                     (get-field self#
                                                                                field#)))]
                                         (if (reduced? acc#)
                                           @acc#
                                           (recur (next fields#) acc#)))
                                       acc#)))
                        'ICounted
                        `(-count [self] ~(count fields))

                        'ISeqable
                        `(-seq [self#]
                               (map #(map-entry % (get-field self# %))
                                    ~fields))

                        'IPersistentCollection
                        `(-conj [self# x]
                                (cond
                                  (instance? MapEntry x)
                                  (assoc self# (key x) (val x))
                                  (instance? PersistentVector x)
                                  (if (= (count x) 2)
                                    (assoc self# (first x) (second x))
                                    (throw
                                     [:pixie.stdlib/InvalidArgumentException
                                      "Vector arg to record conj must be a pair"]))))

                        `(-disj [self# x]
                                (throw [:pixie.stdlib/NotImplementedException
                                        "disj is not supported on defrecords"]))

                        'IMeta
                        `(-with-meta [self# ~meta-gs]
                                     (new ~nm
                                          ~@(conj field-syms meta-gs)))
                        `(-meta [self#] __meta)

                        'IObject
                        `(-str [self#]
                               (str "<" ~(name nm) " " (reduce #(assoc %1 %2 (%2 self#)) {} ~fields) ">"))
                        `(-eq [self other]
                              (and (instance? ~nm other)
                                   ~@(map (fn [field]
                                            `(= (~field self) (~field other)))
                                          fields)))
                        `(-hash [self]
                                (hash [~@field-syms]))
                        `IRecord]
        deftype-decl `(deftype ~nm ~(conj fields '__meta) ~@default-bodies ~@body)
        ctor `(defn ~ctor-name ~field-syms
                (new ~nm
                     ~@(conj field-syms nil)))]
    `(do ~type-from-map
         ~deftype-decl
         ~ctor)))

(defn print
  {:doc "Prints the arguments, seperated by spaces."
   :added "0.1"}
  [& args]
  (printf (transduce (interpose " ") str args))
  nil)

(defn println
  {:doc "Prints the arguments, separated by spaces, with a newline at the end."
   :added "0.1"}
  [& args]
  (puts (transduce (interpose " ") str args))
  nil)

(defn pr-str
  {:doc "Formats the arguments using -repr, separated by spaces, returning a string."
   :added "0.1"}
  [& args]
  (transduce (comp (map -repr) (interpose " ")) str args))

(defn pr
  {:doc "Prints the arguments using -repr, separated by spaces."
   :added "0.1"}
  [& args]
  (printf (apply pr-str args))
  nil)

(defn prn
  {:doc "Prints the arguments using -repr, separated by spaces, with a newline at the end."
   :added "0.1"}
  [& args]
  (puts (apply pr-str args))
  nil)

(defn repeatedly
  {:doc "Returns a lazy seq that contains the return values of repeated calls to f.

        Yields an infinite seq with one argument.
        With two arguments n specifies the number of elements."
   :examples [["(into '(:batman!) (repeatedly 8 (fn [] :na)))"
               nil (:na :na :na :na :na :na :na :na :batman!)]]
   :signatures [[f] [n f]]}
  ([f] (lazy-seq (cons (f) (repeatedly f))))
  ([n f] (take n (repeatedly f))))

(defmacro doseq
  {:doc "Evaluates all elements of the seq, presumably for side effects. Returns nil."
   :added "0.1"}
  [binding & body]
  (assert (= (count binding) 2) "expected a binding and a collection")
  (let [b (first binding)
        s (second binding)]
    `(loop [s# (seq ~s)]
       (if s#
         (let [~b (first s#)]
           ~@body
           (recur (next s#)))))))

(defmacro doc
  {:doc "Returns the documentation of the given value."
   :added "0.1"}
  [v]

  (let [vr (resolve-in *ns* v)
        x (if vr @vr)
        doc (get (meta x) :doc)
        has-doc? (if doc true (get (meta x) :signatures))]
    (cond
     (satisfies? IDoc x) (-doc x)
     has-doc? (let [sigs (get (meta x) :signatures)
                    examples (get (meta x) :examples)
                    indent (fn [s]
                             (if (>= (pixie.string.internal/index-of s "\n") 0)
                               (apply str "\n" (map #(str "  " % "\n") (pixie.string.internal/split s "\n")))
                               s))]
                (println (str (namespace vr) "/" (name vr)))
                (if sigs
                  (prn (seq sigs)))
                (if doc
                  (do (println)
                      (println doc)))
                (if examples
                  (do
                    (println)
                    (doseq [example examples]
                      (println (str "  user => " (indent (first  example))))
                      (if (second example)
                        (print (indent (second example))))
                      (if (contains? example 2)
                        (println (str "  " (-repr (third example))))))))
                (println)
                nil)
     (the-ns v) (doc-ns v))))

(defn doc-ns
  {:doc "Prints a summarizing documentation of the symbols in a namespace."
   :added "0.1"}
  [ns]
  (let [ns (the-ns ns)
        short-doc (fn [x]
                    (let [doc (get (meta x) :doc)]
                      (if doc
                        (let [newline (pixie.string.internal/index-of doc "\n")]
                          (pixie.string.internal/substring doc 0 (if (< newline 0) (count doc) newline))))))]
    (println (str (name ns) ":"))
    (vec (map (fn [sym]
                (print (str "  " (name sym)))
                (let [doc (short-doc @(resolve-in ns sym))]
                  (if doc
                    (print (str (apply str (repeat (- 30 (count (name sym))) " "))
                                doc))))
                (println))
              (keys (ns-map ns))))
    nil))

(defn swap!
  {:doc "Swaps the value in the atom, by applying f to the current value.

The new value is thus `(apply f current-value-of-atom args)`."
   :signatures [[atom f & args]]
   :added "0.1"}
  [a f & args]
  (reset! a (apply f @a args)))

(defn nil? [x]
  (identical? x nil))

(defn some? [x]
  {:doc "Returns true if x is not nil."}
  (not (nil? x)))

(defn fnil [f else]
  (fn [x & args]
    (apply f (if (nil? x) else x) args)))

(defmacro foreach [binding & body]
  (assert (= 2 (count binding)) "binding and collection required")
  `(reduce
    (fn [_ ~(nth binding 0 nil)]
        ~@body
        nil)
    nil
    ~(nth binding 1 nil)))

(defmacro dotimes
  {:doc "Executes the expressions in the body n times."
   :examples [["(dotimes [i 3] (println i))" "1\n2\n3\n"]]
   :signatures [[[i n] & body]]
   :added "0.1"}
  [bind & body]
  (let [b (nth bind 0 nil)]
    `(let [max# ~(nth bind 1 nil)]
       (loop [~b 0]
         (if (= ~b max#)
           nil
           (do ~@body
               (recur (inc ~b))))))))

(defmacro and
  {:doc "Checks if the given expressions return truthy values, returning the last, or false."
   :examples [["(and true false)" nil false]
              ["(and 1 2 3)" nil 3]
              ["(and 1 false 3)" nil false]]
   :added "0.1"}
  ([] true)
  ([x] x)
  ([x y] `(if ~x ~y false))
  ([x y & more] `(if ~x (and ~y ~@more) false)))

(defmacro or
  {:doc "Returns the value of the first expression that returns a truthy value, or false."
   :examples [["(or 1 2 3)" nil 1] ["(or false 2)" nil 2] ["(or false nil)" nil nil]]
   :added "0.1"}
  ([] false)
  ([x] x)
  ([x y] `(let [r# ~x]
            (if r# r# ~y)))
  ([x y & more] `(let [r# ~x]
                   (if r# r# (or ~y ~@more)))))

(defmacro when [test & body]
  `(if ~test (do ~@body)))

(defmacro when-not [test & body]
  `(if (not ~test) (do ~@body)))

(defmacro when-let [binding & body]
  (let [bind (nth binding 0 nil)
        test (nth binding 1 nil)]
    `(let [tmp# ~test]
       (when tmp#
         (let [~bind tmp#]
           ~@body)))))

(defmacro if-not
  ([test then] `(if-not ~test ~then nil))
  ([test then else]
   `(if (not ~test) ~then ~else)))

(defmacro if-let
  ([binding then] `(if-let ~binding ~then nil))
  ([binding then else]
     (let [bind (nth binding 0 nil)
           test (nth binding 1 nil)]
       `(let [tmp# ~test]
          (if tmp#
            (let [~bind tmp#]
              ~then)
            ~else)))))

(defn some
  {:doc "Returns the first true value of the predicate for the elements of the collection."
   :signatures [[pred coll]]
   :added "0.1"}
  [pred coll]
  (if (seq coll)
    (or (pred (first coll))
        (some pred (next coll)))
    false))

(defn nnext
  {:doc "Equivalent to (next (next coll))."
   :added "0.1"}
  [coll]
  (next (next coll)))

(defn nthnext
  {:doc "Returns the result of calling next n times on the collection."
   :examples [["(nthnext [1 2 3 4 5] 2)" nil (3 4 5)]
              ["(nthnext [1 2 3 4 5] 7)" nil nil]]
   :added "0.1"}
  [coll n]
  (loop [n n
         xs (seq coll)]
    (if (and xs (pos? n))
      (recur (dec n) (next xs))
      xs)))

(defn ith
  {:doc "Returns the ith element of the collection, negative values count from the end.
         If an index is out of bounds, will throw an Index out of Range exception.
         However, if you specify a not-found parameter, it will substitute that instead."
   :signatures [[coll i] [coll idx not-found]]
   :added "0.1"}
  ([coll i]
     (when coll
       (let [idx (if (neg? i) (+ i (count coll)) i)]
         (nth coll idx))))
  ([coll i not-found]
     (when coll
       (let [idx (if (neg? i) (+ i (count coll)) i)]
         (nth coll idx not-found)))))

(defn ensure-reduced [x]
  (if (reduced? x)
    x
    (reduced x)))

(defn take
  {:doc "Takes n elements from the collection, or fewer, if not enough."
   :added "0.1"}
  ([n]
   (fn [rf]
     (let [seen (atom 0)]
       (fn
         ([] (rf))
         ([result] (rf result))
         ([result input]
          (let [s (swap! seen inc)]
            (cond (< s n) (rf result input)
                  (= s n) (ensure-reduced (rf result input))
                  :else (reduced result))))))))
  ([n coll]
   (lazy-seq
     (when (pos? n)
       (when-let [s (seq coll)]
         (cons (first s) (take (dec n) (next s))))))))

(defn drop
  {:doc "Drops n elements from the start of the collection."
   :added "0.1"}
  ([n]
   (fn [rf]
     (let [seen (atom 0)]
       (fn
         ([] (rf))
         ([result]
          (rf result))
         ([result input]
          (let [s (swap! seen inc)]
            (if (> s n)
              (rf result input)
              result)))))))
  ([n coll]
   (let [s (seq coll)]
     (if (and (pos? n) s)
       (recur (dec n) (next s))
       s))))

(defn split-at
  {:doc "Returns a vector of the first n elements of the collection, and the remaining elements."
   :examples [["(split-at 2 [:a :b :c :d :e])" nil
               [(:a :b) (:c :d :e)]]]}
  [n coll]
  [(take n coll) (drop n coll)])

(defmacro while
  {:doc "Repeatedly executes body while test expression is true. Presumes
  some side-effect will cause test to become false/nil. Returns nil."
  :added "0.1"}
  [test & body]
    `(loop []
      (when ~test
        ~@body
        (recur))))

(defn take-while
  {:doc "Returns a lazy sequence of successive items from coll while
        (pred item) returns true. pred must be free of side-effects.
        Returns a transducer when no collection is provided."
  :added "0.1"}
  ([pred]
     (fn [rf]
       (fn
         ([] (rf))
         ([result] (rf result))
         ([result input]
            (if (pred input)
              (rf result input)
              (reduced result))))))
  ([pred coll]
     (lazy-seq
      (when-let [s (seq coll)]
        (when (pred (first s))
          (cons (first s) (take-while pred (rest s))))))))


(defn drop-while
  {:doc "Returns a lazy sequence of the items in coll starting from the
        first item for which (pred item) returns logical false.  Returns a
        stateful transducer when no collection is provided."
   :added "0.1"}
   ([pred]
     (fn [rf]
       (let [dv (atom true)]
         (fn
           ([] (rf))
           ([result] (rf result))
           ([result input]
              (let [drop? @dv]
                (if drop?
                  (if (pred input)
                    result
                    (do
                      (reset! dv nil)
                      (rf result input)))
                  (rf result input))))))))
  ([pred coll]
     (let [step (fn [pred coll]
                  (let [s (seq coll)]
                    (if (and s (pred (first s)))
                      (recur pred (rest s))
                      s)))]
       (lazy-seq (step pred coll)))))

(defn cycle
  [coll]
  (if (empty? coll)
    ()
    (let [cycle'
          (fn cycle' [current]
            (lazy-seq
             (cons
              (first current)
              (let [rst (rest current)]
                (cycle' (if (empty? rst) coll rst))))))]
      (cycle' coll))))

;; TODO: use a transient map in the future
(defn group-by
  {:doc "Groups the collection into a map keyed by the result of applying f on each element. The value at each key is a vector of elements in order of appearance."
   :examples [["(group-by even? [1 2 3 4 5])" nil {false [1 3 5] true [2 4]}]
              ["(group-by (partial apply +) [[1 2 3] [2 4] [1 2]])" nil {6 [[1 2 3] [2 4]] 3 [[1 2]]}]]
   :signatures [[f coll]]
   :added "0.1"}
  [f coll]
  (reduce (fn [res elem]
            (update-in res [(f elem)] (fnil conj []) elem))
          {}
          coll))

;; TODO: use a transient map in the future
(defn frequencies
  {:doc "Returns a map with distinct elements as keys and the number of occurences as values."
   :added "0.1"}
  [coll]
  (reduce (fn [res elem]
            (update-in res [elem] (fnil inc 0)))
          {}
          coll))

(defn partition
  {:doc "Separates the collection into collections of size n, starting at the beginning, with an optional step size.

The last element of the result contains the remaining element, not necessarily of size n if
not enough elements were present."
   :examples [["(partition 2 [1 2 3 4 5 6])" nil ((1 2) (3 4) (5 6))]
              ["(partition 2 [1 2 3 4 5])" nil ((1 2) (3 4) (5))]
              ["(partition 2 1 [1 2 3 4 5])" nil ((1 2) (2 3) (3 4) (4 5) (5))]]
   :signatures [[n coll] [n step coll]]
   :added "0.1"}
  ([n coll] (partition n n coll))
  ([n step coll]
   (when-let [s (seq coll)]
     (lazy-seq
       (cons (take n s) (partition n step (drop step s)))))))

(defn partitionf
  {:doc "A generalized version of partition. Instead of taking a constant number of elements,
         this function calls f with the remaining collection to determine how many elements to
         take."
   :examples [["(partitionf first [2 :a, 3 :a :b, 4 :a :b :c])"
               nil ((2 :a) (3 :a :b) (4 :a :b :c))]]}
  [f coll]
  (when-let [s (seq coll)]
    (lazy-seq
      (let [n (f s)]
        (cons (take n s)
              (partitionf f (drop n s)))))))

(defn map-indexed
  {:doc "Returns a lazy sequence consisting of the
  result of applying f to 0 and the first item of coll, followed by
  applying f to 1 and the second item in coll, etc, until coll is
  exhausted. Thus function f should accept 2 arguments, index and
  item. Returns a stateful transducer when no collection is provided."
   :added "0.1"
   :signatures [[f] [f coll]]}
  ([f]
   (fn [rf]
     (let [i (atom -1)]
       (fn
         ([] (rf))
         ([result] (rf result))
         ([result input]
          (rf result (f (swap! i inc) input)))))))
  ([f coll]
   (let [mapi (fn mapi [i coll]
                (lazy-seq
                 (when-let [s (seq coll)]
                   (cons (f i (first s))
                         (mapi (inc i) (rest s))))))]
     (mapi 0 coll))))

(defn keep-indexed
  {:doc "Returns a lazy sequence of the non-nil
  results of (f index item). Note, this means false return values will
  be included.  f must be free of side-effects.  Returns a stateful
  transducer when no collection is provided."
   :signatures [[f] [f coll]]
   :added "0.1"}
  ([f]
   (fn [rf]
     (let [iv (atom -1)]
       (fn
         ([] (rf))
         ([result] (rf result))
         ([result input]
          (let [i (swap! iv inc)
                v (f i input)]
            (if (nil? v)
              result
              (rf result v))))))))
  ([f coll]
   (let [keepi (fn keepi [i coll]
                 (lazy-seq
                  (when-let [s (seq coll)]
                    (let [x (f i (first s))]
                      (if (nil? x)
                        (keepi (inc i) (rest s))
                        (cons x (keepi (inc i) (rest s))))))))]
     (keepi 0 coll))))

(defn reductions
  {:doc "Returns a lazy seq of the intermediate values of the
  reduction (as per reduce) of coll by f, starting with init."
   :added "0.1"
   :signatures [[f coll] [f init coll]]}
  ([f coll]
   (lazy-seq
    (if-let [s (seq coll)]
      (reductions f (first s) (rest s))
      (list (f)))))
  ([f init coll]
   (if (reduced? init)
     (list @init)
     (cons init
           (lazy-seq
            (when-let [s (seq coll)]
              (reductions f (f init (first s)) (rest s))))))))

(defn completing
  "Takes a reducing function f of 2 args and returns a fn suitable for
  transduce by adding an arity-1 signature that calls cf (default -
  identity) on the result argument."
  ([f] (completing f identity))
  ([f cf]
     (fn
       ([] (f))
       ([x] (cf x))
       ([x y] (f x y)))))

(deftype Eduction [xform coll]
   IReduce
   (-reduce [self f init]
     ;; NB (completing f) isolates completion of inner rf from outer rf
     (transduce xform (completing f) init coll))

   ISeqable
   (-seq [self]
     (sequence xform coll)))

(defn eduction
  "Returns a reducible/iterable application of the transducers
  to the items in coll. Transducers are applied in order as if
  combined with comp. Note that these applications will be
  performed every time reduce/iterator is called."
  [& xforms]
  (->Eduction (apply comp (butlast xforms)) (last xforms)))

(defn destructure [binding expr]
  (cond
   (symbol? binding) [binding expr]
   (vector? binding) (let [name (gensym "vec__")]
                       (reduce conj [name expr]
                               (destructure-vector binding name)))
   (map? binding) (let [name (gensym "map__")]
                    (reduce conj [name expr]
                            (destructure-map binding name)))
   :else (throw [:pixie.stdlib/AssertionException
                 (str "unsupported binding form: " binding)])))

(defn destructure-vector [binding-vector expr]
  (loop [bindings (seq binding-vector)
         i 0
         res []]
    (if bindings
      (let [binding (first bindings)]
        (cond
         (= binding '&) (recur (nnext bindings)
                               (inc (inc i))
                               (reduce conj res (destructure (second bindings) `(nthnext ~expr ~i))))
         (= binding :as) (reduce conj res (destructure (second bindings) expr))
         :else (recur (next bindings)
                      (inc i)
                      (reduce conj res (destructure (first bindings) `(nth ~expr ~i nil))))))
      res)))

(defn destructure-map [binding-map expr]
  (let [defaults (or (:or binding-map) {})
        res
        (loop [bindings (seq binding-map)
               res []]
          (if bindings
            (let [binding (key (first bindings))
                  binding-key (val (first bindings))]
              (if (contains? #{:or :as :keys} binding)
                (recur (next bindings) res)
                (recur (next bindings)
                       (reduce conj res (destructure binding `(get ~expr ~binding-key ~(get defaults binding)))))))
            res))
        expand-with (fn [convert] #(vector % `(get ~expr ~(convert %) ~(get defaults %))))
        res (if (contains? binding-map :keys) (transduce (map (expand-with (comp keyword name))) concat res (get binding-map :keys)) res)
        res (if (contains? binding-map :as)
              (reduce conj res [(get binding-map :as) expr])
              res)]
    res))

(defmacro let
  {:doc "Makes the bindings availlable in the body.

The bindings must be a vector of binding-expr pairs. The binding can be a destructuring
binding, as below.

Vector destructuring:
  [x y z]           binds the first three elements of the collection to x, y and z
  [x y & rest]      binds rest to the elements after the first two elements of the collection
  [x y :as v]       binds the value of the complete collection to v

Map destructuring:
  {a :a, b :b}      binds a and b to the values associated with :a and :b
  {a :a :as m}      binds the value of the complete collection to m
  {a :a :or {a 42}} binds a to the value associated with :a, or 42, if not present
  {:keys [a b c]}   binds a, b and c to the values associated with :a, :b and :c

All these forms can be combined and nested, in the example below:

(let [[x y [z :as iv] :as v] [1 2 [3 4 5] 6 7]
      {a :a [b c {:keys [d]}] :more :or {a 42}} {:a 1, :more [1 2 {:d 3, :e 4}]}]
  ...)

For more information, see http://clojure.org/special_forms#binding-forms"}
  [bindings & body]
  (let* [destructured-bindings (transduce (map (fn [args]
                                                 (assert (= 2 (count args)) (str "Bindings must be in pairs, not " args
                                                                                 " " (meta (first args))))
                                                 (apply destructure args)))
                                          concat
                                          []
                                          (partition 2 bindings))]
        `(let* ~destructured-bindings
               ~@body)))

(extend -nth ISeq (fn [s n]
                    (when (empty? s)
                      (throw
                       [:pixie.stdlib/OutOfRangeException
                        "Index out of Range"]))
                    (if (and (pos? n) s)
                      (recur (next s) (dec n))
                      (if (zero? n)
                        (first s)
                        (throw [:pixie.stdlib/OutOfRangeException
                                "Index out of Range"])))))
(extend -nth-not-found ISeq (fn [s n not-found]
                              (if (and (pos? n) s)
                                (recur (next s) (dec n) not-found)
                                (or (first s) not-found))))

(defn abs
  {:doc "Returns the absolute value of x."
   :added "0.1"}
  [x]
  (if (< x 0)
    (* -1 x)
    x))

(deftype Repeat [n x]
  IReduce
  (-reduce [self f init]
    (loop [i 0
           acc init]
      (if (< i n)
        (let [acc (f acc x)]
          (if (reduced? acc)
            @acc
            (recur (inc i) acc)))
        acc)))
  ICounted
  (-count [self]
    n)
  IIndexed
  (-nth [self idx]
    (if (and (>= idx 0) (< idx n))
      x
      (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"])))
  (-nth-not-found [self idx not-found]
    (if (and (>= idx 0) (< idx n))
      x
      not-found))
  ISeqable
  (-seq [self]
    (when (>= n 1)
      (cons x (lazy-seq* (fn [] (->Repeat (dec n) x)))))))

(extend -str Repeat
        (fn [v]
          (-str (seq v))))

(extend -repr Repeat -str)

(defn repeat
  {:doc "Returns a seqable of repetitions of a value."
   :examples [["(repeat 3 :buffalo)" nil (:buffalo :buffalo :buffalo)]
              ["(map vector '(1 2 3) (repeat :ahahah))" nil ([1 :ahahah] [2 :ahahah] [3 :ahahah])]]
   :signatures [[x] [n x]]
   :added "0.1"}
  ([x]
   (let [positive-infinity (/ 1.0 0)]
     (repeat positive-infinity x)))
  ([n x]
   (->Repeat n x)))

(deftype Range [start stop step]
  IReduce
  (-reduce [self f init]
    (loop [i start
           acc init]
      (if (or (and (> step 0) (< i stop))
              (and (< step 0) (> i stop))
              (and (= step 0)))
        (let [acc (f acc i)]
          (if (reduced? acc)
            @acc
            (recur (+ i step) acc)))
        acc)))
  ICounted
  (-count [self]
    (if (or (and (< start stop) (< step 0))
            (and (> start stop) (> step 0))
            (= step 0))
      0
      (abs (quot (- start stop) step))))
  IIndexed
  (-nth [self idx]
    (when (or (= start stop 0) (neg? idx))
      (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"]))
    (let [cmp (if (< start stop) < >)
          val (+ start (* idx step))]
      (if (cmp val stop)
        val
        (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"]))))
  (-nth-not-found [self idx not-found]
    (let [cmp (if (< start stop) < >)
          val (+ start (* idx step))]
      (if (cmp val stop)
        val
       not-found)))
  ISeq
  (-first [this]
    (when (not= start stop)
      start))
  (-next  [this]
    (let [i (+ step start)]
      (when (or (and (> step 0) (< i stop))
                    (and (< step 0) (> i stop))
                    (and (= step 0)))
        (range i stop step))))
  ISeqable
  (-seq [self] self))

(extend -str Range
        (fn [v]
          (str "(" (transduce (interpose " ") string-builder v) ")")))

(extend -repr Range
        (fn [v]
          (str "(" (transduce (interpose " ") string-builder v) ")")))

(defn range
  {:doc "Returns a range of numbers."
   :examples [["(seq (range 3))" nil (0 1 2)]
              ["(seq (range 3 5))" nil (3 4)]
              ["(seq (range 0 10 2))" nil (0 2 4 6 8)]
              ["(seq (range 5 -1 -1))" nil (5 4 3 2 1 0)]]
   :signatures [[] [stop] [start stop] [start stop step]]
   :added "0.1"}
  ([] (->Range 0 MAX-NUMBER 1))
  ([stop] (->Range 0 stop 1))
  ([start stop] (->Range start stop 1))
  ([start stop step] (->Range start stop step)))

(extend -eq ISeqable -seq-eq)

(deftype Unknown [])
(def unknown (->Unknown))

(extend -eq PersistentHashMap
        (fn [self other]
          (cond
           (not (map? other)) false
           (not= (count self) (count other)) false
           :else (reduce (fn
                           ([_] true)
                           ([_ entry]
                              (let [other-val (get other (key entry) unknown)]
                                (if (not= other-val (val entry))
                                  (reduced false)
                                  true))))
                         true
                         self))))

(defn filter
  {:doc "Filters the collection for elements matching the predicate."
   :signatures [[pred] [pred coll]]
   :added "0.1"}
  ([pred]
   (fn [xf]
     (fn
       ([] (xf))
       ([acc] (xf acc))
       ([acc i] (if (pred i)
                  (xf acc i)
                  acc)))))
  ([pred coll]
   (lazy-seq
     (when-let [s (seq coll)]
       (let [[f & r] s]
         (if (pred f)
           (cons f (filter pred r))
           (filter pred r)))))))

(defn remove
  {:doc "Removes any element from the collection which matches the predicate. The complement of filter."
   :signatures [[pred] [pred coll]]
   :added "0.1"}
  ([pred]
   (filter (complement pred)))
  ([pred coll]
   (filter (complement pred) coll)))

(defn sequence
  "Returns a lazy sequence of `data`, optionally transforming it using `xform`"
  ([coll]
   (if (seq? coll) coll
       (or (seq coll) ())))
  ([xform coll]
   (let [step (fn step [xform acc xs]
                (if-let [s (seq xs)]
                  (let [next-acc ((xform conj) acc (first s))]
                    (if (= acc next-acc) (step xform next-acc (next s))
                        (concat (drop (count acc) next-acc) (step xform next-acc (next s)))))
                  nil))]
     (lazy-seq (step xform [] coll)))))

(defn distinct
  {:doc "Returns the distinct elements in the collection."
   :signatures [[] [coll]]
   :added "0.1"}
  ([] (fn [xf]
        (let [seen (atom #{})]
          (fn
            ([] (xf))
            ([acc] (xf acc))
            ([acc i]
               (if (contains? @seen i)
                 acc
                 (do
                   (swap! seen conj i)
                   (xf acc i))))))))
  ([coll]
   (let [step (fn step [xs seen]
                (lazy-seq
                  ((fn [f seen]
                     (when-let [s (seq f)]
                       (let [xs (first s)]
                         (if (contains? seen xs)
                           (step (rest s) seen)
                           (cons xs (step (rest s) (conj seen xs)))))))
                   xs seen)))]
     (step coll #{}))))

(defn keep
  ([f]
   (fn [xf]
     (fn
       ([] (xf))
       ([acc] (xf acc))
       ([acc i] (let [result (f i)]
                  (if result
                    (xf acc result)
                    acc))))))
  ([f coll]
   (lazy-seq
     (when-let [s (seq coll)]
       (let [[first & rest] s
             result (f first)]
         (if result
           (cons result (keep f rest))
           (keep f rest)))))))

(defn refer
  {:doc "Refer to the specified vars from a namespace directly.

Supported filters:
  :rename   refer to the given vars under a different name
  :exclude  don't refer the given vars
  :refer
    :all    refer all vars
    :refer  refer only the given vars
    :only   same as refer

user => (refer 'pixie.string :refer :all)
user => (refer 'pixie.string :only '(index-of starts-with? ends-with?))
user => (refer 'pixie.string :rename '{index-of find})
user => (refer 'pixie.string :exclude '(substring))"
   :added "0.1"}
  [ns-sym & filters]
  (let [ns (or (the-ns ns-sym) (throw [:pixie.stdlib/NamespaceNotFoundException
                                       (str "No such namespace: " ns-sym)]))
        filters (apply hashmap filters)
        nsmap (ns-map ns)
        rename (or (:rename filters) {})
        exclude (set (:exclude filters))
        refers (if (= :all (:refer filters))
                 (keys nsmap)
                 (or (:refer filters) (:only filters)))]
    (when (and refers (not (satisfies? ISeqable refers)))
      (throw [:pixie.stdlib/InvalidArgumentException
              ":only/:refer must be a collection of symbols"]))
    (when-let [as (:as filters)]
      (refer-ns *ns* ns-sym as))
    (loop [syms (seq refers)]
      (if (not syms)
        nil
        (do
          (let [sym (first syms)]
            (when-not (exclude sym)
              (let [v (nsmap sym)]
                (when-not v
                  (throw [:pixie.stdlib/SymbolNotFoundException
                          (str sym "does not exist")]))
                (refer-symbol *ns* (or (rename sym) sym) v))))
          (recur (next syms)))))
    nil))



(defmacro require [ns & args]
  `(do (load-ns (quote ~ns))
       (assert (the-ns (quote ~ns))
               (str "Couldn't find the namespace " (quote ~ns) " after loading the file"))

       (apply refer (quote [~ns ~@args]))))



(defn merge-with
  {:doc "Returns a map consisting of each map merged onto the first. If a
         map contains a key that already exists in the result, the
         value will be f applied to the value in the result map and
         the value from the map being merged in."
   :examples [["(merge-with + {:a 1 :b 2} {:a 3 :c 5} {:c 3 :d 4})" nil {:a 4, :b 2, :c 8 :d 4}]]}
  [f & maps]
  (cond
   (empty? maps) nil
   (= (count maps) 1) (first maps)
   :else (let [merge2 (fn [m1 m2]
                        (reduce (fn [res e]
                                  (let [k (key e) v (val e)]
                                    (if (contains? m1 k)
                                      (assoc res k (f (get m1 k) v))
                                      (assoc res k v))))
                                (or m1 {})
                                m2))]
           (reduce merge2 (first maps) (next maps)))))

(defn every?
  {:doc "Checks if every element of the collection satisfies the predicate."
   :added "0.1"}
  [pred coll]
  (cond
   (nil? (seq coll)) true
   (pred (first coll)) (recur pred (next coll))
   :else false))

; If you want a fn that uses destructuring in its parameter list, place
; it after this definition. If you don't, you will get compile failures
; in unrelated files.
(defmacro fn
  {:doc "Creates a function.

The following two forms are allowed:
  (fn name? [param*] & body)
  (fn name? ([param*] & body)+)

The params can be destructuring bindings, see `(doc let)` for details."}
  [& decls]
  (let [name (if (symbol? (first decls)) [(first decls)] nil)
        decls (if name (next decls) decls)
        decls (cond
               (vector? (first decls)) (list decls)
               ;(satisfies? ISeqable (first decls)) decls
               ;:else (throw (str "expected a vector or a seq, got a " (type decls)))
               :else decls)
        decls (seq (map (fn* [decl]
                          (let [argv (first decl)
                                names (vec (map #(if (= % '&) '& (gensym "arg__")) argv))
                                bindings (loop [i 0 bindings []]
                                           (if (< i (count argv))
                                             (if (= (nth argv i) '&)
                                               (recur (inc i) bindings)
                                               (recur (inc i) (reduce conj bindings [(nth argv i) (nth names i)])))
                                             bindings))
                                body (next decl)
                                conds (when (and (next body) (map? (first body)))
                                        (first body))
                                pre (:pre conds)
                                post (:post conds)
                                body (if conds (next body) body)
                                body (if post
                                       `((let [~'% ~(if (> (count body) 1)
                                                      `(do ~@body)
                                                      (first body))]
                                           ~@(map (fn* [c] `(assert ~c (str '~c))) post)
                                           ~'%))
                                       body)
                                body (if pre
                                       (seq (concat
                                             (map (fn* [c] `(assert ~c (str '~c))) pre)
                                             body))
                                       body)]
                            (if (every? symbol? argv)
                              `(~argv ~@body)
                              `(~names
                                (let ~bindings
                                  ~@body)))))
                        decls))]
    (if (= (count decls) 1)
      `(fn* ~@name ~(first (first decls)) ~@(next (first decls)))
      `(fn* ~@name ~@decls))))

;; TODO: implement :>> like in Clojure?
(defmacro condp
  "Takes a binary predicate, an expression and a number of two-form clauses.
Calls the predicate on the first value of each clause and the expression.
If the result is truthy returns the second value of the clause.

If the number of arguments is odd and no clause matches, the last argument is returned.
If the number of arguments is even and no clause matches, throws an exception."
  [pred-form expr & clauses]
  (let [x (gensym 'expr), pred (gensym 'pred)]
    `(let [~x ~expr, ~pred ~pred-form]
       (cond ~@(mapcat
                 (fn [[a b :as clause]]
                   (if (> (count clause) 1)
                     `((~pred ~a ~x) ~b)
                     `(:else ~a)))
                 (partition 2 clauses))
             :else (throw [:pixie.stdlib/MissingClauseException
                           "No matching clause!"])))))

(defmacro case
  "Takes an expression and a number of two-form clauses.
Checks for each clause if the first part is equal to the expression.
If yes, returns the value of the second part.

The first part of each clause can also be a set. If that is the case, the clause matches when the result of the expression is in the set.

If the number of arguments is odd and no clause matches, the last argument is returned.
If the number of arguments is even and no clause matches, throws an exception."
  [expr & args]
  `(condp #(if (set? %1) (%1 %2) (= %1 %2))
     ~expr ~@args))




(deftype MultiMethod [dispatch-fn default-val methods]
  IMessageObject
  (-get-attr [this kw]
    (case kw
      :methods methods
      :else nil))
  IFn
  (-invoke [self & args]
    (let [dispatch-val (apply dispatch-fn args)
          method (if (contains? @methods dispatch-val)
                   (get @methods dispatch-val)
                   (get @methods default-val))
          _ (assert method (str "no method defined for " dispatch-val))]
      (apply method args))))


(defmacro defmulti
  {:doc "Defines a multimethod, which dispatches to its methods based on dispatch-fn."
   :examples [["(defmulti greet first)"]
              ["(defmethod greet :hi [[_ name]] (str \"Hi, \" name \"!\"))"]
              ["(defmethod greet :hello [[_ name]] (str \"Hello, \" name \".\"))"]
              ["(greet [:hi \"Jane\"])" nil "Hi, Jane!"]]
   :signatures [[name dispatch-fn & options]]
   :added "0.1"}
  [name & args]
  (let [[meta args] (if (string? (first args))
                      [{:doc (first args)} (next args)]
                      [{} args])
        [meta args] (if (map? (first args))
                      [(merge meta (first args)) (next args)]
                      [meta args])
        dispatch-fn (first args)
        options (apply hashmap (next args))]
    `(def ~name (->MultiMethod ~dispatch-fn ~(get options :default :default) (atom {})))))

(defmacro defmethod
  {:doc "Defines a method of a multimethod. See `(doc defmulti)` for details."
   :signatures [[name dispatch-val [param*] & body]]
   :added "0.1"}
  [name dispatch-val params & body]
  `(do
     (let [methods (.-methods ~name)]
       (swap! methods
              assoc
              ~dispatch-val (fn ~params
                              ~@body))
       ~name)))

(defmulti Foo :r)
(defmethod Foo :r
  [x] x)

(defmacro declare
  {:doc "Forward declares the given variable names, setting them to nil."
   :added "0.1"}
  [& nms]
  (let [defs (map (fn [nm] `(def ~nm)) (seq nms))]
    `(do ~@defs)))

(defmacro defprotocol
  {:doc "Defines a new protocol."
   :examples [["(defprotocol SayHi (hi [x]))"]
              ["(extend hi String (fn [name] (str \"Hi, \" name \"!\")))"]
              ["(hi \"Jane\")" nil "Hi, Jane!"]]
   :added "0.1"}
  [nm & sigs]
  `(pixie.stdlib.internal/-defprotocol (quote ~nm)
                                       ~(reduce (fn [r sig]
                                                  (conj r `(quote ~(first sig))))
                                                []
                                                sigs)))

(defmacro extend-type
  {:doc "Extends the protocols to the given type.

Expands to calls to `extend`."
   :examples [["(defprotocol SayHi (hi [x]))"]
              ["(extend-type String SayHi (hi [name] (str \"Hi, \" name \"!\")))"]
              ["(hi \"Jane\")" nil "Hi, Jane!"]]
   :added "0.1"}
  [tp & extensions]
  (let [[_ extends] (reduce (fn [[proto res] extend]
                              (cond
                               (symbol? extend) [extend res]
                               :else [proto (conj res `(extend ~(first extend) ~tp (fn ~@(next extend))))]))
                            []
                            extensions)]
    `(do
       ~@extends)))

(defmacro extend-protocol
  {:doc "Extend the protocol to the given types.

Expands to calls to `extend-type`."
   :examples [["(defprotocol SayHi (hi [x]))"]
              ["(extend-protocol SayHi

  String
  (hi [name]
    (str \"Hi, \" name \"!\"))

  Integer
  (hi [n]
    (str \"Hi, #\" n \"!\")))"]
              ["(hi \"Jane\")" nil "Hi, Jane!"]
              ["(hi 42)" nil "Hi, #42!"]]
   :added "0.1"}
  [protocol & extensions]
  ; tps is used to ensure protocols are extended in order
  (let [[_ tps exts] (reduce (fn [[tp tps res] extend-body]
                               (cond
                                (symbol? extend-body) [extend-body (conj tps extend-body) (assoc res extend-body [])]
                                :else [tp tps (update-in res [tp] conj extend-body)]))
                             [nil [] {}]
                             extensions)
        exts (reduce (fn [res tp]
                       (conj res `(extend-type ~tp ~protocol ~@(get exts tp))))
                     []
                     tps)]
    `(do ~@exts)))

(defprotocol IToFloat
  (-float [this]))

(defn float
  {:doc "Converts a number to a float."
   :since "0.1"}
  [x]
  (-float x))

(extend-type Number
  IToFloat
  (-float [x] (+ x 0.0)))

(defprotocol IToInteger
  (-int [x]))

(extend-protocol IToInteger
  Integer
  (-int [x] x)

  Float
  (-int [x] (floor x))

  Ratio
  (-int [x]
    (int (/ (float (numerator x)) (float (denominator x)))))

  Character
  (-int [x]
    (+ x 0)))

(defn int
  {:doc "Converts a number to an integer."
   :since "0.1"}
  [x]
  (-int x))

(defprotocol IRecord)

(defn record?
  {:doc "Returns true if x implements IRecord."
   :since "0.1"}
  [x]
  (satisfies? IRecord x))

(defmacro for
  {:doc "A list comprehension for the bindings."
   :examples [["(for [x [1 2 3]] x)" nil [1 2 3]]
              ["(for [x [1 2 3] y [:a :b :c]] [x y])" nil [[1 :a] [1 :b] [1 :c] [2 :a] [2 :b] [2 :c] [3 :a] [3 :b] [3 :c]]]]
   :added "0.1"}
  [bindings & body]
  (assert (and (pos? (count bindings)) (even? (count bindings))) "for requires an even number of bindings")
  (let [gen-loop (fn gen-loop [coll-bindings bindings]
                   (if (seq bindings)
                     (let [c (gensym "coll__")
                           binding (first bindings)
                           coll (second bindings)]
                       `(loop [res# []
                               ~c (seq ~coll)]
                          (if ~c
                            (let [~binding (first ~c)]
                              (recur (into res#
                                           ~(gen-loop (into coll-bindings
                                                            [binding `(first ~c)])
                                                      (nnext bindings)))
                                     (next ~c)))
                            res#)))
                     `[~@body]))]
    `(or (seq ~(gen-loop [] bindings)) '())))

(defmacro doto
  {:doc "Evaluate o, uses the value as the first argument in each form. Returns o."}
  [o & forms]
  (let [s (gensym o)]
    `(let [~s ~o]
       ~@(for [f forms]
           (if (seq? f)
             `(~(first f) ~s ~@(rest f))
             `(~f ~s)))
       ~s)))

(defn reverse
  ; TODO: We should probably have a protocol IReversible, so we can e.g.
  ;       reverse vectors efficiently, etc..
  [coll]
  "Returns a collection that contains all the elements of the argument in reverse order."
  (into () coll))

(defmacro use
  "Loads a namespace and refers all symbols from it."
  [ns]
  `(do
     (load-ns ~ns)
     (refer ~ns :refer :all)))

(defn count-rf
  "A Reducing function that counts the items reduced over."
  ([] 0)
  ([result] result)
  ([result _] (inc result)))

(defn dispose!
  "Finalizes use of the object by cleaning up resources used by the object."
  [x]
  (-dispose! x)
  nil)

(defmacro using
  "Evaluates body with the bindings available as with let,
  calling -dispose! on each name afterwards. Returns the value of the
  last expression in body."
  [bindings & body]
  (let [pairs (partition 2 bindings)
        names (map first pairs)]
    `(let [~@bindings
           result# (do ~@body)]
       ~@(map (fn [nm]
                `(-dispose! ~nm))
              names)
       result#)))

(defn pst
  {:doc "Prints the trace of a Runtime Exception if given, or the last Runtime Exception in *e."
   :signatures [[] [e]]
   :added "0.1"}
  ([] (pst *e))
  ([e] (when e (print (str e)))))

(defn trace
  {:doc "Returns a seq of the trace of a Runtime Exception or the last Runtime Exception in *e."
   :signatures [[] [e]]
   :added "0.1"}
  ([] (trace *e))
  ([e] (seq e)))

(defn tree-seq
  "Returns a lazy sequence of the nodes in a tree via a depth-first walk.
branch? - fn of node that should true when node has children
children - fn of node that should return a sequence of children (called if branch? true)
root - root node of the tree"
  [branch? children root]
  (let [walk (fn walk [node]
               (lazy-seq
                (cons node
                  (when (branch? node)
                    (mapcat walk (children node))))))]
    (walk root)))

(defn flatten
  ; TODO: laziness?
  {:doc "Takes any nested combination of ISeqable things, and return their contents as a single, flat sequence.

Calling this function on something that is not ISeqable returns a seq with that value as its only element."
   :examples [["(flatten [[1 2 [3 4] [5 6]] 7])" nil [1 2 3 4 5 6 7]]
              ["(flatten :this)" nil [:this]]]}
  [x]
  (if (not (satisfies? ISeqable x)) [x]
    (transduce (comp (map flatten) cat)
               conj []
               (seq x))))

(defn juxt
  {:doc "Returns a function that applies all fns to its arguments, and returns a vector of the results."
   :examples [["((juxt + - *) 2 3)" nil [5 -1 6]]]}
  [& fns]
  (fn [& args]
    (mapv #(apply % args) fns)))

(defn map-invert
  {:doc "Returns a map where the vals are mapped to the keys."
   :examples [["(map-invert {:a :b, :c :d})" nil {:b :a, :d :c}]]}
  [m]
  (reduce (fn [m* ent]
            (assoc m* (val ent) (key ent)))
          {} m))

(defn mapv
  {:doc "Returns a vector consisting of f applied to each element in col."
   :examples [["(mapv inc '(1 2 3))" nil [2 3 4]]]}
  ([f col]
   (transduce (map f) conj col)))

(defn macroexpand-1
  {:doc "If form is a macro call, returns the expanded form. Does nothing if not a macro call."
   :signatures [[form]]
   :examples [["(macroexpand-1 '(when condition this and-this))"
               nil (if condition (do this and-this))]
              ["(macroexpand-1 ())" nil ()]
              ["(macroexpand-1 [1 2])" nil [1 2]]]}
  [form]
  (if (or (not (list? form))
          (= () form))
    form
    (let [[sym & args] form
          fvar (resolve-in *ns* sym)]
      (if (and fvar (macro? @fvar))
        (apply @fvar args)
        form))))

(def *1)
(def *2)
(def *3)
(defn -push-history [x]
  (def *3 *2)
  (def *2 *1)
  (def *1 x))

(def *e)
(defn -set-*e [e]
  (def *e e))

(def hash-map hashmap)

(defn zipmap
  "Returns a map with the elements of a mapped to the corresponding
  elements of b."
  [a b]
  (into {} (map vector a b)))

(extend -str Environment
        (fn [v]
          (let [entry->str (map (fn [e] (vector (-repr (key e)) " " (-repr (val e)))))]
            (str "#Environment{" (transduce (comp entry->str (interpose [", "]) cat) string-builder v) "}"))))

(extend -repr Environment
        (fn [v]
          (let [entry->str (map (fn [e] (vector (-repr (key e)) " " (-repr (val e)))))]
            (str "#Environment{" (transduce (comp entry->str (interpose [", "]) cat) string-builder v) "}"))))

(defn interleave
  "Returns a seq of all the items in the input collections interleaved."
  ([] ())
  ([c1] (seq c1))
  ([c1 c2]
   (lazy-seq
    (let [s1 (seq c1)
          s2 (seq c2)]
      (when (and s1 s2)
        (cons (first s1) (cons (first s2)
                               (interleave (next s1) (next s2))))))))
  ([& colls]
   (lazy-seq
    (let [ss (map seq colls)]
      (when (every? identity ss)
        (concat (map first ss)
                (apply interleave (map next ss))))))))

(defn min
  "Returns the smallest of all the arguments to this function. Assumes arguments are numeric."
  ([x] x)
  ([x y] (if (< x y) x y))
  ([x y & zs] (apply min (min x y) zs)))

(defn max
  "Returns the largest of all the arguments to this function. Assumes arguments are numeric."
  ([x] x)
  ([x y] (if (> x y) x y))
  ([x y & zs] (apply max (max x y) zs)))

(defn take-nth
  "Returns a lazy seq of every nth item in coll.  Returns a stateful
  transducer when no collection is provided."
  ([n]
   (fn [rf]
     (let [ia (atom -1)]
       (fn
         ([] (rf))
         ([result] (rf result))
         ([result input]
          (let [i (swap! ia inc)]
            (if (zero? (rem i n))
              (rf result input)
              result)))))))
  ([n coll]
   (lazy-seq
    (when-let [s (seq coll)]
      (cons (first s) (take-nth n (drop n s)))))))

(defmacro loop
  [bindings & body]
  (let [vals (take-nth 2 (drop 1 bindings))
        bindings (take-nth 2 bindings)
        binding-syms (map (fn [b] (if (symbol? b) b (gensym))) bindings)
        binding-forms (transduce
                       (map (fn [bind]
                              (let [[b v s] bind]
                                (if (symbol? b)
                                  [b v]
                                  [s v b s]))))
                       concat
                       []
                       (map vector bindings vals binding-syms))]
    `(let ~(vec binding-forms)
       (loop* ~(vec (interleave binding-syms binding-syms))
              (let ~(vec (interleave bindings binding-syms))
                ~@body)))))

(extend -str Namespace
  (fn [v] (str "<Namespace " (name v) ">")))

(extend -repr Namespace -str)


(defn bool?
  "Returns true if x is a Bool."
  [x]
  (instance? Bool x))

(defmacro ->
  {:doc "Threads `x` through `forms`, passing the result of one step as the first argument of the next."
   :examples [["(-> 3 inc inc)" nil 5]
              ["(-> \"James\" (str \" is \" \"awesome \") (str \"(and stuff)\" \"!\"))" nil "James is awesome (and stuff)!"]]
   :signatures [[x & forms]]
   :added "0.1"}
  [x & forms]
  (loop [x x, forms forms]
    (if forms
      (let [form (first forms)
            threaded (if (seq? form)
                       (with-meta `(~(first form) ~x ~@(next form)) (meta form))
                       (list form x))]
        (recur threaded (next forms)))
      x)))

(defmacro ->>
  {:doc "Threads `x` through `forms`, passing the result of one step as the last argument of the next."
   :examples [["(->> \"James\" (str \"we \" \"like \") (str \"you \" \"know \" \"what? \"))" nil "you know what? we like James"]
              ["(->> 5 (range) (map inc) seq)" nil (1 2 3 4 5)]]
   :signatures [[x & forms]]
   :added "0.1"}
  [x & forms]
  (loop [x x, forms forms]
    (if forms
      (let [form (first forms)
            threaded (if (seq? form)
                       (with-meta `(~(first form) ~@(next form)  ~x) (meta form))
                       (list form x))]
        (recur threaded (next forms)))
      x)))

(defmacro some->
  {:doc "When expr is not nil, threads it into the first form (via ->),
    and when that result is not nil, through the next etc."
   :signatures [[expr & forms]]
   :added "0.1"}
  [expr & forms]
  (let [g (gensym)
        steps (map (fn [step] `(if (nil? ~g) nil (-> ~g ~step)))
                   forms)]
    `(let [~g ~expr
           ~@(interleave (repeat g) (butlast steps))]
       ~(if (empty? steps)
          g
          (last steps)))))

(defmacro some->>
  {:doc "When expr is not nil, threads it into the first form (via ->>),
  and when that result is not nil, through the next etc."
   :signatures [[x & forms]]
   :added "0,1"}
  [expr & forms]
  (let [g (gensym)
        steps (map (fn [step] `(if (nil? ~g) nil (->> ~g ~step)))
                   forms)]
    `(let [~g ~expr
           ~@(interleave (repeat g) (butlast steps))]
       ~(if (empty? steps)
          g
          (last steps)))))

(defmacro cond->
  {:added "0.1"
   :signatures [[expr & clauses]]
   :doc "Takes an expression and a set of test/form pairs. Threads expr (via ->)
  through each form for which the corresponding test
  expression is true. Note that, unlike cond branching, cond-> threading does
  not short circuit after the first true test expression."}
  [expr & clauses]
  (assert (even? (count clauses)))
  (let [g (gensym)
        steps (map (fn [[test step]] `(if ~test (-> ~g ~step) ~g))
                   (partition 2 clauses))]
    `(let [~g ~expr
           ~@(interleave (repeat g) (butlast steps))]
       ~(if (empty? steps)
          g
          (last steps)))))

(defmacro cond->>
  {:doc "Takes an expression and a set of test/form pairs. Threads expr (via ->>)
  through each form for which the corresponding test expression
  is true.  Note that, unlike cond branching, cond->> threading does not short circuit
  after the first true test expression."
   :signatures [[expr & clauses]]
   :added "0.1"}
  [expr & clauses]
  (assert (even? (count clauses)))
  (let [g (gensym)
        steps (map (fn [[test step]] `(if ~test (->> ~g ~step) ~g))
                   (partition 2 clauses))]
    `(let [~g ~expr
           ~@(interleave (repeat g) (butlast steps))]
       ~(if (empty? steps)
          g
          (last steps)))))

(defmacro as->
  {:doc "Binds name to expr, evaluates the first form in the lexical context
  of that binding, then binds name to that result, repeating for each
  successive form, returning the result of the last form."
   :signatures [[expr name & forms]]
   :added "0,1"}
  [expr name & forms]
  `(let [~name ~expr
         ~@(interleave (repeat name) (butlast forms))]
     ~(if (empty? forms)
        name
        (last forms))))

(defprotocol IComparable
  (-compare [x y]
    "Compares two objects. Returns 0 when x is equal to y, -1 when x
    is logically smaller than y, and 1 when x is logically larger."))

(defn compare-numbers
  [x y]
  (cond
    (> x y) 1
    (< x y) -1
    :else 0))

(defn compare-counted
  [x y]
  (if (= x y)
    0
    (let [min-length (min (count x) (count y))]
      (loop [n 0]
        (if (not= min-length n)
          (let [diff (-compare (nth x n)
                               (nth y n))]
            (if-not (zero? diff)
              diff
              (recur (inc n))))
          ;; We have compared all characters of the smallest string
          ;; against the largest string.
          ;; If equal lengths 0 otherwise -1 or 1
          (compare-numbers (count x) (count y)))))))

(defn compare-named
  [x y]
  (if (= x y)
    0
    (compare-counted (str x) (str y))))

(extend-protocol ISeq
  ISeqable
  (-first [coll] (-first (seq coll)))
  (-next  [coll] (-next  (seq coll))))

(extend-protocol IComparable
  Number
  (-compare [x y]
    (if (number? y)
      (compare-numbers x y)
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)])))

  Character
  (-compare [x y]
    (if (char? y)
      (compare-numbers (int x) (int y))
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)])))

  PersistentVector
  (-compare [x y]
    (if (vector? y)
      (compare-counted x y)
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)])))

  String
  (-compare [x y]
    (if (string? y)
      (compare-counted (str x) (str y))
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)])))

  Keyword
  (-compare [x y]
    (if (keyword? y)
      (compare-counted (str x) (str y))
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)])))

  Symbol
  (-compare [x y]
    (if (symbol?  y)
      (compare-counted (str x) (str y))
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)])))

  Bool
  (-compare [x y]
    (if (bool? y)
      (cond
        (= x y) 0
        (and (true? x) (false? y)) 1
        :else  -1))
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)]))

  Nil
  (-compare [x y]
    (if (nil? y)
      0
      (throw [::ComparisonError (str "Cannot compare: " x " to " y)]))))

(defn compare
  "Compares two objects. Returns 0 when x is equal to y, -1 when x is
  logically smaller than y, and 1 when x is logically larger. x must
  implement IComparable."
  [x y]
  (if (satisfies? IComparable x)
    (-compare x y)
    (throw [::ComparisonError (str x " does not satisfy IComparable")])))

(defn vary-meta
  {:doc "Returns x with meta data updated with the application of f and args to it.
ex: (vary-meta x assoc :foo 42)"
   :signatures [[x f & args]]
   :added "0.1"}
  [x f & args]
  (with-meta x (apply f (meta x) args)))

(defn memoize
  {:doc "Returns a memoized version of function f. The first call will
   realize the return value and subsequent calls get the same value
   from its cache."
   :signatures [[f]]
   :added "0.1"}
  [f]
  (let [cache (atom {})]
    (fn [& args]
      (let [argsv (vec args)
            val (get @cache argsv ::not-found)]
        (if (= val ::not-found)
          (let [ret (apply f args)]
            (swap! cache assoc argsv ret)
            ret)
          val)))))

(deftype Iterate [f x]
  IReduce
  (-reduce [self rf init]
    (loop [next (f x)
           acc (rf init x)]
      (if (reduced? acc)
        @acc
        (recur (f next) (rf acc next)))))
  ISeq
  (-seq [self]
    (cons x (lazy-seq* (fn [] (->Iterate f (f x)))))))

(defn iterate
  {:doc "Returns a lazy sequence of x, (f x), (f (f x)) etc. f must be free of
    side-effects"
   :signatures [[f x]]
   :added "0.1"}
  [f x]
  (->Iterate f x))
