(ns collections.test-seqables
  (require pixie.test :as t))

(t/deftest test-seq
  (let [l '(1 2 3)
        v [1 2 3]]
    (t/assert= (seq l) '(1 2 3))
    (t/assert= (seq v) [1 2 3])

    (t/assert= (seq nil) nil)
    (t/assert= (seq []) nil)))

(t/deftest test-first
  (let [l '(1 2 3)
        v [1 2 3]]
    (t/assert= (first l) 1)
    (t/assert= (first v) 1)
    (t/assert= (first (seq l)) 1)
    (t/assert= (first (seq v)) 1)))

(t/deftest test-next
  (let [l '(1 2 3)
        v [1 2 3]]
    (t/assert= (next l) '(2 3))
    (t/assert= (next v) '(2 3))
    (t/assert= (next (seq l)) '(2 3))
    (t/assert= (next (seq v)) '(2 3))

    (t/assert= (next (next (next l))) nil)
    (t/assert= (next (next (next v))) nil)))

(t/deftest test-equals
  (let [l '(1 2 3)]
    (t/assert= l l)
    (t/assert= l '(1 2 3))
    (t/assert= l [1 2 3])

    (t/assert= (= l '(1 2 3 4)) false)
    (t/assert= (= l [1 2 3 4]) false)))

(t/deftest test-conj
  (t/assert= '(3 1 2) (conj '(1 2) 3))
  (t/assert= '(5 4 3 1 2) (conj '(1 2) 3 4 5)))
