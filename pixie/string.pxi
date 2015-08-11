(ns pixie.string
  (:require [pixie.stdlib :as std]
            [pixie.string.internal :as si]))

; reexport native string functions
(def substring si/substring)
(def index-of (comp #(if (not= -1 %) %) si/index-of))
(def split si/split)

(defn split-lines
  "Splits on \\n or \\r\\n, the two typical line breaks."
  [s]
  (when s (apply concat (map #(split % "\n") (split s "\r\n")))))

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

(defn reverse
   "Returns s with its characters reversed."
   [s]
   (when s
     (apply str (std/reverse s))))

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

(defn escape
  "Return a new string, using cmap to escape each character ch
   from s as follows:

   If (cmap ch) is nil, append ch to the new string.
   If (cmap ch) is non-nil, append (str (cmap ch)) instead."
  [s cmap]
  (if (or (nil? s)
          (nil? cmap))
    s
    (apply str (map #(if-let [c (cmap %)] c %)
                    (vec s)))))

(defmacro interp
  ; TODO: This might merit special read syntax
  {:doc "String interpolation."
   :examples [["(require pixie.string :refer [interp])"]
              ["(interp \"2 plus 2 is $(+ 2 2)$!\")" nil "2 plus 2 is 4!"]
              ["(let [x \"locals\"] (interp \"You can use arbitrary forms; for example $x$\"))"
               nil "You can use arbitrary forms; for example locals"]
              ["(interp \"$$$$ is the escape for a literal $$\")"
               nil "$$ is the escape for a literal $"]
              ]}
  [txt]
  (loop [forms [], txt txt]
    (cond
      (empty? txt) `(str ~@ forms)
      (starts-with? txt "$")
        (let [pos (or (index-of txt "$" 1)
                      (throw "Unmatched $ in interp argument!"))
              form-str (subs txt 1 pos)
              form (if (empty? form-str) "$"
                     (read-string form-str))
              rest-str (subs txt (inc pos))]
          (recur (conj forms form) rest-str))
      :else
        (let [pos (or (index-of txt "$")
                      (count txt))
              form (subs txt 0 pos)
              rest-str (subs txt pos)]
          (recur (conj forms form) rest-str)))))
