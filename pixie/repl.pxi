(ns pixie.repl
  (require pixie.stacklets :as st)
  (require pixie.io :as io)
  (require pixie.ffi-infer :as f))

(f/with-config {:library "edit"
                :includes ["editline/readline.h"]}
  (f/defcfn readline))


(defn repl []
  (let [rdr (reader-fn (fn []
                         (let [prompt (if (= 0 pixie.stdlib/*reading-form*)
                                        (str (name pixie.stdlib/*ns*) " => ")
                                        "")
                               line (st/apply-blocking readline prompt)]
                           (if line
                             (str line "\n")
                             ""))))]
    (loop []
      (try (let [form (read rdr false)]
             (if (= form eof)
               (exit 0)
               (let [x (eval form)]
                 (pixie.stdlib/-push-history x)
                 (println x))))
           (catch ex
               (println "ERROR: \n" ex)))
      (recur))))
