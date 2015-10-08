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

(defn- -difference [s t]
  (-must-be-set s)
  (-must-be-set t)
  (into #{} (filter #(not (contains? t %))) s))

(defn difference
  "Returns a set that is the difference of the input sets."
  ([] #{})
  ([s] (-must-be-set s))
  ([s t]
   (-difference s t))
  ([s t & sets]
   (reduce -difference (-difference s t) sets)))

(defn- -intersection [s t]
  (-must-be-set s)
  (-must-be-set t)
  (into #{} (filter #(contains? s %)) t))

(defn intersection
  "Returns a set that is the intersection of the input sets."
  ([] #{})
  ([s] (-must-be-set s))
  ([s t]
   (-intersection s t))
  ([s t & sets]
   (reduce -intersection (-intersection s t) sets)))
