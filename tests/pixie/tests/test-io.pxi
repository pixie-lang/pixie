(ns pixie.tests.test-io
  (require pixie.test :as t)
  (require pixie.io :as io))

(t/deftest test-file-reduction
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (t/assert= (transduce (map identity)
                          count-rf
                          f)
               91)))

(t/deftest test-process-reduction
  (let [f (io/run-command "ls tests/pixie/tests/test-io.txt")]
    (t/assert= f "tests/pixie/tests/test-io.txt\n")))

(t/deftest test-read-line
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (io/read-line f)
    (t/assert= (io/read-line f) "Second line.")
    (t/assert= (io/read-line f) nil)))

(t/deftest test-line-seq
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")
        s (io/line-seq f)]
    (t/assert= (last s) "Second line.")))

(comment
(t/deftest test-slurp-spit
  (let [val (vec (range 128))]
    (t/assert= val (read-string (io/slurp "test.tmp" (io/spit "test.tmp" val))))))
)
