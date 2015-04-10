(ns pixie.test.test-errors
  (:require [pixie.test :refer :all]))

(deftest test-add-exception-info
  (try
    (try
      (+ 1 "foo")
      (catch ex
          (throw (add-exception-info ex "My Msg" :my-data))))
    (catch ex
        (let [filter-fn (fn [mp]
                          (and (= (:type mp) :extra)
                               (= (:msg mp) "My Msg")
                               (= (:data mp) :my-data)))]
          (assert= 1 (count (filter filter-fn ex)))))))
