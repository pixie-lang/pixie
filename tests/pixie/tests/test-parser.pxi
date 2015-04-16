(ns pixie.tests.test-parser
  (:require [pixie.test :refer :all]
            [pixie.parser :refer :all]))

(deftest test-and
  (let [p (parser []
                  ENTRY (and \a \b <- [\a \b]))
        c (string-cursor "abc")]
    (assert= ((:ENTRY p) c) [\a \b])
    (assert= (current c) \c)
    (assert= 2 (snapshot c))))

(deftest test-or
  (let [p (parser []
                  ENTRY (or \b \a))
        c (string-cursor "abc")]
    (assert= ((:ENTRY p) c) \a)
    (assert= (current c) \b)
    (assert= 1 (snapshot c))))


(defparser as-and-bs []
  ENTRY (and S -> value
             end
             <- value)
  S (one+ AB) <- `[:S ~@value]
  AB (and A -> a
          B -> b
          <- [:AB a b])
  A (one+ \a) <- `[:A ~@value]
  B (one+ \b) <- `[:B ~@value])

(deftest test-as-and-bs
  (let [c (string-cursor "aabbaa")]
    (assert= ((:S as-and-bs) c) [:S [:AB
                                     [:A \a \a]
                                     [:B \b \b]]])
    (assert (not (at-end? c)))
    (assert= (snapshot c) 4)

    (assert (failure? ((:S as-and-bs) c))))

  (let [c (string-cursor "aabbaa")]
    (assert (failure? ((:ENTRY as-and-bs) c)) )
    (assert (not (at-end? c)))
    (assert= (snapshot c) 0)))
