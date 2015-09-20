(ns benchmarks.readline
  (:require [pixie.time :as time]
            [pixie.io :as io]
            [pixie.streams.utf8 :as utf8]))

(def file-name "/usr/share/dict/words")

(println "Lazy line-seq")
(time/time 
  (->> file-name
       (io/open-read)
       (io/buffered-input-stream)
       (io/line-seq)
       (count)))

(println "Reducing line-reader")
(time/time 
  (->> file-name
       (io/open-read)
       (io/buffered-input-stream)
       (io/line-reader)
       (into [])
       (count)))

(println "Lazy UTF8 line-seq")
(time/time 
  (->> file-name
       (io/open-read)
       (io/buffered-input-stream)
       (utf8/utf8-input-stream)
       (io/line-seq)
       (count)))

(println "Reducing UTF8 line-reader")
(time/time 
  (->> file-name
       (io/open-read)
       (io/buffered-input-stream)
       (utf8/utf8-input-stream)
       (io/line-reader)
       (into [])
       (count)))
