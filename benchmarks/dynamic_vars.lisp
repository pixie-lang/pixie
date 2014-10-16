(defn add-fn [x]
  (inc (inc x)))


(set-dynamic! (resolve 'pixie.stdlib/add-fn))

(set! (resolve 'pixie.stdlib/add-fn) inc)


(loop [x 0] (if (eq x 10000)
                x (recur (add-fn x))))
:exit-repl
