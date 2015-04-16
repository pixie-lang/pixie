(ns pixie.tests.parser.test-json
  (:require [pixie.test :refer :all]
            [pixie.parser.json :as json]))



(deftest test-json-numbers
  (assert-table [x y] (assert= (json/read-string x) y)
                "1" 1
                "1.0" 1.0
                "0.1" 0.1
                "1.1" 1.1
                "1234.5678" 1234.5678

                "-1" -1
                "-0.1" -0.1
                "-1.1" -1.1
                "-1234.5678" -1234.5678
                "1e1" 1e1))

(deftest test-vectors
  (assert-table [x y] (assert= (json/read-string x) y)
                "[]" []
                "[null]" [nil]
                "[1, 2]" [1 2]
                "[1, 1.0, null]" [1 1.0 nil]
                "[\"foo\", 42]" ["foo" 42]))

(deftest test-maps
  (assert-table [x y] (assert= (json/read-string x) y)
                "{\"foo\": 42}"  {"foo", 42}
                "{\"foo\": 42, \"bar\":null}"  {"foo" 42
                                                "bar" nil}))
