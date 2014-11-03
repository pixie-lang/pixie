(ns collections.test-sets
  (require pixie.test :as t))

(t/deftest test-count
  (t/assert= (count (set [])) 0)
  (t/assert= (count (set [1 2 3])) 3)
  (t/assert= (count (set [1 1 2 1])) 2))
    
(t/deftest test-contains
  (let [s #{1 2 3}
        c [1 2 3]
        n [-1 0 4]]
    (foreach [c c]
             (t/assert= (contains? s c) true))
    (foreach [n n]
             (t/assert= (contains? s n) false))))
