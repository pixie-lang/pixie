(ns pixie.test.test-utf8
  (require pixie.test :as t))

(t/deftest test-utf8-string-val
  (t/assert= "🍺=👍" "🍺=👍"))

(t/deftest test-utf8-var-name
  (let [🍺 "🍺=👍"]
    (t/assert= 🍺 "🍺=👍")))
