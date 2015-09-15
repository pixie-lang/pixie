(ns benchmarks.readline
  (:require [pixie.time :as time]
            [pixie.io :as io]
            [pixie.streams.utf8 :as utf8]))

(def file-name "/usr/share/dict/words")

(println "Lazy line-seq")
(time/time (-> file-name
               (io/open-read)
               (io/line-seq)
               (count)
               (println)))

(println "Reducing line-reader")
(time/time 
  (-> file-name
      (io/open-read)
      (io/line-reader)
      (into [])
      (count)
      (println)))
