(ns collections.test-sets
  (require pixie.test :as t))

(t/deftest test-count
  (t/assert= (count (set [])) 0)
  (t/assert= (count (set [1 2 3])) 3)
  (t/assert= (count (set [1 1 2 1])) 2))
    
