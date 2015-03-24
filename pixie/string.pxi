(ns pixie.string
  (require pixie.string.internal :as si))

; reexport native string functions
(def substring si/substring)
(def index-of (comp #(if (not= -1 %) %) si/index-of))
(def split si/split)

(def ends-with? si/ends-with)
(def starts-with? si/starts-with)

(def trim si/trim)
(def triml si/triml)
(def trimr si/trimr)

(def capitalize si/capitalize)
(def lower-case si/lower-case)
(def upper-case si/upper-case)

; TODO: There should be locale-aware variants of these values
(def lower "abcdefghijklmnopqrstuvwxyz")
(def upper "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
(def digits "0123456789")
(def punctuation "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
(def whitespace (str \space \newline \tab \backspace \formfeed \return))
(def letters (str lower upper))
(def printable (str letters digits punctuation whitespace))
(def hexdigits "0123456789abcdefABCDEF")
(def octdigits "012345678")

(defn replace
  "Replace all occurrences of x in s with r."
  [s x r]
  (let [offset (if (zero? (count x)) (+ 1 (count r)) (count r))]
    (loop [start 0
           s s]
      (if-let [i (index-of s x start)]
        (recur (+ i offset) (str (substring s 0 i) r (substring s (+ i (count x)))))
        s))))

(defn replace-first
  "Replace the first occurrence of x in s with r."
  [s x r]
  (if-let [i (index-of s x)]
    (str (substring s 0 i) r (substring s (+ i (count x))))
    s))

(defn join
  {:doc "Join the elements of the collection using an optional separator"
   :examples [["(require pixie.string :as s)"]
              ["(s/join [1 2 3])" nil "123"]
              ["(s/join \", \" [1 2 3])" nil "1, 2, 3"]]}
  ([coll] (join "" coll))
  ([separator coll]
     (loop [s (seq coll)
            res ""]
       (cond
        (nil? s) res
        (nil? (next s)) (str res (first s))
        :else (recur (next s) (str res (first s) separator))))))

(defn blank?
  "True if s is nil, empty, or contains only whitespace."
  [s]
  (if s
    (let [white (set whitespace)
          length (count s)]
      (loop [index 0]
        (if (= length index)
          true
          (if (white (nth s index))
            (recur (inc index))
            false))))
    true))
