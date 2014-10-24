(let [map {:number 1}]
  (loop [x 0]
    (if (= x 10000)
      x
      (recur (+ x (get map :number))))))
