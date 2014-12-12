(ns pixie.test.test-io
  (require pixie.test :as t)
  (require pixie.io :as io))

(t/deftest test-file-reduction
  (let [f (io/open-read "tests/pixie/test/test-io.txt")]
    (t/assert= (transduce (map identity)
                          count-rf
                          f)
               78)))
