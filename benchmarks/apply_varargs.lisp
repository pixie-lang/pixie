(loop [x 0] (if (eq x 10000) x (recur ((fn [& args] (apply + 1 args)) x))))
:exit-repl
