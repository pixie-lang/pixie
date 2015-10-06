(ns pixie.set
  (:require [pixie.stdlib :as std]))

(defn- -must-be-set [s]
  (if (set? s)
    s
    (throw [:pixie.stdlib/InvalidArgumentException
            (str "Not a set: " s)])))

(defn- -union [s t]
  (-must-be-set s)
  (-must-be-set t)
  (if (< (count s) (count t))
    (reduce conj t s)
    (reduce conj s t)))

(defn union
  "Returns a set that is the union of the input sets."
  ([] #{})
  ([s] (-must-be-set s))
  ([s t]
   (-union s t))
  ([s t & sets]
   (reduce -union (-union s t) sets)))
