(ns pixie.repl
  (require pixie.stacklets :as st)
  (require pixie.io :as io)
  (require pixie.ffi-infer :as f))

(f/with-config {:library "edit"
                :includes ["editline/readline.h"]}
  (f/defcfn readline))


(defn run-repl []
  (let [rdr (reader-fn (fn [] (str (st/apply-blocking readline "user->>>") "\n")))]
    (loop [x 1]
      (when (< x 3)

        (let [form (read rdr false)]
          (println (eval form))
          (recur (inc x)))))))

(run-repl)
