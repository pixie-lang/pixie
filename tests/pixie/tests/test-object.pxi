(ns pixie.tests.test-object
  (require pixie.test :as t))

(t/deftest test-hash
  (t/assert= (hash (var foo)) (hash (var foo)))
  (t/assert  (not= (hash (var foo)) (hash (var bar)))))
