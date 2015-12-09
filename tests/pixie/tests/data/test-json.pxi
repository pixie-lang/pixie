(ns pixie.tests.data.test-json
  (:require [pixie.test :refer :all]
            [pixie.data.json :as json]))



;; This test just ensures that we can use read-string; more thorough testing is
;; done in pixie.tests.parser.test-json
(deftest test-read-string
  (assert= (json/read-string "{\"foo\": 42, \"bar\": [\"baz\"]}")
           {"foo" 42, "bar" ["baz"]}))

(deftest test-strings
  (assert-table [x y] (assert= (json/write-string x) y)
                \a "\"a\""
                "foo" "\"foo\""
                :bar "\"bar\""
                "" "\"\""))

(deftest test-numbers
  (assert-table [x y] (assert= (json/write-string x) y)
                1 "1"
                1.0 "1.000000"
                0.1 "0.100000"
                1.1 "1.100000"
                1234.5678 "1234.567800"
                -1 "-1"
                -0.1 "-0.100000"
                -1.1 "-1.100000"
                -1234.5678 "-1234.567800"
                1e1 "10.000000"
                3/1 "3"))

(deftest test-vectors
  (assert-table [x y] (assert= (json/write-string x) y)
                [] "[]"
                [nil] "[null]"
                [1 2] "[1, 2]"
                [1 1.0 nil] "[1, 1.000000, null]"
                ["foo" 42] "[\"foo\", 42]"))

(deftest test-seqs
  (assert-table [x y] (assert= (json/write-string x) y)
                (take 0 (range)) "[]"
                (take 1 (repeat nil)) "[null]"
                (map identity [1 2]) "[1, 2]"
                (reduce + [1 2 3]) "6"))

(deftest test-lists
  (assert-table [x y] (assert= (json/write-string x) y)
                '() "[]"
                '(nil) "[null]"
                '(1 2) "[1, 2]"
                '(1 1.0 nil) "[1, 1.000000, null]"
                '("foo" 42) "[\"foo\", 42]"
                (list) "[]"
                (list nil) "[null]"
                (list 1 2) "[1, 2]"
                (list 1 1.0 nil) "[1, 1.000000, null]"
                (list "foo" 42) "[\"foo\", 42]"))

(deftest test-maps
  (assert-table [x y] (assert= (json/write-string x) y)
                {} "{}"
                {:foo 42} "{\"foo\": 42}"
                {"foo" 42} "{\"foo\": 42}"
                {"foo" 42, "bar" nil} "{\"foo\": 42, \"bar\": null}"))

(deftest test-round-trip
  (let [data {"foo" 1, "bar" [2 3]}]  ; won't work with keywords because the parser doesn't keywordise them (yet)
    (assert= (-> data json/write-string json/read-string)
             data))

  (let [string "{\"foo\": [1, 2, 3]}"]
    (assert= (-> string json/read-string json/write-string)
             string)))
