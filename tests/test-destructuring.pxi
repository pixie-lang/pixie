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
