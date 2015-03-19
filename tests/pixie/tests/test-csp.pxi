(ns pixie.tests.test-buffers
  (require pixie.test :refer :all)
  (require pixie.csp :refer :all))


(deftest test-go-blocks-return-values
  (assert= (<! (go 42)) 42))


(comment
  (deftest can-send-multiple-values
    (let [c (chan 2)
          go-result (go (mapv (partial >! c) (range 10)))]
      (assert= (map <! c) (range 10))
      (assert= go-result []))))
