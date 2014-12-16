(ns pixie.tests.test-io
  (require pixie.test :as t)
  (require pixie.io :as io))

(t/deftest test-file-reduction
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (t/assert= (transduce (map identity)
                          count-rf
                          f)
               78)))

(t/deftest test-process-reduction
  (let [f (io/run-command "ls tests/pixie/tests/test-io.txt")]
    (t/assert= f "tests/pixie/tests/test-io.txt\n")))
