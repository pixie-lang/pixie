(ns pixie.string
  (require pixie.string.internal :as si))

; reexport native string functions
(def substring si/substring)
(def index-of si/index-of)
(def split si/split)

(def ends-with si/ends-with)
(def starts-with si/starts-with)

(def trim si/trim)
(def triml si/triml)
(def trimr si/trimr)

(def capitalize si/capitalize)
(def lower-case si/lower-case)
(def upper-case si/upper-case)

(defn replace
  "Replace all occurrences of x in s with r."
  [s x r]
  (let [offset (if (zero? (count x)) (+ 1 (count r)) (count r))]
    (loop [start 0
           s s]
      (let [i (index-of s x start)]
        (if (neg? i)
          s
          (recur (+ i offset) (str (substring s 0 i) r (substring s (+ i (count x))))))))))

(defn replace-first
  "Replace the first occurrence of x in s with r."
  [s x r]
  (let [i (index-of s x)]
    (if (neg? i)
      s
      (str (substring s 0 i) r (substring s (+ i (count x)))))))
