(ns collections.test-maps
  (require pixie.test :as t))

(t/deftest maps-contains
  (let [m {:a 1, :b 2, :c 3}
        c [:a :b :c]
        n [:d 'a 1]]
    (foreach [c c]
             (t/assert= (contains? m c) true))
    (foreach [n n]
             (t/assert= (contains? m c) false))))
