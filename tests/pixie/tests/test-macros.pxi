(ns collections.test-macros
  (require pixie.test :as t))

(t/deftest hashmap-unquote
  (let [x 10 k :boop]
    (t/assert= (-eq `{:x ~x} {:x 10}) true)
    (t/assert= (-eq `{~k ~x} {:boop 10}) true)
    (t/assert= (-eq `{:x {:y ~x}} {:x {:y 10}}) true)))

(def constantly-nil (constantly nil))

(t/deftest some->test
  (t/assert (nil? (some-> nil)))
  (t/assert (= 0 (some-> 0)))
  (t/assert (= -1 (some-> 1 (- 2))))
  (t/assert (nil? (some-> 1 constantly-nil (- 2)))))

(t/deftest some->>test
  (t/assert (nil? (some->> nil)))
  (t/assert (= 0 (some->> 0)))
  (t/assert (= 1 (some->> 1 (- 2))))
  (t/assert (nil? (some->> 1 constantly-nil (- 2)))))

(t/deftest cond->test
  (t/assert (= 0 (cond-> 0)))
  (t/assert (= -1 (cond-> 0 true inc true (- 2))))
  (t/assert (= 0 (cond-> 0 false inc)))
  (t/assert (= -1 (cond-> 1 true (- 2) false inc))))

(t/deftest cond->>test
  (t/assert (= 0 (cond->> 0)))
  (t/assert (= 1 (cond->> 0 true inc true (- 2))))
  (t/assert (= 0 (cond->> 0 false inc)))
  (t/assert (= 1 (cond->> 1 true (- 2) false inc))))

(t/deftest as->test
  (t/assert (= 0 (as-> 0 x)))
  (t/assert (= 1 (as-> 0 x (inc x))))
  (t/assert (= 2 (as-> [0 1] x
             (map inc x)
             (reverse x)
             (first x)))))

(t/deftest threading-loop-recur
  (t/assert (nil? (loop []
              (as-> 0 x
                (when-not (zero? x)
                  (recur))))))
  (t/assert (nil? (loop [x nil] (some-> x recur))))
  (t/assert (nil? (loop [x nil] (some->> x recur))))
  (t/assert (= 0 (loop [x 0] (cond-> x false recur))))
  (t/assert (= 0 (loop [x 0] (cond->> x false recur)))))
