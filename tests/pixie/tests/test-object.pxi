(ns pixie.tests.test-object
  (require pixie.test :as t))

(t/deftest test-hash
  (t/assert= (hash (var foo)) (hash (var foo)))
  (t/assert  (not= (hash (var foo)) (hash (var bar)))))


(deftype FooType [])

(t/deftest test-everything-is-an-object
  (t/assert (instance? Object 42))
  (t/assert (instance? Object []))
  (t/assert (instance? Object "Foo"))
  (t/assert (instance? Object FooType)))
