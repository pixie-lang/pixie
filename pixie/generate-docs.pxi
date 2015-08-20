(ns pixie.generate-docs
  (:require [pixie.io :as io]
            [pixie.string :as string]))

(let [[namespace] program-arguments]

  (println "<html><head></head><body>")
  (println "<h2>" (name namespace) "</h2")
  (load-ns (symbol namespace))
  (println "<hr/>")
  (println "<ul>")
  (doseq [k (sort (keys (ns-map (the-ns namespace))))]
    (println (str "<li><a href=\"#"
                  (name k)
                  "\">"
                  (name k)
                  "</a></li>")))
  (println "</ul>")  
  
  (println "<hr/>")

  
  (doseq [[k v] (sort-by first (ns-map (the-ns namespace)))]
    (let [m (meta @v)]
      (if (and (:line-number m)
               (:file m))
        (println (str "<a name=\""
                      (name k)
                      "\" "
                      "href=\"http://github.com/pixie-lang/pixie/blob/master/"
                      (:file m)
                      "#L"
                      (:line-number m)
                      "\"><h3>" (name k) "</h3></a>"))
        (println (str "<a name=\""
                      (name k)
                      "\" "
                      "\"><h3>" (name k) "</h3></a>")))
      (println "<ul>")
      (doseq [sig (:signatures (meta @v))]
        (println "<li>" sig "</li>"))
      (println "</ul>")
      (when (:doc m)
        (println "<p>" (:doc m)  "</p>"))
      (println)
      (when (:examples (meta @v))
        (println "<h4>Examples:</h4>"))
      (doseq [[code _ result] (:examples (meta @v))]
        (println "<p>" code "=><i>" result "</i></p>"))
      (println "\n<hr/>")
      ))

  (println "</body></html>"))



