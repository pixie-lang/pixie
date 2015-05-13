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
  (-str [this])
  (-repr [this]))

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

(defprotocol ITransientStack
  (-push! [this x])
  (-pop! [this]))

(defprotocol IDisposable
  (-dispose! [this]))

(defprotocol IMessageObject
  (-get-field [this name])
  (-invoke-method [this name args]))

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

    (if (< (- cnt (tailoff self)) 32)
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


(def EMPTY (->PersistentVector nil 0 5 EMPTY-NODE (array 0)))


(let [x 4]
  (+ x 1))
