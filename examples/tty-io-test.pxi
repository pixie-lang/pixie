(ns io-test
  (:require [pixie.io :as io]
            [pixie.system :as sys]
            [pixie.io.tty :as tty]))

(def history (atom []))

(defn depth [d]
  (apply str (take d (repeat " "))))

(defn nested-trace
  "Prints a stack trace with each level indented slightly"
  [e]
  (loop [d 0 traces (trace e)]
    (io/spit tty/stdout (str (depth d) (pr-str (first traces)) "\n"))
    (if (seq traces)
      (recur (inc d) (rest traces)))))

(io/spit tty/stdout "TTY Demo REPL\n")
(loop []
  (let [command-number (count @history)]
    (io/spit tty/stdout (str "[ " command-number " ] < " ))
    (let [input (io/read-line tty/stdin)
          res   (try (eval (read-string input))
                     (catch e
                       (nested-trace e)))]
      (io/spit tty/stdout (str "[ " command-number " ] > " res "\n"))
      (swap! history conj input)
      (recur))))
