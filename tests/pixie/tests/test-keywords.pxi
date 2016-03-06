(ns pixie.tests.test-keywords
  (require pixie.test :as t))

(t/deftest keyword-invoke
  (let [m {:a 1, :b 2, :c 3}]
    (t/assert= (:a m) 1)
    (t/assert= (:b m) 2)
    (t/assert= (:c m) 3)
    (t/assert= (:d m) nil)
    (t/assert= (:d m :foo) :foo)))

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

(t/deftest keyword-reader
  (t/assert= (read-string ":1") :1)
  (t/assert= (read-string ":1") :1)
  (t/assert= (read-string ":1.0") :1.0)
  (t/assert= (read-string ":foo") :foo)
  (t/assert= (read-string ":1foo") :1foo)
  (t/assert= (read-string ":foo/bar") :foo/bar)
  (t/assert= (read-string ":1foo/1bar") :1foo/1bar)
  (t/assert= (read-string ":nil") :nil)
  (t/assert= (read-string ":true") :true)
  (t/assert= (read-string ":false") :false)

  ;; We are reading at runtime so the namespace isn't
  ;; going to be pixie.test.test-keywords. Its probably
  ;; 'user but lets explicitly set it.
  ;; The refer-ns is to initialize a new space
  (refer-ns 'my.other.ns 'my.fake.core 'fake)
  (binding [*ns* (the-ns 'my.other.ns)]
    (t/assert= (read-string "::1")    :my.other.ns/1)
    (t/assert= (read-string "::1.0")  :my.other.ns/1.0)
    (t/assert= (read-string "::foo")  :my.other.ns/foo)
    (t/assert= (read-string "::true") :my.other.ns/true)))

(t/deftest string-to-keyword
  (t/assert= (keyword "1") :1)
  (t/assert= (keyword "1") :1)
  (t/assert= (keyword "1.0") :1.0)
  (t/assert= (keyword "foo") :foo)
  (t/assert= (keyword "1foo") :1foo)
  (t/assert= (keyword "foo/bar") :foo/bar)
  (t/assert= (keyword "1foo/1bar") :1foo/1bar)
  (t/assert= (keyword "nil") :nil)
  (t/assert= (keyword "true") :true)
  (t/assert= (keyword "false") :false)
  (t/assert-throws? (keyword 1))
  (t/assert-throws? (keyword :a))
  (t/assert-throws? (keyword 'a))
  (t/assert-throws? (keyword nil))
  (t/assert-throws? (keyword true)))
