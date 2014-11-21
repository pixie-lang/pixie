(__ns__ pixie.stdlib)

 (def libc (ffi-library pixie.platform/lib-c-name))
 (def exit (ffi-fn libc "exit" [Integer] Integer))
 (def puts (ffi-fn libc "puts" [String] Integer))

 (def libreadline (ffi-library (str "libreadline." pixie.platform/so-ext)))
 (def readline (ffi-fn libreadline "readline" [String] String))
 (def rand (ffi-fn libc "rand" [Integer] Integer))
 (def srand (ffi-fn libc "srand" [Integer] Integer))

(def reset! -reset!)

(def program-arguments [])



(def conj (fn conj
           ([] [])
           ([result] result)
           ([result item] (-conj result item))))

(def conj! (fn conj!
             ([] (-transient []))
             ([result] (-persistent! result))
             ([result item] (-conj! result item))))

(def disj (fn disj
           ([] [])
           ([result] result)
           ([result item] (-disj result item))))

(def disj! (fn conj!
             ([] (-transient []))
             ([result] (-persistent! result))
             ([result item] (-disj! result item))))

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
               :added "0.1"}
           map
           ([f]
             (fn [xf]
                (fn
                  ([] (xf))
                  ([result] (xf result))
                  ([result item] (xf result (f item))))))
           ([f coll]
              (let [i (iterator coll)]
                (loop []
                  (if (at-end? i)
                    nil
                    (do (yield (f (current i)))
                        (move-next! i)
                        (recur))))))))


(def reduce (fn [rf init col]
              (-reduce col rf init)))

(def into (fn [to from]
            (if (satisfies? IToTransient to)
              (persistent! (reduce conj! (transient to) from))
              (reduce conj to from))))

(def interpose
     (fn interpose [val]
       (fn [xf]
           (let [first? (atom true)]
                (fn
                 ([] (xf))
                 ([result] (xf result))
                 ([result item] (if @first?
                                    (do (reset! first? false)
                                        (xf result item))
                                  (xf (xf result val) item))))))))


(def preserving-reduced
  (fn [rf]
    (fn [a b]
      (let [ret (rf a b)]
        (if (reduced? ret)
          (reduced ret)
          ret)))))

(def cat
  (fn cat [rf]
    (let [rrf (preserving-reduced rf)]
      (fn cat-inner
        ([] (rf))
        ([result] (rf result))
        ([result input]
           (reduce rrf result input))))))


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

(def indexed-reduce (fn indexed-reduce
                      [coll f init]
                      (let [max (count coll)]
                      (loop [init init
                             i 0]
                        (if (reduced? init)
                          @init
                          (if (-eq i max)
                            init
                            (recur (f init (nth coll i)) (+ i 1))))))))

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

(extend -str Bool
  (fn [x]
    (if (identical? x true)
      "true"
      "false")))

(extend -str Nil (fn [x] "nil"))
(extend -reduce Nil (fn [self f init] init))
(extend -hash Nil (fn [self] 100000))

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

(extend -str Cons
  (fn [v]
    (apply str "(" (conj (transduce (interpose " ") conj v) ")"))))

(extend -hash Cons
        (fn [v]
          (transduce ordered-hash-reducing-fn v)))

(extend -str PersistentList
  (fn [v]
    (apply str "(" (conj (transduce (interpose " ") conj v) ")"))))

(extend -str LazySeq
  (fn [v]
    (apply str "(" (conj (transduce (interpose " ") conj v) ")"))))

(extend -hash PersistentVector
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))

(extend -hash PersistentHashSet
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))

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

(def sequence
  (fn
    ([data]
       (let [f (create-stacklet
                 (fn [h]
                   (reduce (fn ([h item] (h item) h)) h data)))]
          (stacklet->lazy-seq f)))
    ([xform data]
        (let [f (create-stacklet
                 (fn [h]
                   (transduce xform
                              (fn ([] h)
                                ([h item] (h item) h)
                                ([h] nil))
                              data)))]
          (stacklet->lazy-seq f)))))


(extend -seq PersistentVector sequence)
(extend -seq Array sequence)



(def concat (fn [& args] (transduce cat conj args)))

(def key (fn [x] (-key x)))
(def val (fn [x] (-val x)))

(def defn (fn [nm & rest]
            (let [meta (if (instance? String (first rest))
                         {:doc (first rest)}
                         {})
                  rest (if (instance? String (first rest)) (next rest) rest)
                  meta (if (satisfies? IMap (first rest))
                         (merge meta (first rest))
                         meta)
                  rest (if (satisfies? IMap (first rest)) (next rest) rest)
                  nm (with-meta nm meta)]
              `(def ~nm (fn ~nm ~@rest)))))
(set-macro! defn)

(defn defmacro [nm & rest]
  `(do (defn ~nm ~@rest)
       (set-macro! ~nm)
       ~nm))

(set-macro! defmacro)

(defmacro ->
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
   :signatures [[arg]]
   :added "0.1"}
  [x]
  (if x false true))

(defn +
  {:doc "Adds the arguments"
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

(defn first
  {:doc "Returns the first item in coll, if coll implements IIndexed nth will be used to retreive
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 0)
    (-first coll)))

(defn second
  {:doc "Returns the second item in coll, if coll implements IIndexed nth will be used to retreive
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 1)
    (first (next coll))))

(defn third
  {:doc "Returns the third item in coll, if coll implements IIndexed nth will be used to retreive
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 2)
    (first (next (next coll)))))

