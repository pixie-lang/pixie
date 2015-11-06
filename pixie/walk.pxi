(ns pixie.walk)

(defprotocol IWalk
  (-walk [x f]))

(extend-protocol IWalk
  PersistentList
  (-walk [x f]
    (apply list (map f x)))

  Cons
  (-walk [x f]
    (cons (f (first x)) (map f (next x))))

  IMapEntry
  (-walk [x f]
    (map-entry (f (key x)) (f (val x))))

  PersistentVector
  (-walk [x f]
    (into [] (map f) x))

  PersistentHashSet
  (-walk [x f]
    (into #{} (map f) x))

  PersistentHashMap
  (-walk [x f]
    (into {} (map f) x))

  IRecord
  (-walk [x f]
    (into x (map f) x))

  ISeqable
  (-walk [x f]
    (map f x))

  IObject
  (-walk [x f] x)

  Nil
  (-walk [x f] nil))

(defn walk
  {:doc "Traverses form, an arbitrary data structure.  f is a
  function.  Applies f to each element of form, building up a data
  structure of the same type.  Recognizes all Pixie data
  structures. Consumes seqs."
   :signatures [[f x]]
   :added "0.1"}
  [f x]
  (-walk x f))

(defn postwalk
  {:doc "Performs a depth-first, post-order traversal of form.  Calls f on
  each sub-form, uses f's return value in place of the original.
  Recognizes all Pixie data structures."
   :signatures [[f x]]
   :added "0.1"}
  [f x]
  (f (walk (partial postwalk f) x)))

(defn prewalk
  {:doc "Like postwalk, but does pre-order traversal."
   :added "0.1"}
  [f x]
  (walk (partial prewalk f) (f x)))

(defn prewalk-replace
  {:doc "Recursively transforms form by replacing
  keys in smap with their values.  Like `replace` but works on
  any data structure.  Does replacement at the root of the tree
  first."
   :signatures [[f x]]
   :added "0.1"}
  [smap x]
  (prewalk (fn [x] (if (contains? smap x) (smap x) x)) x))

(defn postwalk-replace
  {:doc "Recursively transforms form by replacing keys in smap with
  their values.  Like `replace` but works on any data structure.
  Does replacement at the leaves of the tree first."
   :signatures [[smap x]]
   :added "0.1"}
  [smap x]
  (postwalk (fn [x] (if (contains? smap x) (smap x) x)) x))

(defn keywordize-keys
  {:doc "Recursively transforms all map keys from strings to keywords."
   :signatures [[m]]
   :added "0.1"}
  [m]
  (let [f (fn [[k v]] (if (string? k) [(keyword k) v] [k v]))]
    ;; only apply to maps
    (postwalk (fn [x] (if (map? x) (into {} (map f x)) x)) m)))

(defn stringify-keys
  {:doc "Recursively transforms all map keys from keywords to strings."
   :signatures [[m]]
   :added "0.1"}
  [m]
  (let [f (fn [[k v]] (if (keyword? k) [(name k) v] [k v]))]
    ;; only apply to maps
    (postwalk (fn [x] (if (map? x) (into {} (map f x)) x)) m)))

(defn macroexpand-all
  {:doc "Recursively performs all possible macroexpansions in
  form. For development use only."
   :added "0.1"
   :signatures [[x]]}
  [x]
  (prewalk (fn [x] (if (seq? x) (macroexpand-1 x) x)) x))
