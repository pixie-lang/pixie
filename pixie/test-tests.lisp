(ns pixie.test-tests
  (require pixie.test :as t))

(t/deftest foo
  (t/assert= 1 2))

(t/deftest bar
  (t/assert= 1 1))

(t/run-tests)