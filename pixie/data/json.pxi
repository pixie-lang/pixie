(ns pixie.data.json
  (:require [pixie.parser.json]
            [pixie.string :as string]))

(def read-string pixie.parser.json/read-string)

(defprotocol IToJSON
  (write-string [this]))

(defn- write-map [m]
  (if (empty? m)
    "{}"
    (str "{ "
         (->> m
              (map (fn [[k v]] (string/interp "$(write-string k)$: $(write-string v)$")))
              (string/join ", "))
         " }")))

(defn- write-sequential [xs]
  (if (empty? xs)
    "[]"
    (str "[ "
         (->> (map write-string xs)
              (string/join ", "))
         " ]")))

(defn- write-str [s]
  (string/interp "\"$s$\""))

(extend-protocol IToJSON
  Character (write-string [this] (write-str this))
  Cons (write-string [this] (write-sequential this))
  EmptyList (write-string [this] (write-sequential this))
  Number (write-string [this] (str this))
  Keyword (write-string [this] (write-str (name this)))
  LazySeq (write-string [this] (write-sequential this))
  IMap (write-string [this] (write-map this))
  IVector (write-string [this] (write-sequential this))
  Ratio (write-string [this] (str (float this)))
  String (write-string [this] (write-str this)))
