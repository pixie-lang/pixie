(ns pixie.tests.collections.test-vectors
  (require pixie.test :as t))

(def MAX-SIZE 1064)

(comment
;; Takes forever in interpreted mode but useful for debugging
(t/deftest vector-creation
  (loop [acc []]
    (if (= (count acc) MAX-SIZE)
      acc
      (do (dotimes [j (count acc)]
            (t/assert= j (nth acc j)))
          (recur (conj acc (count acc)))))))
)
(t/deftest vector-contains
  (let [v [1 2 3]
        c [0 1 2]
        n [-1 3]]
    (foreach [c c]
             (t/assert= (contains? v c) true))
    (foreach [n n]
             (t/assert= (contains? v n) false))))

(t/deftest vector-equals
  (let [v [1 2 3]]
    (t/assert= [] '())
    (t/assert= v v)
    (t/assert= v [1 2 3])
    (t/assert= v '(1 2 3))

    (t/assert= (= [] nil) false)
    (t/assert= (= v []) false)
    (t/assert= (= v [1 2]) false)
    (t/assert= (= v [1 2 3 4]) false)
    (t/assert= (= v '(1 2)) false)
    (t/assert= (= v '(1 2 3 4)) false)))

(t/deftest vector-conj
  (t/assert= [1 2] (conj [1] 2))
  (t/assert= [1 2 3 4] (conj [1] 2 3 4)))

(t/deftest vector-conj!
  (t/assert= [1 2] (persistent! (conj! (transient [1]) 2)))
  (t/assert= [1 2 3] (persistent! (conj! (transient [1]) 2 3))))

(t/deftest vector-push!
  (t/assert= [1] (persistent! (push! (transient []) 1)))
  (t/assert= [1 2] (persistent! (push! (transient [1]) 2))))

(t/deftest vector-pop!
  (t/assert= [] (persistent! (pop! (transient [1]))))
  (t/assert= [1] (persistent! (pop! (transient [1 2]))))
  (t/assert= [1 2] (persistent! (pop! (transient [1 2 3])))))
