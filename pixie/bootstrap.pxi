;; This file is used to build what we need to even start running stdlib.pxi
;; Ordering of stuff will probably matter here

(defprotocol ISeq
  (-first [this])
  (-next [this]))

(defprotocol ISeqable
  (-seq [this]))

(defprotocol ICounted
  (-count [this]))

(defprotocol IIndexed
  (-nth [this idx])
  (-nth-not-found [this idx not-found]))


(defprotocol IPersistentCollection
  (-conj [this x])
  (-disj [this x]))

(defprotocol IEmpty
  (-empty [this]))

(defprotocol IObject
  (-hash [this])
  (-eq [this other])
  (-str [this sbf])
  (-repr [this sbf]))

(defprotocol IReduce
  (-reduce [this f init]))

(defprotocol IDeref
  (-deref [this]))

(defprotocol IReset
  (-reset! [this val]))

(defprotocol INamed
  (-namespace [this])
  (-name [this]))

(defprotocol IAssociative
  (-assoc [this k v])
  (-contains-key [this k])
  (-dissoc [this k]))

(defprotocol ILookup
  (-val-at [this]))

(defprotocol IMapEntry
  (-key [this])
  (-val [this]))

(defprotocol IStack
  (-push [this v]))

(defprotocol IPop
  (-pop [this]))

(defprotocol IFn
  (-invoke [this args]))

(defprotocol IDoc
  (-doc [this]))

(defprotocol IVector)
(defprotocol ISequential)
(defprotocol IMap)

(defprotocol IMeta
  (-with-meta [this x])
  (-meta [this]))

(defprotocol ITransientCollection
  (-conj! [this x]))

(defprotocol IToTransient
  (-transient [this x]))

(defprotocol ITransient
  (-persistent! [this]))

(defprotocol ITransientStack
  (-push! [this x])
  (-pop! [this]))

(defprotocol IDisposable
  (-dispose! [this]))

(defprotocol IMessageObject
  (-get-field [this name])
  (-invoke-method [this name args]))


(defprotocol IEffect
  (-effect-val [this v])
  (-effect-finally [this v]))

(defeffect EException
  (-throw [this kw data ks]))

(deftype ExceptionHandler [catches finally-fn]
  IEffect
  (-effect-val [this v]
    v)
  
  (-effect-finally [this v]
    (when finally-fn
      (finally-fn))
    v)

  EException
  (-throw [this kw data ks k]
    (let [c (or (get catches kw)
                (get catches :*))]
      (println "Got Exception" kw c)
      (if c
        (c {:ex kw :data data :ks (conj ks k)})
        (-throw nil kw data (cons k ks))))))

(defn throw
  ([[kw val]]
   (throw kw val))
  ([kw val]
    (-throw nil
            kw
            val
            [])))

(defn -try [body catches finally]
  (with-handler [ex (->ExceptionHandler catches finally)]
    (body)))

(-run-external-extends)

(extend -get-field Object -internal-get-field)
(extend -hash Object -internal-identity-hash)
(extend -meta Object (fn [x] nil))

(extend-type Object
  (-str [x sb]
    (sb (-internal-to-str x)))
  
  (-repr  [x sb]
    (sb (-internal-to-repr x)))

  (-eq [this other]
    false))

(extend-type String
  IObject
  (-str [this sb]
    (sb this)))

;; Math wrappers

(extend -eq Number -num-eq)

(defn +
  {:doc "Adds the arguments, returning 0 if no arguments"
   :signatures [[& args]]
   :added "0.1"}  
  ([] 0)
  ([x] x)
  ([x y] (-add x y))
  ([x y & more]
   (-apply + (+ x y) more)))

(defn -
  ([] 0)
  ([x] x)
  ([x y] (-sub x y))
  ([x y & more]
   (-apply - (- x y) more)))

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

(defn inc
  ([x] (+ x 1)))

(defn dec
  ([x] (- x 1)))

(defn <
  ([x y] (-lt x y))
  ([x y & more]
   (-apply < (< x y) more)))

(defn >
  ([x y] (-gt x y))
  ([x y & more]
   (-apply > (> x y) more)))


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


