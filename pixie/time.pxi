(ns pixie.time
  (:require [pixie.uv :as uv]))

(defmacro time
  [body]
  `(let [start# (uv/uv_hrtime)
         return# ~body]
     (prn (str "Elapsed time: " (/ (- (uv/uv_hrtime) start#) 1000000.0) "ms"))
     return#))
