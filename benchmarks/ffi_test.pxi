(loop [x 0]
  (if (= x 10000)
    x
    (do (printf ".")
        (recur (inc x)))))
