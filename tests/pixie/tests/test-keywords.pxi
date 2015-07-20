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
  (t/assert= (namespace :cat/dog) "cat")
  (t/assert= (namespace ::foo) "pixie.tests.test-keywords"))

(t/deftest fqd-keywords
  (t/assert-throws? (read-string "::x/bar"))
  (t/assert-throws? (read-string "::a.b/foo"))
  (refer-ns 'my.other.ns 'my.fake.core 'fake)
  (binding [*ns* (the-ns 'my.other.ns)]
    (t/assert= :my.fake.core/foo (read-string "::fake/foo"))
    (t/assert= :my.fake.core/foo (read-string "::my.fake.core/foo"))
    (t/assert-throws? (read-string "::f/foo"))))

(t/deftest keyword-equality
  (t/assert= :foo/bar :foo/bar)
  (t/assert= (not= :foo/bar :cat/bar) true)
  (t/assert= (not= :foo/cat :foo/dog) true))

(t/deftest string-to-keyword
  (t/assert= (keyword "foo") :foo)
  (t/assert= (keyword "foo/bar") :foo/bar)
  (t/assert-throws? (keyword 1))
  (t/assert-throws? (keyword :a))
  (t/assert-throws? (keyword 'a))
  (t/assert-throws? (keyword nil))
  (t/assert-throws? (keyword true)))
