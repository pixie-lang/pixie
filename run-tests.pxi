(require pixie.test :as t)

(println @load-paths)

(if (= 0 (count program-arguments))
  (t/load-all-tests)
  (doseq [nm program-arguments]
    (println "Loading: " nm)
    (load-ns (symbol nm))))

(let [result (apply t/run-tests program-arguments)]
     (exit (get result :fail)))
