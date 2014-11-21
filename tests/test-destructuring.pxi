(ns pixie.test.test-destructuring
  (require pixie.test :as t))

(t/deftest test-let-simple
  (t/assert= (let [x 1 y 2 z 3] [x y z]) [1 2 3])
  (t/assert= (let [x 1 y 2 z 3] [x y z]) (let* [x 1 y 2 z 3] [1 2 3]))

  (t/assert= (let [x 1 x 2] x) 2)
  (t/assert= (let [x 1 y 2 x 3] x) 3)

  (t/assert= (let [x 1] (let [x 2] x)) 2))

(t/deftest test-let-vector-simple
  (t/assert= (let [[x y z] [1 2 3]] [x y z]) [1 2 3])
  (t/assert= (let [[x y z] [1 2 3 4]] [x y z]) [1 2 3])

  (t/assert= (let [[x y z & rest] [1 2 3 4]]
               [x y z rest])
             [1 2 3 '(4)])
  (t/assert= (let [[x y z & rest] [1 2]]
               [x y z rest])
             [1 2 nil nil]))

(t/deftest test-let-vector-nested
  (t/assert= (let [[[x y] z & rest] [[1 2] 3 4]]
               [x y z rest])
             [1 2 3 '(4)])

  (t/assert= (let [[[x [y]] z & rest] [[1 [2 3]] 4 5]]
               [x y z rest])
             [1 2 4 '(5)]))

(t/deftest test-let-vector-rest
  (t/assert= (let [[x y & [z & rest]] [1 2 3 4 5]]
               [x y z rest])
             [1 2 3 '(4 5)]))

(t/deftest test-let-map
  (t/assert= (let [{a :a, b :b, {c :c :as s} :d :as m} {:a 1, :b 2, :d {:c 3}}]
               [a b c s m])
             [1 2 3 {:c 3} {:a 1, :b 2, :d {:c 3}}])

  (t/assert= (let [{:keys [a b c] :as m} {:a 1, :b 2, :c 3, :d 4}]
               [a b c (:d m)])
             [1 2 3 4]))

(t/deftest test-let-map-defaults
  (t/assert= (let [{a :a :or {a 42}} {:a 1}] a) 1)
  (t/assert= (let [{a :a :or {a 42}} {}] a) 42)

  (t/assert= (let [{a :a :or {a 42}} {:a nil}] a) nil)
  (t/assert= (let [{a :a :or {a 42}} {:a false}] a) false)

  (t/assert= (let [{:keys [a], :or {a 42}} {:a 1}] a) 1)
  (t/assert= (let [{:keys [a], :or {a 42}} {}] a) 42))
