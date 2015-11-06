(ns pixie.tests.test-walk
  (:require [pixie.walk :as w]
            [pixie.test :as t]))

(t/deftest t-prewalk-replace
  (t/assert (= (w/prewalk-replace {:a :b} [:a {:a :a} (list 3 :c :a)])
         [:b {:b :b} (list 3 :c :b)])))

(t/deftest t-postwalk-replace
  (t/assert (= (w/postwalk-replace {:a :b} [:a {:a :a} (list 3 :c :a)])
         [:b {:b :b} (list 3 :c :b)])))

(t/deftest t-prewalk-order
  (t/assert (= (let [a (atom [])]
                 (w/prewalk (fn [form] (swap! a conj form) form)
                            [1 2 {:a 3} (list 4 [5])])
                 @a)
               [[1 2 {:a 3} (list 4 [5])]
                1 2 {:a 3} [:a 3] :a 3 (list 4 [5])
                4 [5] 5])))

(t/deftest t-postwalk-order
  (t/assert (= (let [a (atom [])]
           (w/postwalk (fn [form] (swap! a conj form) form)
                      [1 2 {:a 3} (list 4 [5])])
           @a)
         [1 2
          :a 3 [:a 3] {:a 3}
          4 5 [5] (list 4 [5])
          [1 2 {:a 3} (list 4 [5])]])))

(defrecord Foo [a b c])

(t/deftest walk
  "Checks that walk returns the correct result and type of collection"
         (let [colls ['(1 2 3)
                      [1 2 3]
                      #{1 2 3}
                      {:a 1, :b 2, :c 3}
                      (->Foo 1 2 3)]]
           (doseq [c colls]
             (let [walked (w/walk identity c)]
               (t/assert (= c walked))
               (t/assert (= (type c) (type walked)))
               (if (or (map? c)
                       (record? c))
                 (do
                   (t/assert (= (reduce + (vals (w/walk
                                                 #(map-entry
                                                   (key %)
                                                   (inc (val %)))
                                                 c)))
                                (reduce + (map (comp inc val) c)))))
                 (t/assert (= (reduce + (w/walk inc c))
                        (reduce + (map inc c)))))))))

(t/deftest t-stringify-keys
  (t/assert (= (w/stringify-keys {:a 1, nil {:b 2 :c 3}, :d 4})
         {"a" 1, nil {"b" 2 "c" 3}, "d" 4})))
