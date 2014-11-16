(ns examples.mu-kanren)

(defn lvar []
  (gensym))

(defn lvar? [x]
  (symbol? x))

(defn walk [s u]
  (let [pr (get s u)]
    (if (lvar? pr)
      (recur s pr)
      pr)
    u))

(defn unify [s u v]
  (let [u (walk s u)
        v (walk s v)]
    (cond
      (and (lvar? u)
           (lvar? v)
           (= u v)) s
      (lvar? u) (assoc s u v)
      (lvar? v) (assoc s v u)
      :else (and (= u v) s))))

(defn == [a b]
  (keep (fn [s] (unify s a b))))


(defn -disj [& xforms]
  (fn [xf]
    (let [xforms (transduce (map (fn [xform]
                                   (xform xf)))
                            conj
                            xforms)]
      (fn
        ([] (xf))
        ([acc] (xf acc))
        ([acc i] (reduce
                  (fn [acc xform]
                    (xform acc i))
                  acc
                  xforms))))))

(defn conde [& goals]
  (apply -disj (map (fn [goals]
                      (apply comp goals))
                    goals)))


"Use transduce to run eagerly"
(transduce (conde
            [(== 'a 42)]
            [ (== 'b 1)])
           conj
           [{}])

"Use sequence to make it lazy (via stacklets)"
(sequence (conde
            [(== 'a 42)]
            [(== 'b 1)])
           [{}])
