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
  (-get [this]))

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

(defprotocol ITransientStack
  (-push! [this x])
  (-pop! [this]))

(defprotocol IDisposable
  (-dispose! [this]))

(defprotocol IMessageObject
  (-get-field [this name])
  (-invoke-method [this name args]))



(extend -get-field Object -internal-get-field)


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

(defn not
  [x]
  (if x false true))

(defn not=
  ([& args]
   (not (-apply = args))))

(defn nil?
  [x]
  (identical? x nil))

(defn conj
  ([] [])
  ([coll] coll)
  ([coll itm] (-conj coll itm))
  ([coll item & more]
   (-apply conj (conj x y) more)))

(defn pop
  ([] [])
  ([coll] (-pop coll)))

(defn nth
  {:doc "Returns the element at the idx.  If the index is not found it will return an error.
         However, if you specify a not-found parameter, it will substitute that instead"
   :signatures [[coll idx] [coll idx not-found]]
   :added "0.1"}
  ([coll idx] (-nth coll idx))
  ([coll idx not-found] (-nth-not-found coll idx not-found)))


(defn count
  ([coll] (-count coll)))


(deftype Cons [first next meta]
  ISeq
  (-first [this] first)
  (-next [this] next)
  ISeqable
  (-seq [this] this)
  IMeta
  (-meta [this] meta)
  (-with-meta [this new-meta]
    (->Cons first next new-meta)))

(defn cons [head tail]
  (->Cons head (seq tail) nil))

;; String Builder

(defn string-builder
  ([] (-string-builder))
  ([sb] (-str sb))
  ([sb x]
   (if (instance? String x)
     (-add-to-string-builder x)
     (-add-to-string-bulder (-str x)))))

(defn str [& args]
  (transduce
   (map str)
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

;; Type Helpers


(defn instance?
  ^{:doc "Checks if x is an instance of t.
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

;; End Type Helpers

;; Reduced

(deftype Reduced [x]
  IDeref
  (-deref [this] x))

(defn reduced [x]
  (->Reduced x))

(defn reduced? [x]
  (instance? Reduced x))

;; End Reduced

;; Satisfies

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

;; End Satisfies

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
   (reduce rf (rf) col))
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
     (map (fn [args] (apply f args)) (step colls)))))

;; End Basic Transudcer Support

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



(defn tailoff [this]
  (let [cnt (.-cnt this)]
    (if (< cnt 32)
      0
      (bit-shift-left (bit-shift-right (dec cnt) 5) 5))))

(defn array-for [this i]
  (if (and (<= 0 i) (< i (.-cnt this)))
    (if (>= i (tailoff this))
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

(deftype PersistentVector [cnt shift root tail meta]
  IMessageObject
  (-get-field [this name]
    (get-field this name))
  
  IPersistentCollection
  (-conj [this val]
    (assert (< cnt 0xFFFFFFFF) "Vector too large")

    (if (< (- cnt (tailoff this)) 32)
      (let [new-tail (array-append tail val)]
        (->PersistentVector (inc cnt) shift root new-tail meta))
      
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
                                meta))
          (let [new-root (push-tail this shift root tail-node)]
            (->PersistentVector (inc cnt)
                                shift
                                new-root
                                (array val)
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
  (-get [this val]
    (-nth-not-found self val nil))
  

  ICounted
  (-count [this] cnt)

  IPop
  (-pop [this]
    (assert (not= cnt 0) "Can't pop an empty vector")

    (if (= cnt 1)
      EMPTY
      (if (> (- cnt (tailoff this)) 1)
        (let [size (dec (count tail))
              new-tail (array-resize tail size)]
          (->PersistentVector (dec cnt)
                              shift
                              root
                              new-tail
                              meta))
        (let [new-tail (array-for this (- cnt 2))
              new-root (pop-tail this shift root)]
          (cond
            (nil? new-root)
            (->PersisentVector (dec cnt)
                               shift
                               EMPTY-NODE
                               new-tail
                               meta)
            (and (> shift 5)
                 (nil? (aget (.-array new-root) 1)))
            (->PersistentVector (dec cnt)
                                (- shift 5)
                                (aget (.-array new-root) 0)
                                new-tail
                                meta)

            :else
            (->PersistentVector (dec cnt)
                                shift
                                new-root
                                new-tail
                                meta))))))

  IAssociative
  (-assoc [this k v]
    (assert (int? k) "Vectors expect ints as keys")
    (if (and (>= idx 0)
             (< idx cnt))
      (if (>= idx (tail-off this))
        (let [new-tail (array-clone tail)]
          (aset new-tail (bit-and idx 0x01f) val)
          (->PersistentVector cnt shift root new-tail meta))
        (->PersistentVector cnt shift (do-assoc shift root idx val) tail meta))
      (if (= idx cnt)
        (-conj this val)
        (throw [:pixie.stdlib/IndexOutOfRange
                "Can only assoc to the end or the contents of a vector"])))))

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


(def EMPTY (->PersistentVector 0 5 EMPTY-NODE (array 0) nil))

(defn vector-from-array [arr]
  (if (< (count arr) 32)
    (->PersistentVector (count arr) 5 EMPTY-NODE arr nil)
    (into [] arr)))

(in-ns :pixie.stdlib)

;; Extend Array

(extend-type Array
  IPersistentCollection
  (-conj [arr itm]
    (conj (vector-from-array arr) itm))
  
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
          acc)))))

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

;;;


(println (count (reduce
               (fn [acc _]
                 (pop acc))
               
               (into [] (range 1024))
               (range 1024))))