(defn =
  {:doc "Returns true if all the arguments are equivalent. Otherwise, returns false. Uses
-eq to perform equality checks."
   :signatures [[& args]]
   :added "0.1"}
  ([x] true)
  ([x y] (if (identical? x y)
           true
           (-eq x y)))
  ([x y & rest] (if (eq x y)
                  (apply = y rest)
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


;; Base functions

(defn hash
  [this]
  (-hash this))

(defn identity
  ^{:doc "The identity function. Returns its argument."
        :added "0.1"}
  ([x & _] x))

(defn not
  [x]
  (if x false true))

(defn not=
  ([& args]
   (not (-apply = args))))

(defn nil?
  [x]
  (identical? x nil))

(defn deref
  [x]
  (-deref x))

(defn conj
  {:doc "Adds elements to the transient collection. Elements are added to the end except in the case of Cons lists"
   :signatures [[] [coll] [coll item] [coll item & args]]
   :added "0.1"}
  ([] [])
  ([coll] coll)
  ([coll itm] (-conj coll itm))
  ([coll item & more]
   (-apply conj (conj x y) more)))


(defn conj!
  {:doc "Adds elements to the transient collection. Elements are added to the end except in the case of Cons lists"
   :signatures [[] [coll] [coll item] [coll item & args]]
   :added "0.1"}
  ([] (-transient pixie.stdlib.persistent-vector/EMPTY))
  ([coll] (-persistent! coll))
  ([coll item] (-conj! coll item))
  ([coll item & args]
   (reduce -conj! (-conj! coll item) args)))

(defn disj
  {:doc "Removes elements from the collection."
   :signatures [[] [coll] [coll item]]
   :added "0.1"}
  ([] [])
  ([coll] coll)
  ([coll item] (-disj coll item))
  ([coll item & items]
   (reduce -disj (-disj coll item) items)))

(defn pop
  {:doc "Pops elements off a stack."
   :signatures [[] [coll] [coll item] [coll item & args]]
   :added "0.1"}
  ([] [])
  ([coll] (-pop coll)))

(defn push
  {:doc "Push an element on to a stack."
   :signatures [[] [coll] [coll item] [coll item & args]]
   :added "0.1"}
  ([coll x] (-push coll x)))

(defn pop!
  {:doc "Pops elements off a transient stack."
   :signatures [[] [coll] [coll item] [coll item & args]]
   :added "0.1"}
  ([coll] (-pop! coll)))

(defn push!
  {:doc "Push an element on to a transient stack."
   :signatures [[] [coll] [coll item] [coll item & args]]
   :added "0.1"}
  ([coll x] (-push! coll x)))


(defn nth
  {:doc "Returns the element at the idx.  If the index is not found it will return an error.
         However, if you specify a not-found parameter, it will substitute that instead"
   :signatures [[coll idx] [coll idx not-found]]
   :added "0.1"}
  ([coll idx] (-nth coll idx))
  ([coll idx not-found] (-nth-not-found coll idx not-found)))

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

(defn contains?
  [mp k]
  (-contains-key mp k))

(defn name
  [x] (-name x))

(defn namespace
  [x] (-namespace x))


(defn dispose!
  "Finalizes use of the object by cleaning up resources used by the object"
  [x]
  (-dispose! x)
  nil)


(defn has-meta?
  [x]
  (satisfies? IMeta x))

(defn meta
  [x]
  (-meta x))

(defn with-meta
  [x m]
  (-with-meta x m))

(defn count
  ([coll]
   (if (counted? coll)
     (-count coll)
     (loop [s (seq coll)
            i 0]
       (if (counted? s)
         (+ i (count s))
         (recur (next s)
                (inc i)))))))

(defn assoc
  {:doc "Associates the key with the value in the collection"
   :signatures [[m] [m k v] [m k v & kvs]]
   :added "0.1"}
  ([m] m)
  ([m k v]
     (-assoc m k v))
  ([m k v & rest]
     (apply assoc (-assoc m k v) rest)))

(defn merge
  ([a] a)
  ([a b]
   (reduce
    (fn [a [k v]]
      (assoc a k v))
    a
    b))
  ([a b & cs]
   (apply merge (merge a b) cs)))

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

(defn key [m]
  (-key m))

(defn val [m]
  (-val m))

(defn keys
  {:doc "If called with no arguments returns a transducer that will extract the key from each map entry. If passed
   a collection, will assume that it is a hashmap and return a vector of all keys from the collection."
   :signatures [[] [coll]]
   :added "0.1"}
  ([] (map key))
  ([m]
   (with-handler [g (->Generator)]
     (transduce (map key) yield g m))))

(defn vals
  {:doc "If called with no arguments returns a transducer that will extract the key from each map entry. If passed
   a collection, will assume that it is a hashmap and return a vector of all keys from the collection."
   :signatures [[] [coll]]
   :added "0.1"}
  ([] (map val))
  ([m]
   (with-handler [g (->Generator)]
     (transduce (map val) yield g m))))


(defn seq [x]
  (-seq x))

(defn first [x]
  (if (satisfies? ISeq x)
    (-first x)
    (let [x (seq x)]
      (if (nil? x)
        nil
        (-first x)))))

(defn next [x]
  (if (satisfies? ISeq x)
    (seq (-next x))
    (let [x (seq x)]
      (if (nil? x)
        nil
        (seq (-next x))))))

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


(defn apply [f & args]
  (let [last-itm (last args)
        but-last-cnt (dec (count args))
        arg-array (make-array (+ but-last-cnt
                                 (count last-itm)))
        idx (reduce
             (fn [idx itm]
               (aset arg-array idx itm)
               (inc idx))
             but-last-cnt
             last-itm)]
    (array-copy args 0 arg-array 0 but-last-cnt)
    (-apply f arg-array)))

(defn fnil [f else]
  (fn [x & args]
    (apply f (if (nil? x) else x) args)))


(defn last [coll]
  (if (vector? coll)
    (nth coll (dec (count coll)))
    (loop [coll coll]
      (if-let [v (next coll)]
        (recur v)
        (first coll)))))

(defn butlast [coll]
  (loop [res []
         coll coll]
    (if (next coll)
      (recur (conj res (first coll))
             (next coll))
      (seq res))))

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

(defn repeat
  ([x]
   (cons x (lazy-seq (repeat x))))
  ([n x]
   (take n (repeat x))))

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
  {:doc "Returns a map with distinct elements as keys and the number of occurences as values"
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

(defn seq-reduce [s f acc]
  (if (reduced? acc)
    @acc
    (if (nil? s)
      acc
      (seq-reduce (next s)
                  f
                  (f acc (first s))))))

;; Some logic functions
(defn complement
  {:doc "Given a function, return a new function which takes the same arguments
         but returns the opposite truth value"}
  [f]
  (assert (fn? f) "Complement must be passed a function")
  (fn
    ([] (not (f)))
    ([x] (not (f x)))
    ([x y] (not (f x y)))
    ([x y & more] (not (apply f x y more)))))

;;

;; Cons and List

(deftype Cons [head tail meta]
  IObject
  (-str [this sb]
    (sb "(")
    (let [not-first (atom false)]
      (reduce
       (fn [_ x]
         (if @not-first
           (sb " ")
           (reset! not-first true))
         (-str x sb))
       nil
       this))
    (sb ")"))
  
  ISeq
  (-first [this] head)
  (-next [this] tail)
  ISeqable
  (-seq [this] this)
  IMeta
  (-meta [this] meta)
  (-with-meta [this new-meta]
    (->Cons head tail new-meta))

  IReduce
  (-reduce [this f init]
    (seq-reduce this f init))

  IIndexed
  (-nth [self idx]
    (loop [i idx
           s (seq self)]
      (if (or (= i 0)
              (nil? s))
        (if (nil? s)
          (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"])
          (first s))
        (recur (dec i)
               (next s)))))
  
  (-nth-not-found [self idx not-found]
    (loop [i idx
           s (seq self)]
      (if (or (= i 0)
              (nil? s))
        (if (nil? s)
          (first s)
          not-found)
        (recur (dec i)
               (next s))))))

(defn cons [head tail]
  (->Cons head tail nil))


(deftype List [head tail cnt hash-val meta]
  IObject
  (-hash [this]
    (if hash-val
      hash-val
      (let [val (reduce
                 pixie.stdlib.hashing/ordered-hashing-rf
                 this)]
        (set-field! this :hash-val val)
        val)))

  (-str [this sb]
    (sb "(")
    (let [not-first (atom false)]
      (reduce
       (fn [_ x]
         (if @not-first
           (sb " ")
           (reset! not-first true))
         (-str x sb))
       nil
       this))
    (sb ")"))


  IIndexed

  (-nth [self idx]
    (loop [i idx
           s (seq self)]
      (if (or (= i 0)
              (nil? s))
        (if (nil? s)
          (first s)
          (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"]))
        (recur (dec i)
               (next s)))))
  
  (-nth-not-found [self idx not-found]
    (loop [i idx
           s (seq self)]
      (if (or (= i 0)
              (nil? s))
        (if (nil? s)
          not-found
          (first s))
        (recur (dec i)
               (next s)))))

  
  IReduce
  (-reduce [this f init]
    (seq-reduce this f init))

  
  ISeq
  (-first [this] head)
  (-next [this] tail)

  ICounted
  (-count [this] cnt)

  ISeqable
  (-seq [this] this)

  IMeta
  (-meta [this] meta)
  (-with-meta [this new-meta]
    (->List head tail cnt hash-val new-meta))

  IPersistentCollection
  (-conj [this val]
    (->List val this (inc cnt) nil nil)))


(defn list [& args]
  (loop [acc nil
         idx (dec (count args))
         cnt 1]
    (if (>= idx 0)
      (recur (->List (nth args idx)
                     acc
                     cnt
                     nil
                     nil)
             (dec idx)
             (inc cnt))
      acc)))

;; LazySeq start
(in-ns :pixie.stdlib.lazy-seq)


(deftype LazySeq [f s hash-val meta-data]
  ISeqable
  (-seq [this]
    (sval this)
    (when (.-s this)
      (loop [ls (.-s this)]
        (if (instance? LazySeq ls)
          (recur (sval ls))
          (do (set-field! this :s ls)
              (seq (.-s this)))))))

  ISeq
  (-first [this]
    (seq this)
    (first (.-s this)))

  (-next [this]
    (seq this)
    (next (.-s this)))

  IReduce
  (-reduce [this f init]
    (seq-reduce this f init))

  IMessageObject
  (-get-field [this field]
    (get-field this field)))

(defn sval [this]
  (if (.-f this)
    (do (set-field! this :s ((.-f this)))
        (set-field! this :f nil)
        (.-s this))
    (.-s this)))


(in-ns :pixie.stdlib)

(defn lazy-seq* [f]
  (pixie.stdlib.lazy-seq/->LazySeq f nil nil nil))

(defeffect EGenerator
    (-yield [this val]))

(deftype Generator []
  IEffect
  (-effect-val [this val]
    nil)
  (-effect-finally [this val]
    val)

  EGenerator
  (-yield [this val k]
    (cons val (lazy-seq (k nil)))))

(defn yield
  ([g] nil)
  ([g i]
   (-yield g i)
   g))

(defn sequence [coll]
  (with-handler [gen (->Generator)]
    (reduce yield gen coll)))



;; LazySeq end

;; String Builder

(defn string-builder
  ([] (-string-builder))
  ([sb] (-internal-to-str sb))
  ([sb x]
   (if (instance? String x)
     (-add-to-string-builder sb x)
     (-str x (fn [x]
               (-add-to-string-builder sb x))))))

(defn str
  [& args]
  (reduce
   string-builder
   args))



(defn println [& args]
  (let [sb (-string-builder)
        add-fn (fn [x]
                 (-add-to-string-builder sb x))]
    (loop [idx 0
           sb sb]
      (if (< idx (count args))
        (recur (inc idx)
               (do (-str (aget args idx) add-fn)
                   (add-fn " ")
                 sb))
        (-blocking-println (-finish-string-builder sb))))
    nil))

;;

;; Hashing Functions

(in-ns :pixie.stdlib.hashing)


(def seed 0)
(def C1 (size-t 0xcc9e2d51))
(def C2 (size-t 0x1b873593))
(def LONG-BIT (size-t 32))
(def MASK-32 (size-t 0xFFFFFFFF))

(defn mask-32 [x]
  (bit-and x MASK-32))

(defn rotr [value shift]
  (let [value (size-t value)
        shift (size-t shift)]
    (bit-or (bit-shift-left value shift)
            (bit-shift-right value (- LONG-BIT shift)))))

(defn rotl [value shift]
  (let [value (size-t value)
        shift (size-t shift)]
    (bit-or (bit-shift-right value shift)
            (bit-shift-left value (- LONG-BIT shift)))))

(defn mix-k1 [k1]
  (let [k1 (* k1 C1)
        k1 (rotl k1 15)
        k1 (* k1 C2)]
    k1))

(defn mix-h1 [h1 k1]
  (let [h1 (bit-xor h1 k1)
        h1 (rotr h1 13)
        h1 (+ (* h1 5) 0xe6546b64)]
    h1))


(defn fmix [h1 length]
  (let [h1 (bit-xor h1 length)
        h1 (bit-xor h1 (bit-shift-right h1 16))
        h1 (* h1 0x85ebca6b)
        h1 (bit-xor h1 (bit-shift-right h1 13))
        h1 (* h1 0xc2b2ae35)
        h1 (bit-xor h1 (bit-shift-right h1 16))]
    h1))


(defn mix-coll-hash [hash count]
  (let [h1 seed
        k1 (mix-k1 hash)
        h1 (mix-h1 h1 k1)]
    (fmix h1 count)))

(deftype HashingState [n hash]
  IMessageObject
  (-get-field [this field]
    (get-field this field)))

(defn unordered-hashing-rf
  ([] (->HashingState (size-t 0) (size-t 1)))
  ([acc]
   (mix-coll-hash (.-hash acc)
                  (.-n acc)))
  ([acc itm]
   (set-field! acc :n (inc (.-n acc)))
   (set-field! acc :hash (+ (.-hash acc)
                            (hash itm)))))

(defn ordered-hashing-rf
  ([] (->HashingState 0 1))
  ([acc]
   (mix-coll-hash (.-hash acc)
                  (.-n acc)))
  ([acc itm]
   (set-field! acc :n (inc (.-n acc)))
   (set-field! acc :hash (+ (* (size-t 31) (.-hash acc))
                            (hash itm)))))



(defn hash-int [input]
  (if (= input 0)
    0
    (let [k1 (mix-k1 input)
          h1 (mix-h1 seed k1)]
      (fmix h1 4))))

(defn hash-unencoded-chars [u]
  (let [h1 (loop [i 1
                  h1 seed]
             (if (< i (count u))
               (let [k1 (bit-or (int (nth u (dec i)))
                                (bit-shift-left (int (nth u i)) 16))
                     k1 (mix-k1 k1)
                     h1 (mix-h1 h1 k1)]
                 (recur (+ 2 i)
                        h1))
               h1))
        h1 (if (= (bit-and (count u) 1) 1)
             (let [k1 (int (nth u (dec (count u))))
                   k1 (mix-k1 k1)
                   h1 (bit-xor h1 k1)]
               h1)
             h1)]
    (fmix h1 (* 2 (count u)))))

(in-ns :pixie.stdlib)

;; End Hashing Functions


;; Reduced

(deftype Reduced [x]
  IDeref
  (-deref [this] x))

(defn reduced [x]
  (->Reduced x))

(defn reduced? [x]
  (instance? Reduced x))

;; End Reduced

;; Basic Transducer Support

(defn transduce
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
     (f result))))

(defn reduce 
  ([rf col]
   (rf (reduce rf (rf) col)))
  ([rf init col]
   (-reduce col rf init)))

(defn into
  ^{:doc "Add the elements of `from` to the collection `to`."
    :signatures [[to from]]
    :added "0.1"}
  ([to from]
   (if (satisfies? IToTransient to)
     (persistent! (reduce conj! (transient to) from))
     (reduce conj to from)))
  ([to xform from]
   (if (satisfies? IToTransient to)
     (transduce xform conj! (transient to) from)
     (transduce xform conj to from))))

(defn vec
  {:doc "Converts a reducable collection into a vector using the (optional) transducer."
   :signatures [[coll] [xform coll]]
   :added "0.1"}
  ([coll]
     (transduce conj coll))
  ([xform coll]
     (transduce xform conj coll)))

(defn map
  ^{:doc "map - creates a transducer that applies f to every input element"
    :signatures [[f] [f coll]]
    :added "0.1"}
  ([f]
   (fn [xf]
     (fn
       ([] (xf))
       ([result] (xf result))
       ([result item] (xf result (f item))))))
  ([f coll]
   (with-handler [g (->Generator)]
     (transduce (map f) yield g coll)))
  ([f & colls]
   (let [step (fn step [cs]
                (lazy-seq*
                 (fn []
                   (let [ss (map seq cs)]
                     (if (every? identity ss)
                       (cons (map first ss) (step (map next ss)))
                       nil)))))]
     (map (fn [args] (apply f args)) (step colls)))))

(defn mapv
  ([f col]
   (transduce (map f) conj col)))


(defn filter
  {:doc "Filter the collection for elements matching the predicate."
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
   (with-handler [g (->Generator)]
     (transduce (filter pred) yield g coll))))

(defn interpose
  ^{:doc "Returns a transducer that inserts `val` in between elements of a collection."
    :signatures [[val] [val coll]]
    :added "0.1"}
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
   (transduce (interpose val) conj coll)))


(def preserving-reduced
  (fn preserving-reduced [rf]
    (fn pr-inner [a b]
      (let [ret (rf a b)]
        (if (reduced? ret)
          (reduced ret)
          ret)))))

(defn cat
  {:doc "A transducer that concatenates elements of a collection."
   :added "0.1"}
  [rf]
  (let [rrf (preserving-reduced rf)]
    (fn cat-inner
      ([] (rf))
      ([result] (rf result))
      ([result input]
       (reduce rrf result input)))))

(defn concat
  {:doc "Concatenates its arguments."
   :signatures [[& args]]
   :added "0.1"}
  [& args] (transduce cat conj args))

(defn mapcat
  {:doc "Maps f over the elements of coll and concatenates the result"
   :added "0.1"}
  ([f]
   (comp (map f) cat))
  ([f coll]
   (transduce (mapcat f) conj coll)))

(defn every?
  {:doc "Check if every element of the collection satisfies the predicate."
   :added "0.1"}
  [pred coll]
  (reduce
   (fn [_ i]
     (if (pred i)
       true
       (reduced false)))
   true
   coll))


;; End Basic Transudcer Support

;; Type Checks

(defn instance?
  {:doc "Checks if x is an instance of t.

                           When t is seqable, checks if x is an instance of
                           any of the types contained therein."
   :signatures [[t x]]}
  [t x]
  (if (-satisfies? ISeqable t)
    (let [ts (seq t)]
      (if (not ts) false
          (if (-instance? (first ts) x)
            true
            (instance? (rest ts) x))))
    (-instance? t x)))

(defn satisfies?
  ^{:doc "Checks if x satisfies the protocol p.

                            When p is seqable, checks if x satisfies all of
                            the protocols contained therein."
    :signatures [[t x]]}
  [p x]  
  (if (-satisfies? ISeqable p)
    (let [ps (seq p)]
      (if (not ps) true
          (if (not (-satisfies? (first ps) x))
            false
            (satisfies? (rest ps) x))))
    (-satisfies? p x)))


(defn true? [v] (identical? v true))
(defn false? [v] (identical? v false))

(defn number? [v] (instance? Number v))
(defn integer? [v] (instance? Integer v))
(defn float? [v] (instance? Float v))
(defn ratio? [v] (instance? Ratio v))

(defn char? [v] (instance? Character v))
(defn string? [v] (instance? String v))
(defn symbol? [v] (instance? Symbol v))
(defn keyword? [v] (instance? Keyword v))

(defn list? [v] (instance? [PersistentList Cons] v))
(defn seq? [v] (satisfies? ISeq v))
(defn set? [v] (instance? pixie.stdlib.persistent-hash-set/PersistentHashSet v))
(defn map? [v] (satisfies? IMap v))
(defn fn? [v] (satisfies? IFn v))

(defn indexed? [v] (satisfies? IIndexed v))
(defn counted? [v] (satisfies? ICounted v))
(defn vector? [v] (satisfies? IVector v))

(defn int
  {:doc "Converts a number to an integer."
   :since "0.1"}
  [x]
  (cond
   (integer? x) x
   (float? x) (lround (floor x))
   (ratio? x) (int (/ (float (numerator x)) (float (denominator x))))
   (char? x) (-internal-int x)
   :else (throw
          [:pixie.stdlib/ConversionException
           (throw (str "Can't convert a value of type " (type x) " to an Integer"))])))


;; End Type Checks

;; Range

(in-ns :pixie.stdlib.range)

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
  ISeqable
  (-seq [self]
    (when (or (and (> step 0) (< start stop))
              (and (< step 0) (> start stop)))
      (cons start (lazy-seq* #(range (+ start step) stop step)))))
  IObject
  (-str [this sbf]
    (-str (seq this) sbf))
  (-repr [this sbf]
    (-repr (seq this) sbf))
  (-eq [this sb]
    nil))

(def MAX-NUMBER 0xFFFFFFFF) ;; 32 bits ought to be enough for anyone ;-)

(in-ns :pixie.stdlib)

(defn range
  {:doc "Returns a range of numbers."
   :examples [["(seq (range 3))" nil (0 1 2)]
              ["(seq (range 3 5))" nil (3 4)]
              ["(seq (range 0 10 2))" nil (0 2 4 6 8)]
              ["(seq (range 5 -1 -1))" nil (5 4 3 2 1 0)]]
   :signatures [[] [stop] [start stop] [start stop step]]
   :added "0.1"}
  ([] (pixie.stdlib.range/->Range 0 MAX-NUMBER 1))
  ([stop] (pixie.stdlib.range/->Range 0 stop 1))
  ([start stop] (pixie.stdlib.range/->Range start stop 1))
  ([start stop step] (pixie.stdlib.range/->Range start stop step)))

;; End Range

(in-ns :pixie.stdlib)

;; Extend String

(extend-type String
  IIndexed
  (-nth [self idx]
    (-str-nth self idx))

  ICounted
  (-count [self]
    (-str-len self))

  IReduce
  (-reduce [self f init]
    (loop [acc init
           idx 0]
      (if (< idx (count self))
        (if (reduced? acc)
          @acc
          (recur (f acc (nth self idx))
                 (inc idx)))
        acc))))

;; End Extend String

;; Extend Array

(satisfy IVector Array)

(extend-type Array
  IObject
  (-str [this sb]
    (sb "[")
    (let [not-first (atom false)]
      (reduce
       (fn [_ x]
         (if @not-first
           (sb " ")
           (reset! not-first true))
         (-str x sb))
       nil
       this))
    (sb "]"))
 
  IPersistentCollection
  (-conj [arr itm]
    (conj (pixie.stdlib.persistent-vector/vector-from-array arr) itm))

  IIndexed
  (-nth [this idx]
    (if (and (<= 0 idx)
             (< idx (count this)))
      (aget this idx)
      (throw [:pixie.stdlib/IndexOutOfRangeException
              "Index out of range"])))
  (-nth-not-found [this idx not-found]
    (if (and (<= 0 idx)
             (< idx (count this)))
      (aget this idx)
      not-found))
  
  ICounted
  (-count ([arr]
           (.-count arr)))

  IReduce
  (-reduce [this f init]
    (loop [idx 0
           acc init]
      (if (reduced? acc)
        @acc
        (if (< idx (count this))
          (recur (inc idx)
                 (f acc (aget this idx)))
          acc))))

  ISeqable
  (-seq [this]
    (sequence this)))

(extend-type ArrayMap
  ILookup
  (-val-at [this kw not-found]
    (let [lst (array-map-to-array this)]
      (loop [idx 0]
        (if (< idx (count lst))
          (if (= (nth lst idx) kw)
            (nth lst (inc idx))
            (recur (+ idx 2)))
          not-found))))

  IReduce
  (-reduce [this f init]
    (let [lst (array-map-to-array this)]
      (loop [acc init
             idx 0]
        (if (reduced? acc)
          @acc
          (if (< idx (count lst))
            (let [k (nth lst idx)
                  v (nth lst (inc idx))]
              (recur (f acc (map-entry k v))
                     (+ idx 2)))
            acc))))))

(defn array-copy [from from-idx to to-idx size]
  (loop [idx 0]
    (when (< idx size)
      (do (aset to (+ to-idx idx) (aget from (+ from-idx idx)))
          (recur (inc idx))))))

(defn array-append [arr val]
  (let [new-array (make-array (inc (count arr)))]
    (array-copy arr 0 new-array 0 (count arr))
    (aset new-array (count arr) val)
    new-array))

(defn array-clone [arr]
  (let [new-array (make-array (count arr))]
    (array-copy arr 0 new-array 0 (count arr))
    new-array))

(defn array-resize [arr size]
  (let [new-array (make-array size)]
    (array-copy arr 0 new-array 0 size)
    new-array))

(defn to-array [coll]
  (let [arr (make-array (count coll))]
    (reduce
     (fn [idx i]
       (aset arr idx i)
       (inc idx))
     0
     coll)
    arr))

;;; Extend Var

(extend-type Var
  IObject
  (-str [this sb]
    (if (namespace this)
      (do (sb "<Var ")
          (-str (namespace this) sb)
          (sb "/")
          (-str (name this) sb)
          (sb ">"))
      (do (sb "<Var ")
          (-str (name this) sb)
          (sb ">")))))

;;;

;; Atom

(defprotocol IAtom
  (-swap! [this f args])
  (-reset! [this val]))

(deftype Atom [value]
  IDeref
  (-deref [this]
    value)

  IAtom
  (-swap! [this f args]
    (let [new-val (apply f @this args)]
      (-reset! this new-val)
      new-val))
  (-reset! [this val]
    (set-field! this :value val)))

(defn atom [init]
  (->Atom init))

(defn swap! [a f & args]
  (-swap! a f args))

(defn reset! [a v]
  (-reset! a v))

;; End Atom

;; Map Entry



(deftype MapEntry [k v meta]
  IMapEntry
  (-key [this]
    k)
  (-val [this]
    v)
  
  IIndexed
  (-nth [this idx]
    (cond
      (= idx 0) k
      (= idx 1) v
      :else (throw [:pixie.stdlib/IndexError
                    "Index out of Range"])))
  
  (-nth-not-found [this idx not-found]
    (cond
      (= idx 0) k
      (= idx 1) v
      :else not-found)))

(defn map-entry [k v]
  (->MapEntry k v nil))

;; End Map Entry


;; PersistentVector

(in-ns :pixie.stdlib.persistent-vector)

(deftype Node [edit array]
  IMessageObject
  (-get-field [this name]
    (get-field this name)))

(defn new-node
  ([edit]
   (new-node edit (make-array 32)))
  ([edit array]
   (->Node edit array)))

(def EMPTY-NODE (new-node nil))



(defn tail-off [this]
  (let [cnt (.-cnt this)]
    (if (< cnt 32)
      0
      (bit-shift-left (bit-shift-right (dec cnt) 5) 5))))

(defn array-for [this i]
  (if (and (<= 0 i) (< i (.-cnt this)))
    (if (>= i (tail-off this))
      (.-tail this)
      (loop [node (.-root this)
             level (.-shift this)]
        (if (> level 0)
          (recur (aget (.-array node)
                       (bit-and (bit-shift-right i level) 0x01f))
                 (- level 5))
          (.-array node))))
    (throw [:pixie.stdlib/IndexOutOfRangeException
            "Index out of range"])))

(deftype PersistentVector [cnt shift root tail hash-val meta]
  IObject
  (-hash [this]
    (if hash-val
      hash-val
      (let [val (reduce
                 pixie.stdlib.hashing/ordered-hashing-rf
                 this)]
        (set-field! this :hash-val val)
        val)))

  (-str [this sb]
    (sb "[")
    (let [not-first (atom false)]
      (reduce
       (fn [_ x]
         (if @not-first
           (sb " ")
           (reset! not-first true))
         (-str x sb))
       nil
       this))
    (sb "]"))

  IVector

  ISeqable
  (-seq [this]
    (sequence this))
  
  
  IMessageObject
  (-get-field [this name]
    (get-field this name))
  
  IPersistentCollection
  (-conj [this val]
    (assert (< cnt 0xFFFFFFFF) "Vector too large")

    (if (< (- cnt (tail-off this)) 32)
      (let [new-tail (array-append tail val)]
        (->PersistentVector (inc cnt) shift root new-tail hash-val meta))
      
      (let [tail-node (->Node (.-edit root) tail)]
        (if (> (bit-shift-right cnt 5) (bit-shift-left 1 shift))

          (let [new-root (new-node (.-edit root))
                new-root-arr (.-array new-root)]
            (aset new-root-arr 0 root)
            (aset new-root-arr 1 (new-path (.-edit root) shift tail-node))
            (->PersistentVector (inc cnt)
                                (+ shift 5)
                                new-root
                                (array val)
                                hash-val
                                meta))
          (let [new-root (push-tail this shift root tail-node)]
            (->PersistentVector (inc cnt)
                                shift
                                new-root
                                (array val)
                                hash-val
                                meta))))))
  IIndexed
  (-nth [self i]
    (if (and (<= 0 i)
             (< i cnt))
      (let [node (array-for self i)]
        (aget node (bit-and i 0x01F)))
      (throw [:pixie.stdlib/IndexOutOfRange
              (str "Index out of range, got " i " only have " cnt)])))
  
  (-nth-not-found [self i not-found]
    (if (and (<= 0 i)
             (< i cnt))
      (let [node (array-for self i)]
        (aget node (bit-and i 0x01F)))
      not-found))

  

  ILookup
  (-val-at [this val]
    (-nth-not-found self val nil))
  

  ICounted
  (-count [this] cnt)

  IPop
  (-pop [this]
    (assert (not= cnt 0) "Can't pop an empty vector")

    (if (= cnt 1)
      EMPTY
      (if (> (- cnt (tail-off this)) 1)
        (let [size (dec (count tail))
              new-tail (array-resize tail size)]
          (->PersistentVector (dec cnt)
                              shift
                              root
                              new-tail
                              hash-val
                              meta))
        (let [new-tail (array-for this (- cnt 2))
              new-root (pop-tail this shift root)]
          (cond
            (nil? new-root)
            (->PersisentVector (dec cnt)
                               shift
                               EMPTY-NODE
                               new-tail
                               hash-val
                               meta)
            (and (> shift 5)
                 (nil? (aget (.-array new-root) 1)))
            (->PersistentVector (dec cnt)
                                (- shift 5)
                                (aget (.-array new-root) 0)
                                new-tail
                                hash-val
                                meta)

            :else
            (->PersistentVector (dec cnt)
                                shift
                                new-root
                                new-tail
                                hash-val
                                meta))))))

  IAssociative
  (-assoc [this k v]
    (assert (int? k) "Vectors expect ints as keys")
    (if (and (>= idx 0)
             (< idx cnt))
      (if (>= idx (tail-off this))
        (let [new-tail (array-clone tail)]
          (aset new-tail (bit-and idx 0x01f) val)
          (->PersistentVector cnt shift root new-tail hash-val meta))
        (->PersistentVector cnt shift (do-assoc shift root idx val) tail hash-val meta))
      (if (= idx cnt)
        (-conj this val)
        (throw [:pixie.stdlib/IndexOutOfRange
                "Can only assoc to the end or the contents of a vector"]))))

  IToTransient
  (-transient [this]
    (->TransientVector cnt shift
                       (editable-root root)
                       (editable-tail tail)
                       meta))

  IReduce
  (-reduce [this f init]
    ((fn outer-loop [i acc]
       (if (< i cnt)
         (let [array (array-for this i)]
           ((fn inner-loop [i j acc]
              (if (< j (count array))
                (let [acc (f acc (aget array j))]
                  (if (reduced? acc)
                    @acc
                    (inner-loop (inc i)
                                (inc j)
                                acc)))
                (outer-loop i acc)))
            i 0 acc))
         acc))
     0 init)))

(defn do-assoc [lvl node idx val]
  (let [new-array (array-clone (.-array node))
        ret (if (= lvl 0)
              (aset new-array (bit-and idx 0x01f) val)
              (let [sub-idx (bit-and (bit-shift-right idx lvl) 0x01f)]
                (aset new-array sub-idx (do-assoc (- lvl 5) (aget (.-array node) idx val)))))]
    (->Node (.-edit node) new-array)))


(defn push-tail [this level parent tail-node]
  (let [subidx (bit-and (bit-shift-right (dec (.-cnt this)) level) 0x01f)
        ret-array (array-clone (.-array parent))
        node-to-insert (if (= level 5)
                         tail-node
                         (let [child (aget (.-array parent) subidx)]
                           (if (= child nil)
                             (new-path (.-edit (.-root this))
                                       (- level 5)
                                       tail-node)
                             (push-tail this
                                        (- level 5)
                                        child
                                        tail-node))))]
    (aset ret-array subidx node-to-insert)
    (->Node (.-edit parent) ret-array)))

(defn pop-tail [this level node]
  (let [sub-idx (bit-and (bit-shift-right (dec (.-cnt this)) level) 0x01F)]
    (cond
      (> level 5)
      (let [new-child (pop-tail this
                                (- level 5)
                                (aget (.-array node) sub-idx))]
        (if (or (nil? new-child)
                (= sub-idx 0))
          nil
          (let [root (.-root this)
                ret (->Node (.-edit root)
                            (.-array node))]
            (aset (.-array ret) sub-idx new-child)
            ret)))
      
      (= sub-idx 0)
      nil

      :else
      (let [root (.-root this)
            ret (->Node (.-edit root)
                        (array-clone (.-array node)))]
        (aset (.-array ret) sub-idx nil)
        ret))))

(defn new-path [edit level node]
  (if (= level 0)
    node
    (let [nnode (new-node edit)]
      (aset (.-array nnode) 0 (new-path edit (- level 5) node))
      nnode)))


(def EMPTY (->PersistentVector 0 5 EMPTY-NODE (array 0) nil nil))

(defn vector-from-array [arr]
  (if (< (count arr) 32)
    (->PersistentVector (count arr) 5 EMPTY-NODE arr nil nil)
    (into [] arr)))


;; Transient Vector

#_(deftype Edited [])
(def edited ::edited)


(deftype TransientVector [cnt shift root tail meta]
  IMessageObject
  (-get-field [this field]
    (get-field this field))

  ITransientCollection
  (-conj! [this val]
    (ensure-editable this)
    (let [i cnt]
      (if (< (- i (tail-off this)) 32)
        (do (aset tail (bit-and i 0x01F) val)
            (set-field! this :cnt (inc cnt))
            this)
        (let [tail-node (->Node (.-edit root) tail)]
          (set-field! this :tail (make-array 32))
          (aset tail 0 val)
          (if (> (bit-shift-right cnt 5)
                 (bit-shift-left 1 shift))
            (let [root-array (make-array 32)]
              (aset root-array 0 root)
              (aset root-array 1 (new-path (.-edit root) shift tail-node))
              (set-field! this :shift (+ shift 5))
              (set-field! this :root new-root)
              (set-field! this :cnt (inc cnt))
              this)
            (do (set-field this :root (push-tail-transient shift root tail-node))
                (set-field this :cnt (inc cnt))
                this))))))

  ITransient
  (-persistent! [this]
    (ensure-editable this)
    (let [trimmed (make-array (- cnt (tail-off self)))]
      (array-copy tail 0 trimmed 0 (count trimmed))
      (->PersistentVector cnt shift root trimmed nil meta))))


(defn editable-root [node]
  (->Node edited (array-clone (.-array node))))

(defn ensure-editable [node]
  (assert (nil? (.-edit node))
          "Transient used after call to persist!"))

(defn ensure-node-editable [this node]
  (let [root (.-root this)]
    (if (identical? (.-edit node) (.-edit root))
      node
      (->Node (.-edit root) (.-array node)))))

(defn editable-tail [tail]
  (let [ret (make-array 32)]
    (array-copy tail 0 ret 0 (count tail))
    ret))

(in-ns :pixie.stdlib)
;; End Persistent Vector

;; Persistent Hash Map

(in-ns :pixie.stdlib.persistent-hash-map)

(def MASK-32 0xFFFFFFFF)


(defprotocol INode
  (-assoc-inode [this shift hash-val key val added-leaf])
  (-find [self shift hash-val key not-found])
  (-reduce-inode [self f init])
  (-without [self shift hash key]))

(defn mask [hash shift]
  (bit-and (bit-shift-right hash shift) 0x01f))

(defn bitpos [hash shift]
  (bit-and (bit-shift-left 1 (mask hash shift)) MASK-32))

(defn index [this bit]
  (bit-count32 (bit-and (.-bitmap this)
                        (dec bit))))


(deftype BitmapIndexedNode [edit bitmap array]
  IMessageObject
  (-get-field [this field]
    (get-field this field))
  
  INode
  (-assoc-inode [this shift hash-val key val added-leaf]
    (let [bit (bitpos hash-val shift)
          idx (index this bit)]
      (if (not= (bit-and bitmap bit) 0)
        (let [key-or-null (aget array (* 2 idx))
              val-or-node (aget array (inc (* 2 idx)))]
          (if (nil? key-or-null)
            (let [n (-assoc-inode val-or-node
                                  (+ shift 5)
                                  (bit-and hash-val MASK-32)
                                  key
                                  val
                                  added-leaf)]
              (if (identical? n val-or-node)
                this
                (->BitmapIndexedNode nil
                                     bitmap
                                     (clone-and-set array (inc (* 2 idx)) n))))
            (if (= key key-or-null)
              (if (identical? val val-or-node)
                this
                (->BitmapIndexedNode nil
                                     bitmap
                                     (clone-and-set array (inc (* 2 idx)) val)))
              (do (reset! added-leaf true)
                  (->BitmapIndexedNode nil bitmap
                                       (clone-and-set2 array
                                                       (* 2 idx) nil
                                                       (inc (* 2 idx))
                                                       (create-node (+ shift 5)
                                                                    key-or-null
                                                                    val-or-node
                                                                    hash-val
                                                                    key
                                                                    val)))))))
        (let [n (bit-count32 bitmap)]
          (if (>= n 16)
            (let [nodes (make-array 32)
                  jdx (mask hash-val shift)]
              (aset nodes jdx (-assoc-inode BitmapIndexedNode-EMPTY
                                            (+ shift 5)
                                            hash-val
                                            key
                                            val
                                            added-leaf))
              (loop [j 0
                     i 0]
                (when (< i 32)
                  (if (not= (bit-and (bit-shift-right bitmap i) 1) 0)
                    (do (if (nil? (aget array j))
                          (aset nodes i (aget array (inc j)))
                          (aset nodes i (-assoc-inode BitmapIndexedNode-EMPTY
                                                      (+ shift 5)
                                                      (pixie.stdlib/hash (aget array j))
                                                      (aget array j)
                                                      (aget array (inc j))
                                                      added-leaf)))
                        (recur (+ 2 j)
                               (inc i)))
                    (recur j
                           (inc i)))))
              (->ArrayNode nil (inc n) nodes))
            (let [new-array (make-array (* 2 (inc n)))]
              (array-copy array 0 new-array 0 (* 2 idx))
              (aset new-array (* 2 idx) key)
              (reset! added-leaf true)
              (aset new-array (inc (* 2 idx)) val)
              (array-copy array (* 2 idx) new-array (* 2 (inc idx)) (* 2 (- n idx)))
              (->BitmapIndexedNode nil (bit-or bitmap bit) new-array)))))))

  (-find [self shift hash-val key not-found]
    (let [bit (bitpos hash-val shift)]
      (if (= (bit-and bitmap bit) 0)
        not-found
        (let [idx (index self bit)
              key-or-null (aget array (* 2 idx))
              val-or-node (aget array (inc (* 2 idx)))]
          (if (nil? key-or-null)
            (-find val-or-node (+ 5 shift) hash-val key not-found)
            (if (= key key-or-null)
              val-or-node
              not-found))))))
  
  (-reduce-inode [this f init]
    (loop [x 0
           acc init]
      (if (< x (count array))
        (let [key-or-nil (aget array x)
              val-or-node (aget array (inc x))
              acc (if (and (nil? key-or-nil)
                           (not (nil? val-or-node)))
                    (-reduce-inode val-or-node f acc)
                    (f acc (map-entry key-or-nil val-or-node)))]
          (if (reduced? acc)
            acc
            (recur (+ 2 x) acc)))
        acc))))

(def BitmapIndexedNode-EMPTY (->BitmapIndexedNode nil (size-t 0) []))

(defn ann [x]
  (assert x)
  x)

(deftype ArrayNode [edit cnt array]
  INode
  (-assoc-inode [this shift hash-val key val added-leaf]
    (let [idx (mask hash-val shift)
          node (aget array idx)]
      (if (nil? node)
        (->ArrayNode nil
                     (inc cnt)
                     (clone-and-set array
                                    idx
                                    (-assoc-inode BitmapIndexedNode-EMPTY
                                                  (+ shift 5)
                                                  hash-val
                                                  key
                                                  val
                                                  added-leaf)))
        (let [n (-assoc-inode node
                            (+ 5 shift)
                            hash-val
                            key
                            val
                            added-leaf)]
          (if (identical? n node)
            this
            (->ArrayNode nil cnt (clone-and-set array idx n)))))))
  (-find [this shift hash-val key not-found]
    (let [idx (mask hash-val shift)
          node (aget array idx)]
      (if (nil? node)
        not-found
        (-find node
               (+ shift 5)
               hash-val
               key
               not-found))))

  (-reduce-inode [this f init]
    (loop [x 0
           acc init]
      (if (< x (count array))
        (let [node (aget array x)]
          (if (not (nil? node))
            (let [acc (-reduce-inode node f acc)]
              (if (reduced? acc)
                acc
                (recur (inc x) acc)))
            (recur (inc x) acc)))
        acc))))

(deftype PersistentHashMap [cnt root has-nil? nil-val hash-val meta]
  IMap
  IFn
  (-invoke [this k]
    (-val-at this k nil))
  
  IObject
  (-hash [this]
    (if hash-val
      hash-val
      (do (set-field! this :hash-val
                      (transduce cat
                                 pixie.stdlib.hashing/unordered-hash-reducing-fn
                                 this))
          hash-val)))
  
  (-str [this sb]
    (sb "{")
    (let [not-first (atom false)]
      (reduce
       (fn [_ x]
         (if @not-first
           (sb " ")
           (reset! not-first true))
         (-str (key x) sb)
         (sb " ")
         (-str (val x) sb))
       nil
       this))
    (sb "}"))
  
  IMeta
  (-meta [this]
    meta)
  (-with-meta [this new-meta]
    (->PersistentHashMap cnt root has-nil? nil-val hash-val new-meta))

  IEmpty
  (-empty [this]
    (-with-meta pixie.stdlib.persistent-hash-map/EMPTY
                meta))
  
  IAssociative
  (-assoc [this key val]
    (if (nil? key)
      (if (identical? val nil-val)
        this
        (->PersistentHashMap cnt root true val nil meta))
      (let [new-root (if (nil? root)
                       BitmapIndexedNode-EMPTY
                       root)
            added-leaf (atom false)
            new-root (-assoc-inode new-root
                                   0
                                   (bit-and (hash key) MASK-32)
                                   key
                                   val
                                   added-leaf)]
        (if (identical? new-root root)
          this
          (->PersistentHashMap (if @added-leaf
                                 (inc cnt)
                                 cnt)
                               new-root
                               has-nil?
                               nil-val
                               nil
                               meta)))))

  (-contains-key [this k]
    (if (identical? (-val-at this k NOT-FOUND) NOT-FOUND)
      false
      true))

  ILookup
  (-val-at [this key not-found]
    (if (nil? key)
      (if has-nil?
        nil-val
        not-found)
      (if (nil? root)
        not-found
        (-find root 0
               (bit-and (hash key) MASK-32)
               key
               not-found))))

  

  IReduce
  (-reduce [this f init]
    (let [acc (if has-nil?
                (f init nil-val)
                init)]
      (if (reduced? acc)
        @acc
        (if root
          (let [acc (-reduce-inode root f acc)]
            (if (reduced? acc)
              @acc
              acc))
          acc)))))

(deftype NOT-FOUND-TP [])
(def NOT-FOUND (->NOT-FOUND-TP))

(def EMPTY (->PersistentHashMap (size-t 0) nil false nil nil nil))

(defn create-node [shift key1 val1 key2hash key2 val2]
  (let [key1hash (bit-and (pixie.stdlib/hash key1) MASK-32)]
    (if (= key1hash key2hash)
      (do
        (println "HASH " key1 val1 key2 val2 key1hash key2hash)
        (->HashCollisionNode nil key1hash [key1 val1 key2 val2]))
      (let [added-leaf (atom false)]
        (-> BitmapIndexedNode-EMPTY
            (-assoc-inode shift key1hash key1 val1 added-leaf)
            (-assoc-inode shift key2hash key2 val2 added-leaf))))))

(defn clone-and-set [array i a]
  (let [clone (array-clone array)]
    (aset clone i a)
    clone))

(defn clone-and-set2 [array i a j b]
  (let [clone (array-clone array)]
    (aset clone i a)
    (aset clone j b)
    clone))

(in-ns :pixie.stdlib)

(defn hashmap [& args]
  (loop [idx 0
         acc pixie.stdlib.persistent-hash-map/EMPTY]
    (if (< idx (count args))
      (do (assert (> (- (count args) idx) 1) "hashmap requires even number of args")
          (recur (+ 2 idx)
                 (assoc acc (nth args idx) (nth args (inc idx)))))
      acc)))

;; End Persistent Hash Map

;; Start Persistent Hash Set

(in-ns :pixie.stdlib.persistent-hash-set)

(deftype PersistentHashSet [m hash-val meta]
  IObject
  (-hash [this]
    (when-not hash-val
      (set-field! this :hash-val (reduce
                                  unordered-hashing-rf
                                  this)))
    hash-val)

  (-str [this sb]
    (sb "#{")
    (let [not-first (atom false)]
      (reduce
       (fn [_ x]
         (if @not-first
           (sb " ")
           (reset! not-first true))
         (-str x sb))
       nil
       this))
    (sb "}"))
  
  ICounted
  (-count [this]
    (-count m))

  IPersistentCollection
  (-conj [this x]
    (->PersistentHashSet (-assoc m x x) nil meta))
  (-disj [this x]
    (->PersistentHashSet (-dissoc m x) nil meta))

  IMeta
  (-meta [this]
    meta)

  (-with-meta [this x]
    (->PersistentHashSet m hash-val x))

  IAssociative
  (-contains-key [this x]
    (-contains-key m x))

  ILookup
  (-val-at [this k not-found]
    (-val-at m k not-found))

  IReduce
  (-reduce [this f init]
    (reduce
     (fn [acc kv]
       (f acc (key kv)))
     init
     m)))

(def EMPTY (->PersistentHashSet
            pixie.stdlib.persistent-hash-map/EMPTY
            nil
            nil))

;; End Persistent Hash Set

(in-ns :pixie.stdlib)

(defn set [coll]
  (into pixie.stdlib.persistent-hash-set/EMPTY
        coll))


;; Extend Core Types

(extend -invoke Code -invoke)
(extend -invoke NativeFn -invoke)
(extend -invoke VariadicCode -invoke)
(extend -invoke MultiArityFn -invoke)
(extend -invoke Closure -invoke)
(extend -invoke Var -invoke)
(extend -invoke PolymorphicFn -invoke)
(extend -invoke DoublePolymorphicFn -invoke)

(extend -name Keyword -internal-get-name)
(extend -namespace Keyword -internal-get-ns)
(extend -hash Keyword (fn [x]
                        (let [v (-internal-get-hash x)]
                          (if (zero? v)
                            (let [h (pixie.stdlib.hashing/hash-unencoded-chars (str x))]
                              (-internal-store-hash x h)
                              h)
                            v))))

(extend -invoke Keyword (fn
                          ([this o]
                           (-val-at o this nil))
                          ([this o not-found]
                            (-val-at o this not-found))))



(extend -name Symbol -internal-get-name)
(extend -namespace Symbol -internal-get-ns)
(extend -hash Symbol (fn [x]
                        (let [v (-internal-get-hash x)]
                          (if (zero? v)
                            (let [h (pixie.stdlib.hashing/hash-unencoded-chars (str x))]
                              (-internal-store-hash x h)
                              h)
                            v))))

(extend -name String identity)
(extend -namespace String (fn [x] nil))





;(extend -reduce Cons seq-reduce)
;(extend -reduce PersistentList seq-reduce)
;(extend -reduce LazySeq seq-reduce)



;; Buffer

(extend -reduce Buffer
        (fn [b f init]
          (loop [idx 0
                 acc init]
            (if (reduced? acc)
              @acc
              (if (< idx (count b))
                (let [val (pixie.ffi/unpack b idx CUInt8)]
                  (recur (inc idx)
                         (f acc val)))
                acc)))))

;;


(extend -str Bool
  (fn [x sb]
    (if x
      (sb "true")
      (sb "false"))))
(extend -repr Bool -str)

(extend-type Nil
  IObject
  (-str [this f]
    (f "nil"))
  (-repr [this f]
    (f "nil"))
  (-hash [this]
    1000000)
  (-eq [this other]
    (identical? this other))

  IPersistentCollection
  (-conj [this x]
    (vector x))
  (-disj [this x]
    nil)

  IAssociative
  (-assoc [this k v]
    (hashmap k v))
  (-dissoc [this k]
    nil)
  (-contains-key [this k]
    false)
  
  ILookup
  (-val-at
    ([this k] nil)
    ([this k not-found] nil))
  
  IDeref
  (-deref [this]
    nil)

  IIndexed
  
  (-nth [this idx]
    (throw [:pixie.stdlib/IndexOutOfRangeException
            "Index out of range"]))
  (-nth-not-found [this idx not-found]
    not-found)

  IReduce
  (-reduce [this f init]
    init)

  ICounted
  (-count [this]
    0)

  ISeqable
  (-seq [this]
    nil)

  ISeq
  (-first [this]
    nil)
  (-next [this]
    nil))


(extend -with-meta Nil (fn [self _] nil))
(extend -contains-key Nil (fn [_ _] false))

(extend -hash Integer pixie.stdlib.hashing/hash-int)

(extend -eq Integer -num-eq)
(extend -eq Float -num-eq)
(extend -eq Ratio -num-eq)

(defn vector [& args]
  (pixie.stdlib.persistent-vector/vector-from-array args))


;; End Extend Core Types

;; NS functions

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
  [from-ns ns-sym & filters]
  (assert ns-sym "Must provide a ns-sym")
  (assert from-ns "Must provide a from-ns")
  (let [ns (or (the-ns ns-sym) (throw [:pixie.stdlib/NamespaceNotFoundException
                                       (str "No such namespace: " ns-sym)]))
        filters (apply hashmap filters)
        rename (or (:rename filters) {})
        exclude (:exclude filters)
        rname (or (:as filters)
                  ns-sym)]
    (-add-refer from-ns ns-sym rname)
    (if (= :all (:refer filters))
      (-refer-all from-ns rname)
      (doseq [sym (:refer filters)]
        (-add-refer from-ns rname sym sym)))

    (doseq [[from to] (:rename filters)]
      (-add-refer from-ns rname from to))

    (doseq [nm (:exclude filters)]
      (-add-exclude from-ns rname nm))
    
    nil))


(defn load-ns [ns-sym]
  (assert (not (namespace ns-sym)) "Namespace names must not be namespaced")
  (or (the-ns ns-sym)
      (load-file ns-sym)))

;; End NS Functions

;; Delay

(deftype Delay [f val]
  (-deref [this]
    (when f
      (set-field! :val (f))
      (set-field! :f nil))
    val))

(defn -delay [f]
  (->Delay f nil))

;; End Delay 

;; Dynamic Vars

(defeffect EDynamicVarEnv
  (-dynamic-var-get [this var])
  (-dynamic-var-set [this var val])
  (-dynamic-get-vars [this])
  (-dynamic-set-vars [this s']))

(deftype DynamicVar [x]
  IEffect
  (-effect-val [this y]
    (fn val-fn [s] y))
  
  (-effect-finally [this f]
    (f x))

  EDynamicVarEnv
  (-dynamic-var-get [this var k]
    (fn lookup-fn [s]
      ((k (get s var)) s)))

  (-dynamic-var-set [this var val k]
    (fn [s]
      ((k nil) (assoc s var val))))
  
  (-dynamic-get-vars [this k]
    (fn [s]
      ((k s) s)))

  (-dynamic-set-vars [this s' k]
    (fn set-vars [s]
      ((k nil) s'))))


(def dynamic-var-handler (->DynamicVar {}))





 
;; LibC Stuff
(def load-paths (atom ["." ""]))

(defn ffi-library [nm]
  (reduce
   (fn [_ x]
     (when-let [l (-ffi-library (str x (name nm)))]
       (reduced l)))
   nil
   @load-paths))


(def libc (ffi-library pixie.platform/lib-c-name))


;;



;; Mutimethods

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

(deftype MultiMethod [dispatch-fn default-val methods]
  IFn
  (-invoke [self & args]
    (let [dispatch-val (apply dispatch-fn args)
          method (or (get @methods dispatch-val)
                     (get @methods default-val))
          _ (assert method (str "no method defined for " dispatch-val))]
      (apply method args))))


;; End Multimethods

(def gensym-state (atom 0))
(defn gensym
  ([] (gensym "auto_"))
  ([prefix] (symbol (str prefix (swap! gensym-state inc)))))


;; Macros 

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
        decls (seq (map (fn [[argv & body]]
                          (let [names (vec (map #(if (= % '&) '& (gensym "arg__")) argv))
                                bindings (loop [i 0 bindings []]
                                           (if (< i (count argv))
                                             (if (= (nth argv i) '&)
                                               (recur (inc i) bindings)
                                               (recur (inc i) (reduce conj bindings [(nth argv i) (nth names i)])))
                                             bindings))]
                            (if (every? symbol? argv)
                              `(~argv ~@body)
                              `(~names
                                (let ~bindings
                                  ~@body)))))
                        decls))]
    (if (= (count decls) 1)
      `(fn* ~@name ~(first (first decls)) ~@(next (first decls)))
      `(fn* ~@name ~@decls))))


(defmacro defn ^{:doc "Defines a new function."
                 :signatures [[nm doc? meta? & body]]}
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
    `(def ~nm (fn ~nm ~@rest))))


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
  (let* [destructured-bindings (transduce (map (fn let-foo [args]
                                                 (assert (= 2 (count args)) (str "Bindings must be in pairs, not " args
                                                                                 " " (meta (first args))))
                                                 (apply destructure args)))
                                          concat
                                          []
                                          (partition 2 bindings))]
        `(let* ~destructured-bindings
               ~@body)))

;; State

(defeffect EState
  (-state-lookup [this k])
  (-state-update [this key f args]))

(deftype State [x]
  IEffect
  (-effect-val [this y]
    (fn val-fn [s] y))
  
  (-effect-finally [this f]
    (f x))

  EState
  (-state-lookup [this key k]
    (fn lookup-fn [s]
      ((k (get s key)) s)))

  (-state-update [this key f args k]
    (fn [s]
      (let [new-state (assoc s key (apply f (get s key) args))]
        ((k nil) new-state))))


  ILookup
  (-val-at [this k]
    (-sate-lookup this k)))

(defn state
  ([]
   (state {}))
  ([s]
   (->State s)))

(defn update [s k f & args]
  (-state-update s k v))

(defmacro with-state [[n] & body]
  `(with-handler [~n (state)]
     ~@body))


