(ns pixie.test.test-fns
  (require pixie.test :as t))

(t/deftest test-fn-literals
  (t/assert= (#(+ 3 4)) 7)
  (t/assert= (#(+ 3 %) 4) 7)
  (t/assert= (#(+ 3 %1) 4) 7)
  (t/assert= (#(+ %1 3) 4) 7)
  (t/assert= (#(+ %1 %2) 3 4) 7)
  (t/assert= (#(- %2 %1) 3 4) 1)
  (t/assert= (#(+ %1 %3) 3 'ignored 4) 7)
  (t/assert= (#(- %3 %1) 3 'ignored 4) 1)
  (t/assert= (#(apply + %1 %2 %&) 1 2 3 4 5) (+ 1 2 3 4 5)))
