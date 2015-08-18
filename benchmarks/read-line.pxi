(ns benchmarks.readline
  (:require [pixie.time :as time]
            [pixie.io :as io]))

(def file-name "/usr/share/dict/words")

(println "testing unbuffered")
(time/time (-> file-name
               (io/open-read)
               (io/line-seq)
               (count)))

(println "testing buffered")
(time/time (-> file-name
               (io/open-read)
               (io/buffered-input-stream)
               (io/line-seq)
               (count)))
