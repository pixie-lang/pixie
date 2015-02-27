(ns pixie.tests.test-keywords
  (require pixie.test :as t))

(t/deftest keyword-invoke
  (let [m {:a 1, :b 2, :c 3}]
    (t/assert= (:a m) 1)
    (t/assert= (:b m) 2)
    (t/assert= (:c m) 3)

    (t/assert= (:d m) nil)))

(t/deftest keyword-namespace
  (t/assert= (namespace :foo/bar) "foo")
  (t/assert= (namespace :cat/dog) "cat"))


(t/deftest keyword-equality
  (t/assert= :foo/bar :foo/bar)
  (t/assert= (not= :foo/bar :cat/bar) true)
  (t/assert= (not= :foo/cat :foo/dog) true))

(t/deftest string-to-keyword
  (t/assert= (keyword "foo") :foo)
  (t/assert= (keyword "foo/bar") :foo/bar))
