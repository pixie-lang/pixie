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
