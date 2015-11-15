(ns pixie.tests.test-buffers
  (require pixie.test :refer :all)
  (require pixie.csp :refer :all))


(deftest test-go-blocks-return-values
  (assert= (<! (go 42)) 42))



(deftest can-send-multiple-values
  (let [c (chan 2)
        go-result (go (mapv (partial >! c) (range 10))
                      (close! c))]
    (assert= (vec c) (range 10))
    (assert= (<! go-result) nil)))


(deftest alts-works-correctly
  (let [c1 (chan 1)
        c2 (chan 1)
        results (go (hash-set (alts! [c1 c2])
                              (alts! [c1 c2])))]
    (>! c1 1)
    (>! c2 2)
    (assert (not (= c1 c2)))
    (assert= (<! results) #{[c1 1] [c2 2]})))

(deftest alts-prefers-default
  (let [c (chan 1)]
    (assert= (alts! [c] :default 42) [:default 42])
    (>! c 1)
    (assert= (alts! [c] :default 42) [c 1])))

(deftest test-timeout-channel
  (let [ts [(timeout 300)
            (timeout 200)
            (timeout 100)]]
    (-> (go
          (loop [ts (set ts)
                 res []]
            (if (empty? ts)
              res
              (let [[p _] (alts! ts)]
                (recur (set (remove #{p} ts))
                       (conj res p))))))
        <!
        (assert= (reverse ts)))))
