(ns collections.test-sets
  (require pixie.test :as t)
  (require tests.utils :as u))

(def worst-hashers (vec (map u/->WorstHasher) 
                        (range 100)))

(t/deftest test-count
  (t/assert= (count (set [])) 0)
  (t/assert= (count (set [1 2 3])) 3)
  (t/assert= (count (set [1 1 2 1])) 2)
  (t/assert= (count (set worst-hashers)) 100))
    
(t/deftest test-contains
  (let [s #{1 2 3}
        c [1 2 3]
        n [-1 0 4]
        g (set worst-hashers)]
    (foreach [c c]
             (t/assert= (contains? s c) true))
    (foreach [n n]
             (t/assert= (contains? s n) false))
    (foreach [n worst-hashers]
             (t/assert= (contains? g n) true))))

(t/deftest test-conj
  (t/assert= (conj #{}) #{})
  (t/assert= (conj #{1 2} 3) #{1 2 3})
  (t/assert= (reduce conj #{} (range 10)) (set (vec (range 10))))
  (t/assert= (reduce conj #{} worst-hashers) (set worst-hashers)))


(t/deftest test-eq
  (let [s  #{1 2 3}]
    (t/assert= s s)
    (t/assert= s #{1 2 3})
    (t/assert= #{1 2 3} s)

    (t/assert= (= s [1 2 3]) false)
    (t/assert= (= s '(1 2 3)) false)
    (t/assert= (= s #{1 2}) false)
    (t/assert= (= s #{1 2 3 4}) false)))

(t/deftest test-invoke
  (let [s #{1 2 3}]
    (t/assert= (s 1) 1)
    (t/assert= (s 2) 2)
    (t/assert= (s 3) 3)

    (t/assert= (s -1) nil)
    (t/assert= (s 4) nil)))

(t/deftest test-has-meta
  (let [m {:has-meta true}
        s (with-meta #{} m)]
    (t/assert= (meta #{}) nil)
    (t/assert= (meta s) m)))
