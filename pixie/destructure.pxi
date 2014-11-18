;(ns pixie.destructure)

(defn nnext [coll]
  (next (next coll)))

(defn nthnext [coll n]
  (loop [n n
         xs (seq coll)]
    (if (and xs (pos? n))
      (recur (dec n) (next xs))
      xs)))

(defn destructure [binding expr]
  (cond
   (symbol? binding) [binding expr]
   (vector? binding) (let [name (gensym "vec__")]
                       (reduce conj [name expr]
                               (destructure-vector binding name)))
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
