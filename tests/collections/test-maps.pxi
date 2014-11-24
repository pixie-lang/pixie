(ns collections.test-maps
  (require pixie.test :as t))

(t/deftest maps-contains
  (let [m {:a 1, :b 2, :c 3}
        c [:a :b :c]
        n [:d 'a 1]]
    (foreach [c c]
             (t/assert= (contains? m c) true))
    (foreach [n n]
             (t/assert= (contains? m c) false))))

(t/deftest map-equals
  (let [m {:a 1, :b 2, :c 3}]
    (t/assert= (-eq {} {}) true)
    (t/assert= (-eq m m) true)
    (t/assert= (-eq m {:a 1, :b 2, :c 3}) true)

    (t/assert= (-eq m {}) false)

    (t/assert= (-eq m {:a 1, :b 2}) false)
    (t/assert= (-eq m [[:a 1] [:b 2] [:c 3]]) false)

    (t/assert= (-eq m {:a 1, :b 2, :c 4}) false)
    (t/assert= (-eq m {:a 3, :b 2, :c 1}) false)))


(t/deftest map-val-at-and-invoke
  (let [m {:a 1, :b 2, :c 3}]
    (foreach [e m]
             (t/assert= (get m (key e)) (val e))
             (t/assert= (m (key e)) (val e)))
    (t/assert= (get m :d) nil)
    (t/assert= (m :d) nil)))

(t/deftest map-without
  (let [m {:a 1 :b 2}]
    (t/assert= m m)
    (t/assert= (dissoc m :a) {:b 2})
    (t/assert= (dissoc m :a :b) {})))

(t/deftest map-conj
  (let [m {:a 1 :b 2}]
    (t/assert= m m)
    ;; Should conj vector of length 2
    (t/assert= (conj m [:c 3]) {:a 1 :b 2 :c 3})
    (t/assert= (conj m [:b 4]) {:a 1 :b 4})
    (t/assert= (conj m [:b 4] [:c 5]) {:a 1 :b 4 :c 5})

    ;; Should conj sequences of pairs
    (t/assert= (conj {} '([:a 1] [:b 2] [:c 3])) {:a 1 :b 2 :c 3})

    ;; Should conj sequences of MapEntries
    (t/assert= (conj {} (seq {:a 1 :b 2 :c 3})) {:a 1 :b 2 :c 3})))