(defn fourth
  {:doc "Returns the fourth item in coll, if coll implements IIndexed nth will be used to retreive
         the item from the collection."
   :signatures [[coll]]
   :added "0.1"}
  [coll]
  (if (satisfies? IIndexed coll)
    (nth coll 3)
    (first (next (next (next coll))))))

(defn assoc
  ([m] m)
  ([m k v]
     (-assoc m k v))
  ([m k v & rest]
     (apply assoc (-assoc m k v) rest)))

(defn dissoc
  ([m] m)
  ([m & ks]
    (reduce -dissoc m ks)))

(defn contains? [coll key]
  (-contains-key coll key))

(defn get-val [inst]
  (get-field inst :val))

(defn comp
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

(defn string? [v] (instance? String v))
(defn keyword? [v] (instance? Keyword v))

(defn list? [v] (instance? PersistentList v))
(defn map? [v] (satisfies? IMap v))
(defn fn? [v] (satisfies? IFn v))

(defn indexed? [v] (satisfies? IIndexed v))
(defn counted? [v] (satisfies? ICounted v))

(defn last [coll]
  (if (next coll)
    (recur (next coll))
    (first coll)))

(defn butlast [coll]
  (loop [res []
         coll coll]
    (if (next coll)
      (recur (conj res (first coll)) (next coll))
      (seq res))))

(extend -count MapEntry (fn [self] 2))
(extend -nth MapEntry (fn [self idx not-found]
                          (cond (= idx 0) (-key self)
                                (= idx 1) (-val self)
                                :else not-found)))

(extend -reduce MapEntry indexed-reduce)

(extend -str MapEntry
        (fn [v]
            (apply str "[" (conj (transduce (interpose " ") conj v) "]"))))

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

(extend -hash PersistentHashMap
        (fn [v]
          (transduce cat unordered-hash-reducing-fn v)))

(extend -seq PersistentHashSet sequence)

(extend -str PersistentHashSet
        (fn [s]
          (apply str "#{" (conj (transduce (interpose " ") conj s) "}"))))

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
                 (assoc coll (nth x 0) (nth x 1))
                 (throw "Vector arg to map conj must be a pair"))
             
             (satisfies? ISeqable x)
             (reduce conj coll (-seq x))

             :else
             (throw (str (type x) " cannot be conjed to a map")))))
 
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

(extend -invoke Keyword (fn [k m] (-val-at m k nil)))
(extend -invoke PersistentHashMap (fn [m k] (-val-at m k nil)))
(extend -invoke PersistentHashSet (fn [m k] (-val-at m k nil)))

(defn get
  ([mp k]
     (get mp k nil))
  ([mp k not-found]
     (-val-at mp k not-found)))

(defn get-in
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
  ([m ks v]
     (let [ks (seq ks)
           k  (first ks)
           ks (next ks)]
       (if ks
         (assoc m k (assoc-in (get m k) ks v))
         (assoc m k v)))))

(def subs pixie.string/substring)

(defmacro assert
  ([test]
     `(if ~test
        nil
        (throw "Assert failed")))
  ([test msg]
     `(if ~test
        nil
        (throw (str "Assert failed " ~msg)))))

(defmacro resolve [sym]
  `(resolve-in (this-ns-name) ~sym))

(defmacro with-bindings [binds & body]
  `(do (push-binding-frame!)
       (reduce (fn [_ map-entry]
                 (set! (resolve (key map-entry)) (val map-entry)))
               nil
               (apply hashmap ~@binds))
       (let [ret (do ~@body)]
         (pop-binding-frame!)
         ret)))

