(ns pixie.tests.test-ith
  (require pixie.test :as t))

(t/deftest test-ith
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (t/assert= (ith [1 2 3 4 5] 0) 1)
    (t/assert= (ith v 0) 1)
    (t/assert= (ith v 0) (nth v 0))
    ))

(t/deftest test-ith-nil
  (t/assert= (ith nil 0) nil)
  (t/assert= (ith nil 1) nil)
  (t/assert= (ith nil -1) nil)
  )
(comment
(t/deftest test-ith-empty-always-oob
  (t/assert= "Index out of bounds" (try (ith [] 0)           (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith [] 1)           (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith [] -1)          (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith '() 0)          (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith '() 1)          (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith '() -1)         (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith (range 0 0) 0)  (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith (range 0 0) 1)  (catch e (ex-msg e))))
  (t/assert= "Index out of bounds" (try (ith (range 0 0) -1) (catch e (ex-msg e))))
  )

(t/deftest test-ith-out-of-bounds
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (comment ">= 5 s/b oob")
    (t/assert= "Index out of bounds" (try (ith v  5) (catch e (ex-msg e))))
    (t/assert= "Index out of bounds" (try (ith l  5) (catch e (ex-msg e))))
    (t/assert= "Index out of bounds" (try (ith r  5) (catch e (ex-msg e))))
    (comment "< -5 s/b oob")
    (t/assert= "Index out of bounds" (try (ith v -6) (catch e (ex-msg e))))
    (t/assert= "Index out of bounds" (try (ith l -6) (catch e (ex-msg e))))
    (t/assert= "Index out of bounds" (try (ith r -6) (catch e (ex-msg e))))
    )
  )
)
(t/deftest test-ith-explicit
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]

    (t/assert= (ith v 1) (nth v 1))
    (t/assert= (ith l 1) (nth l 1))
    (t/assert= (ith r 1) (nth r 1))

    (t/assert= (ith r 0) (nth r 0))
    (t/assert= (ith l 0) (nth l 0))
    (t/assert= (ith v 0) (nth v 0))

    (t/assert= (ith v 2) (nth v 2))
    (t/assert= (ith l 2) (nth l 2))
    (t/assert= (ith r 2) (nth r 2))

    (t/assert= (ith v 3) (nth v 3))
    (t/assert= (ith l 3) (nth l 3))
    (t/assert= (ith r 3) (nth r 3))

    (t/assert= (ith v 4) (nth v 4))
    (t/assert= (ith l 4) (nth l 4))
    (t/assert= (ith r 4) (nth r 4))

    (t/assert= (ith v -5) (nth v 0))
    (t/assert= (ith l -5) (nth l 0))
    (t/assert= (ith r -5) (nth r 0))

    (t/assert= (ith v -4) (nth v 1))
    (t/assert= (ith l -4) (nth l 1))
    (t/assert= (ith r -4) (nth r 1))

    (t/assert= (ith v -3) (nth v 2))
    (t/assert= (ith l -3) (nth l 2))
    (t/assert= (ith r -3) (nth r 2))

    (t/assert= (ith v -2) (nth v 3))
    (t/assert= (ith l -2) (nth l 3))
    (t/assert= (ith r -2) (nth r 3))

    (t/assert= (ith v -1) (nth v 4))
    (t/assert= (ith l -1) (nth l 4))
    (t/assert= (ith r -1) (nth r 4))

    ))

(t/deftest test-ith-doseq
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (doseq [i (range 0 5)]
      (t/assert= (ith v i) (nth v i))
      (t/assert= (ith l i) (nth l i))
      (t/assert= (ith r i) (nth r i))
      )
    (doseq [i (range -5 0)]
      (t/assert= (ith v i) (nth v (+ 5 i)))
      (t/assert= (ith l i) (nth l (+ 5 i)))
      (t/assert= (ith r i) (nth r (+ 5 i)))
      )
    ))

