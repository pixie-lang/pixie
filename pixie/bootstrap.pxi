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

(defprotocol IOpaqueObject
  (-get-field [this name])
  (-invoke-method [this name args]))

(comment
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

  (defn +
    ([] 0)
    ([x] x)
    ([x y] (-add x y))
    ([x y & more]
     (-apply + (+ x y) more))))


;; PersistentVector

(comment
  (deftype PersistentVectorNode [edit array])

  (defn persistent-vector-node
    ([edit]
     (persistent-vector-node edit (array 32)))
    ([edit array]
     (->PersistentVectorNode edit array)))

  (def EMPTY_NODE (persistent-vector-node nil))

  
)

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
