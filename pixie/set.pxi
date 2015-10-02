(ns pixie.set
  (:require [pixie.stdlib :as std]))

(defn- -union [s t]
  (if (< (count s) (count t))
    (reduce conj t s)
    (reduce conj s t)))

(defn union
 "Returns a set that is the union of the input sets."
 ([] #{})
 ([s] s)
 ([s t] 
  (-union s t))
 ([s t & sets]
  (reduce -union (-union s t) sets)))
