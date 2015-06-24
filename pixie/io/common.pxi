(ns pixie.io.common
  "Common functionality for handling IO"
  (:require [pixie.streams :refer :all]))

(def DEFAULT-BUFFER-SIZE 1024)

(defn stream-reducer [this f init]
  (let [buf (buffer DEFAULT-BUFFER-SIZE)
        rrf (preserving-reduced f)]
    (loop [acc init]
      (let [read-count (read this buf DEFAULT-BUFFER-SIZE)]
        (if (> read-count 0)
          (let [result (reduce rrf acc buf)]
            (if (not (reduced? result))
              (recur result)
              @result))
          acc)))))
