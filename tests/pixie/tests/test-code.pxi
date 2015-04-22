(ns pixie.tests.test-code
  (:require [pixie.code :refer [introspect]]
            [pixie.test :refer :all]))


(deftest test-fn-types
  (assert-table [x y] (assert= (:type (introspect x)) y)
                (fn [x] x) :code
                (fn [& y] y) :variadic
                (fn ([] 0) ([x] 1)) :multi

                (let [x 1]
                  (fn [] x)) :closure

                  -conj :polymorphic
                  -add :double-polymorphic

                name :native))
