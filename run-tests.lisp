(require pixie.test :as t)

(print @load-paths)

(t/load-all-tests)

(let [result (t/run-tests)]
     (exit (get result :fail)))
