(ns pixie.tests.test-keywords
  (require pixie.test :as t))

(t/deftest keyword-invoke
  (let [m {:a 1, :b 2, :c 3}]
    (t/assert= (:a m) 1)
    (t/assert= (:b m) 2)
    (t/assert= (:c m) 3)

    (t/assert= (:d m) nil)))
