(ns pixie.tests.test-parser
  (require pixie.test :refer :all)
  (require pixie.parser :refer :all))

(deftest test-and
  (let [p (parser []
                  (and \a \b))
        c (string-cursor "abc")]
    (assert= [\a \b] c)
    (assert= (current c) \c)))
