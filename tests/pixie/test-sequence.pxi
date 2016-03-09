(ns pixie.tests.test-sequence
  (:require [pixie.test :as t]))

(t/deftest empty-sequences
  (t/assert= '() (take 1 (sequence (map inc) '())))
  (t/assert= '() (take 1 (sequence (map inc) [])))
  (t/assert= '() (take 1 (sequence (map inc) #{})))
  (t/assert= '() (take 1 (sequence (map inc) {}))))

(t/deftest non-empty-sequences
  (t/assert= '(1 3) (take 2 (sequence (comp
                                       (filter even?)
                                       (map inc)) (range 3))))
  (t/assert= '(1) (take 1 (sequence (distinct) (repeat 4 1)))))

(t/deftest early-terminating-sequences
  (t/assert= '() (take 5 (sequence (filter (fn [x] false)) (repeat 8 8))))
  (t/assert= '(1 2) (take 3 (sequence (map identity) [1 2])))
  (t/assert= #{[:a 1] [:b 2]} (into #{} (take 3 (sequence (filter (fn [[k v]]
                                                                    (keyword? k)) {:a 1
                                                                                   :b 2
                                                                                   "c" 3
                                                                                   "d" 4}))))))
