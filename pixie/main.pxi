(ns pixie.main
  (:require [pixie.io-blocking :as io]
            [pixie.reader :as reader]
            [pixie.compiler :as compiler]
            [pixie.ast-output :as ast-out]
            [pixie.string :as string]))

(defmulti print-stack-at :type)
(defmethod print-stack-at :handler
  [{:keys [handler]}]
  (println "Handler:" (type handler) ":" handler))

(defmethod print-stack-at :default
  [{:keys [ast type]}]
  (if ast
    (let [meta (:meta (describe-internal-object ast))]
      (println (:line meta)
               "in"
               (:file meta)
               " "
               type
               "at"
               (str (:line-number meta)
                    ":"
                    (:column-number meta)))
      (println (apply str (repeat (- (:column-number meta) 2) " "))
               "^"))
    (println "Unknown location in " type)))

(defn print-stack-trace [ks]
  (doseq [slice ks]
    (doseq [k (:slice (describe-internal-object slice))]
      (print-stack-at k))))

(defn load-file [ns-sym]
  (let [name (if (string? ns-sym)
               ns-sym
               (string/replace (name ns-sym) "." "/"))
        name (if (string/ends-with? name ".pxi")
               name
               (str name ".pxi"))
        full-name (reduce
                   (fn [_ load-path]
                     (let [nm (str load-path "/" name)]
                       (println "Looking for " nm)
                       (when (pixie.io-blocking/file-exists? nm)
                         (reduced nm))))
                   nil
                   @load-paths)]
    (assert full-name (str "Couldn't load file " ns-sym))
    (load-resolved-file full-name)))

(defn load-resolved-file [full-name]
  (let [data (io/slurp full-name)
        rdr (reader/metadata-reader
             (reader/indexed-reader data)
             full-name)]
    (with-handler [_ dynamic-var-handler]
      (binding [reader/*current-ns* 'user]
        (loop []
          (println "read..")
          (let [d (reader/read rdr false)]
            (println "done")
            (if (not (= d :eof))
              (do (println "analyze")
                  (let [analyzed (ast-out/to-ast (compiler/analyze d))]
                    (println "done")
                    (println "eval")
                    (pixie.ast.internal/eval analyzed)
                    (println "done")
                    (recur))))))))))

#_(try
  (load-file :pixie.ffi-infer)
  (catch :* data
      (println "ERROR Compiling file" data)
      (print-stack-trace (:ks data))))


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
            (let [analyzed (try
                             (ast-out/to-ast (compiler/analyze d))
                             (catch :* data
                               (println "ERROR Analyzing" data)
                               (print-stack-trace (:ks data))))]
              (println "analyzed " analyzed)
              (try
                (println "result :" (pixie.ast.internal/eval analyzed))
                (catch :* data
                  (println "ERROR Compiling file" data)
                  (print-stack-trace (:ks data)))))
            (if (not (= d :exit-repl))
              (recur))))))))
(repl)

(println "done")


(count (with-handler [y (->Generator)]
         (reduce yield y (range 10000))))
