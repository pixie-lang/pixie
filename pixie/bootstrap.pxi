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
(extend -str Object (fn [x sb]
                      (sb (-internal-to-str x))))
(extend -repr Object (fn [x sb]
                       (sb (-internal-to-repr x))))


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

(defn conj
  ([] [])
  ([coll] coll)
  ([coll itm] (-conj coll itm))
  ([coll item & more]
   (-apply conj (conj x y) more)))


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

(deftype Range [start stop step]
  IReduce
  (-reduce [self f init]
    (loop [i start
           acc init]
      (println i)
      (println acc)
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
  (-eq [this sb]))

(def MAX-NUMBER 0xFFFFFFFF) ;; 32 bits ought to be enough for anyone ;-)

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

;; End Range

;; PersistentVector

(deftype Node [edit array]
  IMessageObject
  (-get-field [this name]
    (get-field this name)))

(defn new-node
  ([edit]
   (new-node edit (array 32)))
  ([edit array]
   (->Node edit array)))

(def EMPTY-NODE (new-node nil))



(defn tailoff [this]
  (let [cnt (.-cnt this)]
    (if (< cnt 32)
      0
      (bit-shift-left (bit-shift-right (dec cnt) 5) 5))))

(defn array-for [this i cnt root shift tail]
      (if (and (<= 0 i) (< i cnt))
        (if (>= i (tailoff this))
          tail
          (.-array ((fn look-deeper [node level]
                      (if (> level 0)
                        (look-deeper (aget (:array node)
                                           (bit-and (bit-shift-right i level) 0x01f))
                                     (- level 5))
                        (:array node)))
                    root
                    shift)))))

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

          (let [new-root (new-node (.-edit root))]
            (aset new-root 0 root)
            (aset new-root 1 (new-path (.-edit root) shift tail-node))
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

  ICounted
  (-count [this] cnt))


(defn push-tail [this level parent tail-node]
  (let [subidx (bit-and (bit-shift-right (dec (.-cnt this)) level) 0x01f)
        ret-array (aclone (.-array parent))
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
    (->Node (.-edit parent) node-to-insert)))

(defn new-path [edit level node]
  (if (= level 0)
    node
    (->Node edit
            (new-path edit (- level 5) node))))


(def EMPTY (->PersistentVector 0 5 EMPTY-NODE (array 0) nil))

(defn vector-from-array [arr]
  (println "Vector for array")
  (println (count arr))
  (if (< (count arr) 32)
    (->PersistentVector (count arr) 5 EMPTY-NODE arr nil)
    (into [] arr)))

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


;;;

(into [] (range 4))

(comment
  (println 42)

  #_(into [] (range 4))


  (println ( (fn [x]
               (assert (< x 0xFFFFFFFF) "Vector too large")

               (if true
                 11
                 2)) 0))

  (println ((fn []
              (if true nil (println 100))
              11)))

  (println 44))
