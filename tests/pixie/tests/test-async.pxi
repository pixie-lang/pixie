(ns pixie.tests.test-async
  (require pixie.stacklets :as st)
  (require pixie.async :as async :refer :all)
  (require pixie.test :as t :refer :all))


(deftest test-future-deref
  (let [f (future 42)]
    (assert= @f 42)))

(deftest test-future-deref-chain
  (let [f1 (future 42)
        f2 (future @f1)
        f3 (future @f2)]
    (assert= @f3 42)))
