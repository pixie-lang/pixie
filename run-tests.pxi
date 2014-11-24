(require pixie.test :as t)

(println @load-paths)

(t/load-all-tests)

(let [result (apply t/run-tests program-arguments)]
     (exit (get result :fail)))
