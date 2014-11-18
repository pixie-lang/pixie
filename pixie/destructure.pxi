;(ns pixie.destructure)

(defmacro when-let [binding & body]
  `(let ~binding
     (when ~(first binding)
       ~@body)))

(defn nnext [coll]
  (next (next coll)))

(defn nthnext [coll n]
  (loop [n n
         xs (seq coll)]
    (if (and xs (pos? n))
      (recur (dec n) (next xs))
      xs)))

(defn take [n coll]
  (when (pos? n)
    (when-let [s (seq coll)]
      (cons (first s) (take (dec n) (next s))))))

(defn drop [n coll]
  (let [s (seq coll)]
    (if (and (pos? n) s)
      (recur (dec n) (next s))
      s)))

(defn partition
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
                      (reduce conj res (destructure (first bindings) `(nth ~expr ~i))))))
      res)))

(defn destructure-map [binding-map expr]
  (loop [bindings (seq binding-map)
         res []]
    (if bindings
      (let [binding (key (first bindings))
            binding-key (val (first bindings))]
        (recur (next bindings)
               (reduce conj res (destructure binding `(get ~expr ~binding-key)))))
      res)))

(defmacro let+ [bindings & body]
  (let [destructured-bindings (transduce (map #(apply destructure %1)) concat [] (partition 2 bindings))]
    `(let ~destructured-bindings
       ~@body)))
