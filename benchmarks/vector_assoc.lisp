(let [v (loop [acc []
               i 0]
          (if (= (count acc) 10000)
            acc
            (recur (conj acc i) (inc i))))]
  (loop [i 0]
    (if (= (nth acc i) i)
      (recur (inc i))
      (throw "Assert failure")))

  nil)



:exit-repl
