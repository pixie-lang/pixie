(ns pixie.tests.parsers.test-json
  (:require [pixie.test :refer :all]
            [pixie.parsers.json :as json]))



(deftest test-json-numbers
  (assert-table [x y] (assert= (json/read-string x) y)
                "1" 1
                "1.0" 1.0
                "0.1" 0.1))
