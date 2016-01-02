(ns pixie.generate-docs
  (:require [pixie.io :as io]
            [pixie.string :as string]))

(let [[namespace] program-arguments]
  
  (println "==============")
  (println (name namespace))
  (println "==============")

  (load-ns (symbol namespace))
  (println)

  ;;Should be sorting the map
  ;;Like so: (sort-by first map)
  ;;However, I'm holding off until sort is properly supported
  (doseq [[k v] (ns-map (the-ns namespace))]
    (println (name k))
    (println "====================================")
    (println)

    (if-let [m (meta @v)]
      (do
        ;(println m)
        (if-let [doc (:doc m)];;
          (println doc)
          (println "No doc available :("))
        (println)

        (when-let (examples (:examples m))
          (println "**Examples:**")
          (doseq [[code _ result] examples]
              (println)
              (println code)
              (println)
              (when (not (nil? result))
                (println "=> " result)))
          (println))
        
        (when-let (signatures (:signatures m))
          (println "**Signatures:**")
          (println)
          (doseq [sig signatures]
            (println (str "- " sig)))
          (println))

        (when (and (:line-number m) (:file m))
          (let [file (str "pixie/" (last (string/split (:file m) "/")))]
            (println (str "http://github.com/pixie-lang/pixie/blob/master/"
                        file "#L" (:line-number m))))
          (println)))

      (println "No meta data available :("))
        (println)))