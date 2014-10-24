(loop [acc []] 
  (if (= (count acc) 10000) 
    (hash acc) 
    (recur (conj acc (count acc)))))

:exit-repl
