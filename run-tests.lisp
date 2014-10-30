(require pixie.test :as t)


(swap! load-paths conj "./tests/")

(print @load-paths)

(t/load-all-tests)

(let [result (t/run-tests)]
     (exit (get result :fail)))
