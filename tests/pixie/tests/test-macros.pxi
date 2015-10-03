(ns collections.test-macros
  (require pixie.test :as t))

(t/deftest hashmap-unquote
  (let [x 10 k :boop]
    (t/assert= (-eq `{:x ~x} {:x 10}) true)
    (t/assert= (-eq `{~k ~x} {:boop 10}) true)
    (t/assert= (-eq `{:x {:y ~x}} {:x {:y 10}}) true)))