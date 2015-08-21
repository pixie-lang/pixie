(ns pixie.generate-docs
  (:require [pixie.io :as io]
            [pixie.string :as string]))

(let [[namespace] program-arguments]

  (println "============================================================================")
  (println (name namespace))
  (println "============================================================================")
  
  (load-ns (symbol namespace))
  (println "\n")

  
  (doseq [[k v] (sort-by first (ns-map (the-ns namespace)))]
    (let [m (meta @v)]
      (println (name k))
      (println "----------------------------------------------------------------------------")
      #_(if (and (:line-number m)
               (:file m))
        #_(println (str "<a name=\""
                      (name k)
                      "\" "
                      "href=\"http://github.com/pixie-lang/pixie/blob/master/"
                      (:file m)
                      "#L"
                      (:line-number m)
                      "\"><h3>" (name k) "</h3></a>"))
        )
      #_(println "<ul>")
      #_(doseq [sig (:signatures (meta @v))]
        (println "<li>" sig "</li>"))
      (println "\n")
      (when (:doc m)
        (println (:doc m)))
      (println "\n")
      (comment (println)
               (when (:examples (meta @v))
                 (println "<h4>Examples:</h4>"))
               (doseq [[code _ result] (:examples (meta @v))]
                 (println "<p>" code "=><i>" result "</i></p>"))
               (println "\n<hr/>"))
      (println "\n\n")
      ))

  (println "</body></html>"))



