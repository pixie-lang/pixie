(ns pixie.tests.parser.test-json
  (:require [pixie.test :refer :all]
            [pixie.io :refer [slurp open-read]]
            [pixie.parser :refer [failure? input-stream-cursor]]
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

(deftest test-streaming-json-file
  (let [filename "tests/pixie/tests/parser/test-json-data.json"
        cursor (-> filename
                   open-read
                   input-stream-cursor)
        streamed-result (json/read-one cursor)
        slurped-result (-> "tests/pixie/tests/parser/test-json-data.json"
                           slurp
                           json/read-string)]
    (assert (not (failure? streamed-result)))
    (assert (not (failure? slurped-result)))
    (assert= slurped-result streamed-result)))
