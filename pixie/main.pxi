(ns pixie.main
  (:require [pixie.io-blocking :as io]
            [pixie.reader :as reader]
            [pixie.compiler :as compiler]
            [pixie.ast-output :as ast-out]))

(def libedit (ffi-library "libedit.dylib"))
(println libedit)
(def -readline (ffi-fn libedit "readline" [CCharP] CCharP))

(defrecord Foo [x y])

(let [env (compiler/new-env false)
      _ (println "MAKE ENV " (:ns env))
      data (reader/read-string "( * 1 2)")
      _ (println "got " data)
      ast (ast-out/to-ast (compiler/analyze data env))]
    (println "_> ast -> " ast)
    (println (pixie.ast.internal/eval ast)))

(defn repl []
  (with-handler [_ dynamic-var-handler]
    (binding [reader/*current-ns* 'user]
      (let [read-fn #(str (-readline "=>") "\n")
            rdr (reader/metadata-reader
                 (reader/user-space-reader read-fn)
                 "<repl>")]
        (loop []
          (let [d (reader/read rdr false)]
            (println "got " d)
            (println "analyzing ")
            (let [analyzed (ast-out/to-ast (compiler/analyze d))]
              (println "analyzed " analyzed)
              (println "result :" (pixie.ast.internal/eval analyzed)))
            (recur)))))))
(repl)

(println "done")
