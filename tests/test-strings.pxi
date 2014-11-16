(ns pixie.test.test-strings
  (require pixie.test :as t)
  (require pixie.string :as s))

(t/deftest test-starts-with
  (let [s "heyhohuh"]
    (t/assert= (s/starts-with s "") true)
    (t/assert= (s/starts-with s "hey") true)
    (t/assert= (s/starts-with s "heyho") true)
    (t/assert= (s/starts-with s s) true)

    (t/assert= (s/starts-with s "ho") false)
    (t/assert= (s/starts-with s "foo") false)))

(t/deftest test-ends-with
  (let [s "heyhohuh"]
    (t/assert= (s/ends-with s "") true)
    (t/assert= (s/ends-with s "huh") true)
    (t/assert= (s/ends-with s "hohuh") true)
    (t/assert= (s/ends-with s s) true)

    (t/assert= (s/ends-with s "hey") false)
    (t/assert= (s/ends-with s "foo") false)))

(t/deftest test-split
  (let [s "hey,ho,huh"]
    (t/assert= (s/split s ",") ["hey" "ho" "huh"])
    (t/assert= (s/split s "h") ["" "ey," "o," "u" ""])))

(t/deftest test-index-of
  (let [s "heyhohuh"]
    (t/assert= (s/index-of s "hey") 0)
    (t/assert= (s/index-of s "ho") 3)
    (t/assert= (s/index-of s "foo") -1)

    (t/assert= (s/index-of s "h" 2) 3)
    (t/assert= (s/index-of s "h" 4) 5)
    (t/assert= (s/index-of s "hey" 1) -1)

    (t/assert= (s/index-of s "h" 1 2) -1)))

(t/deftest test-substring
  (let [s "heyhohuh"]
    (t/assert= (s/substring s 0) s)
    (t/assert= (s/substring s 3) (s/substring s 3 (count s)))
    (t/assert= (s/substring s 0 0) "")
    (t/assert= (s/substring s 0 3) "hey")
    (t/assert= (s/substring s 3 5) "ho")
    (t/assert= (s/substring s 5 8) "huh")
    (t/assert= (s/substring s 3 10000) "hohuh")))

(t/deftest test-upper-case
  (t/assert= (s/lower-case "") "")
  (t/assert= (s/upper-case "hey") "HEY")
  (t/assert= (s/upper-case "hEy") "HEY")
  (t/assert= (s/upper-case "HEY") "HEY")
  (t/assert= (s/upper-case "hey?!") "HEY?!"))

(t/deftest test-lower-case
  (t/assert= (s/lower-case "") "")
  (t/assert= (s/lower-case "hey") "hey")
  (t/assert= (s/lower-case "hEy") "hey")
  (t/assert= (s/lower-case "HEY") "hey")
  (t/assert= (s/lower-case "HEY?!") "hey?!"))

(t/deftest test-capitalize
  (t/assert= (s/capitalize "timothy") "Timothy")
  (t/assert= (s/capitalize "Timothy") "Timothy"))

(t/deftest test-trim
  (t/assert= (s/trim "") "")
  (t/assert= (s/trim "      ") "")
  (t/assert= (s/trim "   hey  ") "hey")
  (t/assert= (s/trim "   h  ey   ") "h  ey"))

(t/deftest test-triml
  (t/assert= (s/triml "") "")
  (t/assert= (s/triml "     ") "")
  (t/assert= (s/triml "   hey") "hey")
  (t/assert= (s/triml "   hey  ") "hey  ")
  (t/assert= (s/triml "   h  ey   ") "h  ey   "))

(t/deftest test-trimr
  (t/assert= (s/trimr "") "")
  (t/assert= (s/trimr "     ") "")
  (t/assert= (s/trimr "hey   ") "hey")
  (t/assert= (s/trimr "   hey  ") "   hey")
  (t/assert= (s/trimr "   h  ey   ") "   h  ey"))

(t/deftest test-char-literals
  (let [s "hey"]
    (t/assert= (nth s 0) \h)
    (t/assert= (nth s 0) \o150)
    (t/assert= (nth s 0) \u0068)

    (t/assert= (nth s 1) \e)
    (t/assert= (nth s 1) \o145)
    (t/assert= (nth s 1) \u0065)

    (t/assert= (nth s 2) \y)
    (t/assert= (nth s 2) \o171)
    (t/assert= (nth s 2) \u0079)))
