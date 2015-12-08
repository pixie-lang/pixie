(ns pixie.tests.data.test-json
  (:require [pixie.test :refer :all]
            [pixie.data.json :as json]))



;; This test just ensures that we can use read-string; more thorough testing is
;; done in pixie.tests.parser.test-json
(deftest test-read-string
  (assert= (json/read-string "{\"foo\": 42, \"bar\": [\"baz\"]}")
           {"foo" 42, "bar" ["baz"]}))

(deftest test-write-string
  (assert= (json/write-string {:strings {:a \a, :b "b", :c "", :d :d}
                               :numbers {:one 1, :two 2.0, :three 3/1}
                               :lists {:empty {:vector [], :list '(), :seq (take 0 (range))}
                                       :non-empty {:vector [1 2 3], :list '(1 2 3), :seq (take 3 (range))}}
                               :maps {:empty {}, :non-empty {:this "is covered, right? ;)"}}})
           "{ \"numbers\": { \"three\": 3, \"two\": 2.000000, \"one\": 1 }, \"lists\": { \"empty\": { \"vector\": [], \"list\": [], \"seq\": [] }, \"non-empty\": { \"vector\": [ 1, 2, 3 ], \"list\": [ 1, 2, 3 ], \"seq\": [ 0, 1, 2 ] } }, \"maps\": { \"empty\": {}, \"non-empty\": { \"this\": \"is covered, right? ;)\" } }, \"strings\": { \"d\": \"d\", \"a\": \"a\", \"c\": \"\", \"b\": \"b\" } }"))

(deftest test-round-trip
  (let [data {"foo" 1, "bar" [2 3]}]  ; won't work with keywords because the parser doesn't keywordise them (yet)
    (assert= (-> data json/write-string json/read-string)
             data))

  (let [string "{ \"foo\": [ 1, 2, 3 ] }"]
    (assert= (-> string json/read-string json/write-string)
             string)))
