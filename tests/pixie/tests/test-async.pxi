(ns pixie.tests.test-async
  (:require [pixie.stacklets :as st]
            [pixie.async :as async :refer :all]
            [pixie.test :as t :refer :all]))


(deftest test-future-deref
  (let [f (future 42)]
    (assert= @f 42)))

(deftest test-future-deref-chain
  (let [f1 (future 42)
        f2 (future @f1)
        f3 (future @f2)]
    (assert= @f3 42)))

(def *some-var* 0)
(set-dynamic! (var *some-var*))

(deftest test-dynamic-var-propagation
  (set! (var *some-var*) 0)
  (assert= *some-var* 0)
  (let [fr @(future (do (println "running")
                       (let [old-val *some-var*]
                         (set! (var *some-var*) 42)
                         [old-val *some-var*])))]

    (assert= fr [0 42])
    (assert= *some-var* 0)))
