(ns pixie.tests.test-ith
  (require pixie.test :as t))

(t/deftest test-ith
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (t/assert= (ith [1 2 3 4 5] 0) 1)
    (t/assert= (ith v 0) 1)
    (t/assert= (ith v 0) (nth v 0))))

(t/deftest test-ith-nil
  (t/assert= (ith nil 0) nil)
  (t/assert= (ith nil 1) nil)
  (t/assert= (ith nil -1) nil))

(t/deftest test-ith-empty-always-oob
  (t/assert= "Index out of Range" (try (ith [] 0)           (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith [] 1)           (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith [] -1)          (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith '() 0)          (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith '() 1)          (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith '() -1)         (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith (range 0 0) 0)  (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith (range 0 0) 1)  (catch e (ex-msg e))))
  (t/assert= "Index out of Range" (try (ith (range 0 0) -1) (catch e (ex-msg e)))))

(t/deftest test-ith-out-of-bounds
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (t/assert= "Index out of Range" (try (ith v  5) (catch e (ex-msg e))))
    (t/assert= "Index out of Range" (try (ith l  5) (catch e (ex-msg e))))
    (t/assert= "Index out of Range" (try (ith r  5) (catch e (ex-msg e))))
    (t/assert= "Index out of Range" (try (ith v -6) (catch e (ex-msg e))))
    (t/assert= "Index out of Range" (try (ith l -6) (catch e (ex-msg e))))
    (t/assert= "Index out of Range" (try (ith r -6) (catch e (ex-msg e))))))

(t/deftest test-ith-doseq
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (doseq [i (range 0 5)]
      (t/assert= (ith v i) (nth v i))
      (t/assert= (ith l i) (nth l i))
      (t/assert= (ith r i) (nth r i)))
    (doseq [i (range -5 0)]
      (t/assert= (ith v i) (nth v (+ 5 i)))
      (t/assert= (ith l i) (nth l (+ 5 i)))
      (t/assert= (ith r i) (nth r (+ 5 i))))))

