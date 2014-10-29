(require pixie.test :as t)
(t/load-all-tests)
(let [result (t/run-tests)]
     (exit (get result :fail)))
