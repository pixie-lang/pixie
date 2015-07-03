(ns pixie.compile-bootstrap
  (:require [pixie.compiler :refer :all]
            [pixie.io :as io]
            [pixie.pxic-writer :as pxic-writer]
            [pixie.bootstrap-macros]))



(defn read-and-compile [form env]
  (let [ast (analyze form env)]
    ast))

(defn compile-file [env from os]
  (let [forms (read-string (str "[" (io/slurp from) "]") from)
        form-count (atom 0)
        total-count (atom 0)]
    (doseq [form forms]
          (swap! form-count inc)
          (swap! total-count inc)
          (when (= @form-count 10)
            (println from (int (* 100 (/ @total-count (count forms)))) "% in" @(:ns env))
            (reset! form-count 0))
          
          (let [ast (read-and-compile form env)]
            (pxic-writer/write-object os ast)))))

(defn compile-files [files to]
  (let [os (-> to
               io/open-write
               io/buffered-output-stream)
        env (new-env true)]
    
    (binding [pxic-writer/*cache* (pxic-writer/writer-cache os)]
      (doseq [file files]
        (compile-file env file os)))
    (dispose! os)))

(compile-files ["pixie/bootstrap.pxi"
                #_"pixie/bootstrap-macros.pxi"
                "pixie/streams.pxi"
                "pixie/io-blocking.pxi"
                "pixie/reader.pxi"
                "pixie/ast.pxi"
                "pixie/ast-output.pxi"
                "pixie/compiler.pxi"
                "pixie/main.pxi"]
               "./bootstrap.pxic")

