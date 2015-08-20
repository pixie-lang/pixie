(ns pixie.tests.test-sort
  (require pixie.test :as t))

(t/deftest test-sort
  (t/assert= (sort [5 2 3 1 4]) [1 2 3 4 5])
  (t/assert= (sort ["d" "c" "b" "a"]) ["a" "b" "c" "d"])
  (t/assert= (sort [1/1 1/2 1/3 1/4]) [1/4 1/3 1/2 1/1]))

(t/deftest test-sort-big
  (t/assert= (sort (range 10000))      (range 10000))
  (t/assert= (sort (range 9999 -1 -1)) (range 10000)))

(t/deftest test-sort-by
  (t/assert= (sort-by first
                      (zipmap (range 4)
                              (range 4)))
             [[0 0]
              [1 1]
              [2 2]
              [3 3]])


  (t/assert= (sort-by second
                      (zipmap (range 4)
                              (range 100 0 -1)))
             [[0 0]
              [1 1]
              [2 2]
              [3 3]]))
