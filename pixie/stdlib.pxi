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

(def libm (ffi-library (str "libm." pixie.platform/so-ext)))
(def atan2 (ffi-fn libm "atan2" [CDouble CDouble] CDouble))
(def floor (ffi-fn libm "floor" [CDouble] CDouble))
(def lround (ffi-fn libm "lround" [CDouble] CInt))


(def reset! -reset!)

(def program-arguments [])

(def fn (fn* [& args]
             (cons 'fn* args)))
(set-macro! fn)

(def let (fn* [& args]
              (cons 'let* args)))
(set-macro! let)

(def identity
  (fn ^{:doc "The identity function. Returns its argument."
        :added "0.1"}
    identity
    [x]
    x))

(def conj
  (fn ^{:doc "Adds elements to the collection. Elements are added to the end except in the case of Cons lists"
        :signatures [[] [coll] [coll item] [coll item & args]]
        :added "0.1"}
    conj
    ([] [])
    ([coll] coll)
    ([coll item] (-conj coll item))
    ([coll item & args]
       (reduce -conj (-conj coll item) args))))

(def conj!
  (fn ^{:doc "Adds elements to the transient collection. Elements are added to the end except in the case of Cons lists"
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
  (fn ^{:doc "Push an element on to a stack."
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
  (fn ^{:doc "Push an element on to a transient stack."
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

(def map (fn ^{:doc "map - creates a transducer that applies f to every input element"
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

(def reduce (fn [rf init col]
              (-reduce col rf init)))

(def into (fn ^{:doc "Add the elements of `from` to the collection `to`."
                :signatures [[to from]]
                :added "0.1"}
            into
            [to from]
            (if (satisfies? IToTransient to)
              (persistent! (reduce conj! (transient to) from))
              (reduce conj to from))))

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
  (fn ^{:doc "Maps f over the elements of coll and concatenates the result"
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
(extend -at-end? Nil (fn [_] true))
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


(extend -str PersistentVector
  (fn [v]
    (apply str "[" (conj (transduce (interpose " ") conj v) "]"))))
(extend -repr PersistentVector
  (fn [v]
    (apply str "[" (conj (transduce (comp (map -repr) (interpose " ")) conj v) "]"))))

(extend -str Cons
  (fn [v]
    (apply str "(" (conj (transduce (interpose " ") conj v) ")"))))
(extend -repr Cons
  (fn [v]
    (apply str "(" (conj (transduce (comp (map -repr) (interpose " ")) conj v) ")"))))

(extend -hash Cons
        (fn [v]
          (transduce ordered-hash-reducing-fn v)))

(extend -str PersistentList
  (fn [v]
    (apply str "(" (conj (transduce (interpose " ") conj v) ")"))))
(extend -repr PersistentList
  (fn [v]
    (apply str "(" (conj (transduce (comp (map -repr) (interpose " ")) conj v) ")"))))

(extend -hash PersistentList
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))


(extend -str LazySeq
  (fn [v]
    (apply str "(" (conj (transduce (interpose " ") conj v) ")"))))
(extend -repr LazySeq
  (fn [v]
    (apply str "(" (conj (transduce (comp (map -repr) (interpose " ")) conj v) ")"))))

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

(def stacklet->lazy-seq
  (fn [k]
    (if (-at-end? k)
      nil
      (cons (-current k)
            (lazy-seq* (fn [] (stacklet->lazy-seq (-move-next! k))))))))

(def = -eq)

(extend -seq PersistentVector
  (fn vector-seq
   ([self]
    (vector-seq self 0))
   ([self x]
    (if (= x (count self))
      nil
      (cons (nth self x) (lazy-seq* (fn [] (vector-seq self (+ x 1)))))))))



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
  {:doc "Define a new non-public function. Otherwise the same as defn"
   :signatures [[nm doc? meta? & body]]
   :added "0.1"}
  [nm & rest]
  (let [nm (with-meta nm (assoc (meta nm) :private true))]
    (cons `defn (cons nm rest))))

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

(defn not
  {:doc "Inverts the input, if a truthy value is supplied, returns false, otherwise
returns true"
   :signatures [[x]]
   :added "0.1"}
  [x]
  (if x false true))

(defn +
  {:doc "Adds the arguments, returning 0 if no arguments"
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

(defn /
  ([x] (-div 1 x))
  ([x y] (-div x y))
  ([x y & args]
      (reduce -div (-div x y) args)))

(defn quot [num div]
  (-quot num div))

(defn rem [num div]
  (-rem num div))

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
  {:doc "Returns true if x is greater than zero"
   :signatures [[x]]
   :added "0.1"}
  [x]
  (> x 0))

(defn neg?
  {:doc "Returns true if x is less than zero"
   :signatures [[x]]
   :added "0.1"}
  [x]
  (< x 0))

(defn zero?
  {:doc "Returns true if x is equal to zero"
   :signatures [[x]]
   :added "0.1"}
  [x]
  (= x 0))

(defn inc
  {:doc "Increments x by one"
   :signatures [[x]]
   :added "0.1"}
  [x]
  (+ x 1))

(defn dec
  {:doc "Decrements x by one"
   :signatures [[x]]
   :added "0.1"}
  [x]
  (- x 1))

(defn empty?
  {:doc "returns true if the collection has no items, otherwise false"
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (not (seq coll)))

(defn not-empty?
  {:doc "returns true if the collection has items, otherwise false"
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (seq coll) true false))

(defn even?
  {:doc "Returns true if n is even"
   :signatures [[n]]
   :added "0.1"}
  [n]
  (zero? (rem n 2)))

(defn odd?
  {:doc "Returns true of n is odd"
   :signatures [[n]]
   :added "0.1"}
  [n]
  (= (rem n 2) 1))

(defn nth
  {:doc "Returns the element at the idx.  If the index is not found it will return an error.
         However, if you specify a not-found parameter, it will substitute that instead"
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
  {:doc "Associates the key with the value in the collection"
   :signatures [[m] [m k v] [m k v & kvs]]
   :added "0.1"}
  ([m] m)
  ([m k v]
     (-assoc m k v))
  ([m k v & rest]
     (apply assoc (-assoc m k v) rest)))

(defn dissoc
  {:doc "Removes the value associated with the keys from the collection"
   :signatures [[m] [m & ks]]
   :addded "0.1"}
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
  {:doc "Creates a hash-set from the arguments of the function"
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
  {:doc "Checks if any of the tests is truthy, if so, stops and returns the value of the corresponding body"
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
                               (throw "Can only have one catch clause per try")
                               (recur (next (next form)) (first (next form)) body-items finally (next body)))
             (= head 'finally) (if finally
                                 (throw "Can only have one finally clause per try")
                                 (recur catch catch-sym body-items (next form) (next body)))
             :else (recur catch catch-sym (conj body-items form) finally (next body)))))
        `(-try-catch
          (fn [] ~@body-items)
          ~(if catch
             `(fn [~catch-sym] ~@catch)
             `(fn [] nil))

          (fn [] ~@finally))))))

(defn .
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

(defn list? [v] (instance? PersistentList v))
(defn set? [v] (instance? PersistentHashSet v))
(defn map? [v] (satisfies? IMap v))
(defn fn? [v] (satisfies? IFn v))

(defn indexed? [v] (satisfies? IIndexed v))
(defn counted? [v] (satisfies? ICounted v))

(defn float
  {:doc "Converts a number to a float."
   :since "0.1"}
  [x]
  (cond
   (number? x) (+ x 0.0)
   :else (throw (str "Can't convert a value of type " (type x) " to a Float"))))

(defn int
  {:doc "Converts a number to an integer."
   :since "0.1"}
  [x]
  (cond
   (integer? x) x
   (float? x) (lround (floor x))
   (ratio? x) (int (/ (float (numerator x)) (float (denominator x))))
   (char? x) (+ x 0)
   :else (throw (str "Can't convert a value of type " (type x) " to an Integer"))))

(defn last
  {:doc "Returns the last element of the collection, or nil if none."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (next coll)
    (recur (next coll))
    (first coll)))

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
  {:doc "Given a function, return a new function which takes the same arguments
         but returns the opposite truth value"}
  [f]
  (if (not (fn? f))
    (throw "Complement must be passed a function")
    (fn
      ([] (not (f)))
      ([x] (not (f x)))
      ([x y] (not (f x y)))
      ([x y & more] (not (apply f x y more))))))

(defn constantly [x]
  {:doc "Return a function that always returns x, no matter what it is called with."
   :examples [["(let [f (constantly :me)] [(f 1) (f \"foo\") (f :abc) (f nil)])"
               nil [:me :me :me :me]]]}
  (fn [& _] x))

(defn some
  {:doc "Checks if the predicate is true for any element of the collection.

Stops if it finds such an element."
   :signatures [[pred coll]]
   :added "0.1"}
  [pred coll]
  (cond
   (nil? (seq coll)) false
   (pred (first coll)) true
   :else (recur pred (next coll))))

(extend -count MapEntry (fn [self] 2))
(extend -nth MapEntry (fn map-entry-nth [self idx]
                          (cond (= idx 0) (-key self)
                                (= idx 1) (-val self))))
(extend -nth-not-found MapEntry (fn map-entry-nth [self idx not-found]
                                  (cond (= idx 0) (-key self)
                                        (= idx 1) (-val self)
                                        :else not-found)))

(extend -reduce MapEntry indexed-reduce)

(extend -str MapEntry
  (fn [v]
    (apply str "[" (conj (transduce (interpose " ") conj v) "]"))))
(extend -repr MapEntry
  (fn [v]
    (apply str "[" (conj (transduce (comp (map -repr) (interpose " ")) conj v) "]"))))

(extend -hash MapEntry
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))

(defn keys
  {:doc "If called with no arguments returns a transducer that will extract the key from each map entry. If passed
   a collection, will assume that it is a hashmap and return a vector of all keys from the collection."
   :signatures [[] [coll]]
   :added "0.1"}
  ([] (map key))
  ([m]
     (transduce (map key) conj! m)))

(defn vals
  {:doc "If called with no arguments returns a transducer that will extract the key from each map entry. If passed
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
            (apply str "{" (conj (transduce (comp entry->str (interpose [", "]) cat) conj v) "}")))))
(extend -repr PersistentHashMap
        (fn [v]
          (let [entry->str (map (fn [e] (vector (-repr (key e)) " " (-repr (val e)))))]
            (apply str "{" (conj (transduce (comp entry->str (interpose [", "]) cat) conj v) "}")))))

(extend -hash PersistentHashMap
        (fn [v]
          (transduce cat unordered-hash-reducing-fn v)))

(extend -seq PersistentHashSet (fn [self] (seq (iterator self))))

(extend -str PersistentHashSet
        (fn [s]
          (apply str "#{" (conj (transduce (interpose " ") conj s) "}"))))
(extend -repr PersistentHashSet
        (fn [s]
          (apply str "#{" (conj (transduce (comp (map -repr) (interpose " ")) conj s) "}"))))

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
                 (throw "Vector arg to map conj must be a pair"))

             (satisfies? ISeqable x)
             (reduce conj coll (-seq x))

             :else
             (throw (str (type x) " cannot be conjed to a map")))))

(extend -conj Cons
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

(extend -invoke Keyword (fn [k m] (-val-at m k nil)))
(extend -invoke PersistentHashMap (fn [m k] (-val-at m k nil)))
(extend -invoke PersistentHashSet (fn [m k] (-val-at m k nil)))

(defn get
  {:doc "Get an element from a collection implementing ILookup, return nil or the default value if not found."
   :added "0.1"}
  ([mp k]
     (get mp k nil))
  ([mp k not-found]
     (-val-at mp k not-found)))

(defn get-in
  {:doc "Get a value from a nested collection at the \"path\" given by the keys."
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
  {:doc "Associate a value in a nested collection given by the path.

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
  {:doc "Update a value in a nested collection."
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
        (throw "Assert failed")))
  ([test msg]
     `(if ~test
        nil
        (throw (str "Assert failed " ~msg)))))

(defmacro resolve
  {:doc "Resolve the var associated with the symbol in the current namespace."
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
  `(do (in-ns ~(keyword (name nm)))
       ~@body))


(defn symbol? [x]
  (identical? Symbol (type x)))


(defmacro lazy-seq [& body]
  `(lazy-seq* (fn [] ~@body)))

(def Protocol @(resolve (symbol "/Protocol")))

(defn protocol? [x]
  (instance? Protocol x))

(defmacro deftype
  {:doc "Define a custom type."
   :examples [["(deftype Person [name]
  Object
  (say-hi [self other-name]
    (str \"Hi, I'm \" name \". You're \" other-name \", right?\"))

  IObject
  (-str [self]
    (str \"<Person \" (pr-str name) \">\")))"]
              ["(.say-hi (->Person \"James\") \"Paul\")" nil "Hi, I'm James. You're Paul, right?"]
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
                                   :else (throw (str "can only extend protocols or Object, not " body " of type " (type body))))
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

(defmacro defrecord
  {:doc "Define a record type.

Similar to `deftype`, but supports construction from a map using `map->Type`
and implements IAssociative, ILookup and IObject."
   :added "0.1"}
  [nm fields & body]
  (let [ctor-name (symbol (str "->" (name nm)))
        map-ctor-name (symbol (str "map" (name ctor-name)))
        fields (transduce (map (comp keyword name)) conj fields)
        type-from-map `(defn ~map-ctor-name [m]
                         (apply ~ctor-name (map #(get m %) ~fields)))
        default-bodies ['IAssociative
                        `(-assoc [self k v]
                                 (let [m (reduce #(assoc %1 %2 (. self %2)) {} ~fields)]
                                   (~map-ctor-name (assoc m k v))))
                        `(-contains-key [self k]
                                        (contains? ~(set fields) k))
                        `(-dissoc [self k]
                                  (throw "dissoc is not supported on defrecords"))
                        'ILookup
                        `(-val-at [self k not-found]
                                  (if (contains? ~(set fields) k)
                                    (. self k)
                                    not-found))
                        'IObject
                        `(-str [self]
                               (str "<" ~(name nm) " " (reduce #(assoc %1 %2 (. self %2)) {} ~fields) ">"))
                        `(-eq [self other]
                              (and (instance? ~nm other)
                                   ~@(map (fn [field]
                                            `(= (. self ~field) (. other ~field)))
                                          fields)))
                        `(-hash [self]
                                (throw "not implemented"))]
        deftype-decl `(deftype ~nm ~fields ~@default-bodies ~@body)]
    `(do ~type-from-map
         ~deftype-decl)))

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

(defn repeat
  ([x]
     (cons x (lazy-seq* (fn [] (repeat x)))))
  ([n x]
     (take n (repeat x))))

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

  (let [vr (resolve v)
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

(defmacro iterate [binding & body]
  (assert (= 2 (count binding)) "binding and collection required")
  `(let [i# (iterator ~(second binding))]
     (loop []
       (if (at-end? i#)
         nil
         (let [~(first binding) (current i#)]
           ~@body
           (move-next! i#)
           (recur))))))


(defmacro dotimes
  {:doc "Execute the expressions in the body n times."
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

(extend -iterator PersistentVector
        (fn [v]
          (dotimes [x (count v)]
            (yield (nth v x nil)))))

(extend -iterator Array
        (fn [v]
          (dotimes [x (count v)]
            (yield (nth v x nil)))))

(extend -iterator String
        (fn [v]
          (dotimes [x (count v)]
            (yield (nth v x nil)))))

(defmacro and
  {:doc "Check if the given expressions return truthy values, returning the last, or false."
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

(defn nnext
  {:doc "Equivalent to (next (next coll))"
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
         However, if you specify a not-found parameter, it will substitute that instead"
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

(defn take
  {:doc "Takes n elements from the collection, or fewer, if not enough."
   :added "0.1"}
  [n coll]
  (when (pos? n)
    (when-let [s (seq coll)]
      (cons (first s) (take (dec n) (next s))))))

(defn drop
  {:doc "Drops n elements from the start of the collection."
   :added "0.1"}
  [n coll]
  (let [s (seq coll)]
    (if (and (pos? n) s)
      (recur (dec n) (next s))
      s)))

(defmacro while
  {:doc "Repeatedly executes body while test expression is true. Presumes
  some side-effect will cause test to become false/nil. Returns nil"
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

;; TODO: use a transient map in the future
(defn group-by [f coll]
  {:doc "Groups the collection into a map keyed by the result of applying f on each element. The value at each key is a vector of elements in order of appearance."
   :examples [["(group-by even? [1 2 3 4 5])" nil {false [1 3 5] true [2 4]}]
              ["(group-by (partial apply +) [[1 2 3][2 4][1 2]]" nil {6 [[1 2 3] [2 4]] 3 [[1 2]]}]]
   :signatures [[f coll]]
   :added "0.1"}
  (reduce (fn [res elem]
            (update-in res [(f elem)] (fnil conj []) elem))
          {}
          coll))

;; TODO: use a transient map in the future
(defn frequencies [coll]
  {:doc "Returns a map with distinct elements as keys and the number of occurences as values"
   :added "0.1"}
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
       (cons (take n s) (partition n step (drop step s))))))

(defn destructure [binding expr]
  (cond
   (symbol? binding) [binding expr]
   (vector? binding) (let [name (gensym "vec__")]
                       (reduce conj [name expr]
                               (destructure-vector binding name)))
   (map? binding) (let [name (gensym "map__")]
                    (reduce conj [name expr]
                            (destructure-map binding name)))
   :else (throw (str "unsupported binding form: " binding))))

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
                      (throw "Index out of Range"))
                    (if (and (pos? n) s)
                      (recur (next s) (dec n))
                      (if (zero? n)
                        (first s)
                        (throw "Index out of Range")))))
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
  IIterable
  (-iterator [self]
    (loop [i start]
      (when (or (and (> step 0) (< i stop))
                (and (< step 0) (> i stop))
                (and (= step 0)))
        (yield i)
        (recur (+ i step)))))
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
      (throw "Index out of Range"))
    (let [cmp (if (< start stop) < >)
          val (+ start (* idx step))]
      (if (cmp val stop)
        val
        (throw "Index out of Range"))))
  (-nth-not-found [self idx not-found]
    (let [cmp (if (< start stop) < >)
          val (+ start (* idx step))]
      (if (cmp val stop)
        val
       not-found)))
  ISeqable
  (-seq [self]
    (when (or (and (> step 0) (< start stop))
              (and (< step 0) (> start stop)))
      (cons start (lazy-seq* #(range (+ start step) stop step))))))

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

(defn iterator
  {:doc "Returns an iterator for the collection."
   :added "0.1"}
  [coll]
  (-iterator coll))

(defn move-next! [i]
  (-move-next! i)
  i)

(defn at-end? [i]
  (-at-end? i))

(defn current [i]
  (-current i))

(defn iterator-seq [i]
  (if (at-end? i)
    nil
    (cons (current i) (lazy-seq (iterator-seq (move-next! i))))))

(extend -first IIterator -current)
(extend -iterator IIterator identity)

(extend -seq IIterator iterator-seq)
(extend -seq IIterable (comp seq iterator))

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

(extend -reduce ShallowContinuation
        (fn [k f init]
          (loop [acc init]
            (if (reduced? init)
              @init
              (if (-at-end? k)
                acc
                (let [acc (f acc (-current k))]
                  (-move-next! k)
                  (recur acc)))))))

(defn filter
  {:doc "Filter the collection for elements matching the predicate."
   :signatures [[pred] [pred coll]]
   :added "0.1"}
  ([f] (fn [xf]
         (fn
           ([] (xf))
           ([acc] (xf acc))
           ([acc i] (if (f i)
                      (xf acc i)
                      acc)))))
  ([f coll]
    (let [iter (iterator coll)]
      (loop []
        (when (not (at-end? iter))
          (if (f (current iter))
            (yield (current iter)))
          (move-next! iter)
          (recur))))))

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
    (let [iter (iterator coll)]
      (loop [acc #{}]
        (when (not (at-end? iter))
          (if (contains? acc (current iter))
            (do (move-next! iter)
                (recur acc))
            (let [val (current iter)]
              (yield val)
              (move-next! iter)
              (recur (conj acc val)))))))))


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
     (iterate [x coll]
              (let [result (f x)]
                (if result
                  (yield result))))))

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
  (let [ns (or (the-ns ns-sym) (throw (str "No such namespace: " ns-sym)))
        filters (apply hashmap filters)
        nsmap (ns-map ns)
        rename (or (:rename filters) {})
        exclude (set (:exclude filters))
        refers (if (= :all (:refer filters))
                 (keys nsmap)
                 (or (:refer filters) (:only filters)))]
    (when (and refers (not (satisfies? ISeqable refers)))
      (throw ":only/:refer must be a collection of symbols"))
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
                  (throw (str sym "does not exist")))
                (refer-symbol *ns* (or (rename sym) sym) v))))
          (recur (next syms)))))
    nil))



(defmacro require [ns & args]
  `(do (load-ns (quote ~ns))
       (assert (the-ns (quote ~ns))
               (str "Couldn't find the namespace " (quote ~ns) " after loading the file"))

       (apply refer (quote [~ns ~@args]))))



(extend -iterator ISeq (fn [s]
                         (loop [s s]
                           (when s
                             (yield (first s))
                             (recur (next s))))))
(extend -at-end? EmptyList (fn [_] true))

(defn merge-with
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
  {:doc "Check if every element of the collection satisfies the predicate."
   :added "0.1"}
  [pred coll]
  (cond
   (nil? (seq coll)) true
   (pred (first coll)) (recur pred (next coll))
   :else false))

(defmacro fn
  {:doc "Creates a function.

The following two forms are allowed:
  (fn name? [param*] & body)
  (fn name? ([param*] & body)+)

The params can be destructuring bindings, see `(doc let)` for details."}
  [& decls]
  (let [name (if (symbol? (first decls)) (first decls) nil)
        decls (if name (next decls) decls)
        name (or name '-fn)
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
                                body (next decl)]
                            (if (every? symbol? argv)
                              `(~argv ~@body)
                              `(~names
                                (let ~bindings
                                  ~@body)))))
                        decls))]
    (if (= (count decls) 1)
      `(fn* ~name ~(first (first decls)) ~@(next (first decls)))
      `(fn* ~name ~@decls))))

(deftype MultiMethod [dispatch-fn default-val methods]
  IFn
  (-invoke [self & args]
    (let [dispatch-val (apply dispatch-fn args)
          method (if (contains? @methods dispatch-val)
                   (get @methods dispatch-val)
                   (get @methods default-val))
          _ (assert method (str "no method defined for " dispatch-val))]
      (apply method args))))

(defmacro defmulti
  {:doc "Define a multimethod, which dispatches to its methods based on dispatch-fn."
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
  {:doc "Define a method of a multimethod. See `(doc defmulti)` for details."
   :signatures [[name dispatch-val [param*] & body]]
   :added "0.1"}
  [name dispatch-val params & body]
  `(do
     (let [methods (.methods ~name)]
       (swap! methods
              assoc
              ~dispatch-val (fn ~params
                              ~@body))
       ~name)))

(defmacro declare
  {:doc "Forward declare the given variable names, setting them to nil."
   :added "0.1"}
  [& nms]
  (let [defs (map (fn [nm] `(def ~nm)) (seq nms))]
    `(do ~@defs)))

(defmacro defprotocol
  {:doc "Define a new protocol."
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
  {:doc "Extend the protocols to the given type.

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
                            (recur (into res#
                                         ~(gen-loop (into coll-bindings
                                                          [binding `(first ~c)])
                                                    (nnext bindings)))
                                   (next ~c))
                            res#)))
                     `(let ~coll-bindings
                        [~@body])))]
    `(or (seq ~(gen-loop [] bindings)) '())))

(defmacro use
  [ns]
  `(do
     (load-ns ~ns)
     (refer ~ns :refer :all)))

(defn count-rf
  "A Reducing function that counts the items reduced over"
  ([] 0)
  ([result] result)
  ([result _] (inc result)))

(defn string-builder
  "Creates a reducing function that builds a string based on calling str on the transduced collection"
  ([] (-string-builder))
  ([sb] (str sb))
  ([sb item] (conj! sb item)))

(defn dispose!
  "Finalizes use of the object by cleaning up resources used by the object"
  [x]
  (-dispose! x)
  nil)

(defmacro using [bindings & body]
  (let [pairs (partition 2 bindings)
        names (map first pairs)]
    `(let [~@bindings
           result# (do ~@body)]
       ~@(map (fn [nm]
                `(-dispose! ~nm))
              names)
       result#)))

(defn pst
  {:doc "Prints the trace of a Runtime Exception if given, or the last Runtime Exception in *e"
   :signatures [[] [e]]
   :added "0.1"}
  ([] (pst *e))
  ([e] (when e (print (str e)))))

(defn trace
  {:doc "Returns a seq of the trace of a Runtime Exception or the last Runtime Exception in *e"
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

(defn mapv
  ([f col]
   (transduce (map f) conj col)))

(defn -push-history [x]
  (def *3 *2)
  (def *2 *1)
  (def *1 x))

(defn -set-*e [e]
  (def *e e))