(def foo 42)
(set-dynamic! (resolve 'pixie.stdlib/foo))

(defmacro require [ns kw as-nm]
  (assert (= kw :as) "Require expects :as as the second argument")
  `(do (load-ns (quote ~ns))
       (refer-ns (this-ns-name) (the-ns (quote ~ns)) (quote ~as-nm))))

(defmacro ns [nm & body]
  `(do (__ns__ ~nm)
       ~@body))


(defn symbol? [x]
  (identical? Symbol (type x)))


(defmacro lazy-seq [& body]
  `(lazy-seq* (fn [] ~@body)))

(def Protocol @(resolve (symbol "/Protocol")))

(defn protocol? [x]
  (instance? Protocol x))

(defmacro deftype [nm fields & body]
  (let [ctor-name (symbol (str "->" (name nm)))
        fields (transduce (map (comp keyword name)) conj fields)
        field-syms (transduce (map (comp symbol name)) conj fields)
        mk-body (fn [body]
                  (let [fn-name (first body)
                        _ (assert (symbol? fn-name) "protocol override must have a name")
                        args (second body)
                        _ (assert (vector? args) "protocol override must have arguments")
                        self-arg (first args)
                        _ (assert (symbol? self-arg) "protocol override must have at least one `self' argument")
                        field-lets (transduce (comp (map (fn [f]
                                                           [(symbol (name f)) (list 'get-field self-arg f)]))
                                                    cat)
                                              conj fields)
                        rest (next (next body))]
                    `(fn ~fn-name ~args (let ~field-lets ~@rest))))
        bodies (reduce
                (fn [res body]
                  (cond
                   (symbol? body) (cond
                                   (= body 'Object) [body (second res) (third res)]
                                   (protocol? @(resolve body)) [@(resolve body) (second res) (conj (third res) body)]
                                   :else (throw (str "can only extend protocols or Object, not " body)))
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
                (let [~inst (new ~nm)]
                  ~@(transduce
                     (map (fn [field]
                            `(set-field! ~inst ~field ~(symbol (name field)))))
                     conj
                     fields)
                  ~@(transduce
                     (map (fn [type-body]
                            `(set-field! ~inst ~(keyword (name (first type-body))) ~(mk-body type-body))))
                     conj
                     type-bodies)
                  ~inst))
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

(defmacro defrecord [nm fields & body]
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

 (def libc (ffi-library pixie.platform/lib-c-name))
 (def exit (ffi-fn libc "exit" [Integer] Integer))
 (def puts (ffi-fn libc "puts" [String] Integer))
 (def printf (ffi-fn libc "printf" [String] Integer))
 (def getenv (ffi-fn libc "getenv" [String] String))

(defn print [& args]
  (puts (apply str args)))


(defn doc [x]
  (get (meta x) :doc))

(defn swap! [a f & args]
  (reset! a (apply f @a args)))

(defn update-in
  [m ks f & args]
  (let [f (fn [m] (apply f m args))
        update-inner-f (fn update-inner-f
                         ([m f k]
                            (assoc m k (f (get m k))))
                         ([m f k & ks]
                            (assoc m k (apply update-inner-f m f ks))))]
    (apply update-inner-f m f ks)))

(defn nil? [x]
  (identical? x nil))

(defn fnil [f else]
  (fn [x & args]
    (apply f (if (nil? x) else x) args)))

(defmacro foreach [binding & body]
  (assert (= 2 (count binding)) "binding and collection required")
  `(reduce
    (fn [_ ~ (nth binding 0)]
        ~@body
        nil)
    nil
    ~(nth binding 1)))

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


(defmacro dotimes [bind & body]
  (let [b (nth bind 0)]
    `(let [max# ~(nth bind 1)]
       (loop [~b 0]
         (if (= ~b max#)
           nil
           (do ~@body
               (recur (inc ~b))))))))

(extend -iterator PersistentVector
        (fn [v]
          (dotimes [x (count v)]
            (yield (nth v x)))))

(defmacro and
  ([] true)
  ([x] x)
  ([x y] `(if ~x ~y false))
  ([x y & more] `(if ~x (and ~y ~@more))))

(defmacro or
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

(defn abs [x]
  (if (< x 0)
    (* -1 x)
    x))

(deftype Range [:start :stop :step]
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
    (let [cmp (if (< start stop) < >)
          val (+ start (* idx step))]
      (if (cmp val stop)
        val
        nil))))




(defn range
  ([] (->Range 0 MAX-NUMBER 1))
  ([stop] (->Range 0 stop 1))
  ([start stop] (->Range start stop 1))
  ([start stop step] (->Range start stop step)))

(defn iterator [coll]
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

(defn filter [f]
  (fn [xf]
    (fn
      ([] (xf))
      ([acc] (xf acc))
      ([acc i] (if (f i)
                 (xf acc i)
                 acc)))))

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

(defn refer [ns-sym & filters]
  (let [ns (or (the-ns ns-sym) (throw (str "No such namespace: " ns-sym)))
        filters (apply hashmap filters)
        nsmap (ns-map ns)
        rename (or (:rename filters) {})
        exclude (set (:exclude filters))
        refers (if (= :all (:refer filters))
                 (keys nsmap)
                 (or (:refer filters) (:only filters) (keys nsmap)))]
    (when (and refers (not (satisfies? ISeqable refers)))
      (throw ":only/:refer must be a collection of symbols"))
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


(defn vec
  {:doc "Converts a reducable collection into a vector using the (optional) transducer."
   :signatures [[coll] [xform coll]]
   :added "0.1"}
  ([coll]
     (transduce conj! coll))
  ([xform coll]
     (transduce xform conj! coll)))
