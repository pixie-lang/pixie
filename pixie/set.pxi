(ns pixie.set
  (:require [pixie.stdlib :as std]))

(defn- -must-be-set [s]
  (if (set? s)
    s
    (throw [:pixie.stdlib/InvalidArgumentException
            (str "Not a set: " s)])))

(defn- -must-be-sets [& sets]
  (doseq [set sets]
    (-must-be-set set)))

(defn- -union [s t]
     (-must-be-sets s t)
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
  (-must-be-sets s t)
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

(defn subset?
  "Returns true if the first set is a subset of the second."
  [s t]
  (-must-be-sets s t)
  (and (<= (count s) (count t))
       (every? #(contains? t %) (vec s))))

(defn strict-subset?
  "Returns true if the first set is a subset of the second."
  [s t]
  (-must-be-sets s t)
  (and (< (count s) (count t))
       (subset? s t)))

(defn superset?
  "Returns true if the first set is a superset of the second."
  [s t]
  (subset? t s))

(defn strict-superset?
  "Returns true if the first set is a strict superset of the second."
  [s t]
  (strict-subset? t s))
