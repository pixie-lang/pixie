(ns collections.test-vectors
  (require pixie.test :as t))



(def MAX-SIZE 2000)

(t/deftest vector-creation
  (loop [acc []]
    (if (= (count acc) MAX-SIZE)
      acc
      (do (dotimes [j (count acc)]
            (t/assert= j (nth acc j)))
          (recur (conj acc (count acc)))))))
