(ns pixie.tests.test-readeval
  (require pixie.test :as t))

(t/deftest test-read
  (t/assert= (read-string "0xDEADBEEF") 3735928559)
  (t/assert= (read-string "0xDeadBeef") 3735928559)
  (t/assert= (read-string "0xdeadbeef") 3735928559) 
  (t/assert= (read-string "foo") 'foo)
  (t/assert= (read-string "()") '())
  (t/assert= (read-string "(1 2 3)") '(1 2 3))
  (t/assert= (read-string "[1 2 3]") [1 2 3])
  (t/assert= (read-string "{:a 1 :b 2 :c 3}") {:a 1 :b 2 :c 3})
  (t/assert= (read-string "\"foo\"") "foo")
  (t/assert= (read-string "\"fo\\\\o\"") "fo\\o")
  (t/assert= (read-string "false") false)
  (t/assert= (read-string "true") true)
  (t/assert= (read-string "(foo (bar (baz)))") '(foo (bar (baz)))))
