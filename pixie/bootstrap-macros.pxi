(ns pixie.bootstrap-macros)

;;
;; 1) The compiler should translate pixie.bootstrap-macros/foo to pixie.stdlib/foo
;; 2) the compiler should allow these macros to override any other macros/locals but only during bootstrap compilation
;;

(defmacro when [test & body]
  `(if ~test (do ~@body)))


(defmacro deftype
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
        all-fields fields
        type-nm (str #_@(:ns env) "." (name nm))
        type-decl `(def ~nm (create-type ~(keyword type-nm)
                                         ~all-fields))
        inst (gensym)
        ctor `(defn ~ctor-name ~field-syms
                (new ~nm
                     ~@field-syms))
        proto-bodies (transduce
                      (map (fn [body]
                             (cond
                               (symbol? body) `(satisfy ~body ~nm)
                               (seq? body) `(extend ~(first body)
                                              ~(symbol (str #_@(:ns env) "/" nm))
                                              ~(mk-body body))
                               :else (assert false "Unknown body element in deftype, expected symbol or seq"))))
                      conj
                      body)]
    `(do ~type-decl
         ~ctor
         ~@proto-bodies)))

(defmacro defprotocol
  [nm & sigs]
  `(do (def ~nm (~'pixie.stdlib/protocol ~(str nm)))
       ~@(map (fn [[x]]
                `(def ~x (~'pixie.stdlib/polymorphic-fn ~(str x) ~nm)))
              sigs)))


(defmacro ns [nm & body]
  (let [bmap (reduce (fn [m b]
                       (update-in m [(first b)] (fnil conj []) (rest b)))
                     {}
                     body)
        requires
        (do
          (assert (>= 1 (count (:require bmap)))
                  "Only one :require block can be defined per namespace")
          (mapv (fn [r] `(require ~(keyword (name nm)) ~@r)) (first (:require bmap))))]
    `(do (in-ns ~(keyword (name nm)))
         ~@requires)))

(defmacro require [ins ns & args]
  `(do (load-ns (quote ~ns))
       (assert (the-ns (quote ~ns))
               (str "Couldn't find the namespace " (quote ~ns) " after loading the file"))

       (apply refer ~ins (quote [~ns ~@args]))))


(defn -make-record-assoc-body [cname fields]
  (let [k-sym (gensym "k")
        v-sym (gensym "v")
        this-sym (gensym "this")
        result `(-assoc [~this-sym ~k-sym ~v-sym]
                 (condp identical? ~k-sym
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
  {:doc "Define a record type.

Similar to `deftype`, but supports construction from a map using `map->Type`
and implements IAssociative, ILookup and IObject."
   :added "0.1"}
  [nm field-syms & body]
  (let [ctor-name (symbol (str "->" (name nm)))
        map-ctor-name (symbol (str "map" (name ctor-name)))
        fields (transduce (map (comp keyword name)) conj field-syms)
        type-from-map `(defn ~map-ctor-name [m]
                         (apply ~ctor-name (map #(get m %) ~fields)))
        default-bodies ['IAssociative
                        (-make-record-assoc-body ctor-name fields)
                        `(-contains-key [self# k#]
                                        (contains? ~(set fields) k#))
                        `(-dissoc [self k]
                                  (throw [:pixie.stdlib/NotImplementedException
                                          "dissoc is not supported on defrecords"]))
                        'ILookup
                        '(-val-at [self# k# not-found#]
                                  (get-field self# k# not-found#))
                        'IObject
                        `(-str [self# sb#]
                               (sb# (str "<" ~(name nm) " >" )))
                        `(-eq [self other]
                              (and (instance? ~nm other)
                                   ~@(map (fn [field]
                                            `(= (. self ~field) (. other ~field)))
                                          fields)))
                        `(-hash [self]
                                (hash [~@field-syms]))]
        deftype-decl `(deftype ~nm ~fields ~@default-bodies ~@body)]
    `(do ~type-from-map
         ~deftype-decl)))
