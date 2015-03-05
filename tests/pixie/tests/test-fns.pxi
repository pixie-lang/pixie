(ns pixie.test.test-fns
  (require pixie.test :as t))

(t/deftest test-fn-literals
  (t/assert= (#(+ 3 4)) 7)
  (t/assert= (#(+ 3 %) 4) 7)
  (t/assert= (#(+ 3 %1) 4) 7)
  (t/assert= (#(+ %1 3) 4) 7)
  (t/assert= (#(+ %1 %1) 3.5) 7.0)
  (t/assert= (#(+ %1 %2) 3 4) 7)
  (t/assert= (#(- %2 %1) 3 4) 1)
  (t/assert= (#(+ %1 %1 %2 %2) 1.5 2) 7.0)
  (t/assert= (#(+ %1 %3) 3 'ignored 4) 7)
  (t/assert= (#(- %3 %1) 3 'ignored 4) 1)
  (t/assert= (#(apply + %1 %2 %&) 1 2 3 4 5) (+ 1 2 3 4 5)))

;; Note these tests are for functions of type 'Code'.
(t/deftest test-code-arity-errors
  (let [arity-0 (fn arity-0 [])
        arity-1 (fn arity-1 [a])
        arity-2 (fn arity-2 [a b])
        arity-0-or-1 (fn arity-0-or-1 ([]) ([a]))
        arity-1-or-3 (fn arity-1-or-3 ([a]) ([a b c]))
        arity-0-or-1-or-3-or-more 
        (fn arity-0-or-1-or-3-or-more ([]) ([a]) ([a b c & more]))]
    (t/assert-throws? RuntimeException 
      "Invalid number of arguments 1 for function 'arity-0'. Expected 0" 
      (arity-0 :foo))
    (t/assert-throws? RuntimeException
      "Invalid number of arguments 2 for function 'arity-0'. Expected 0"
      (arity-0 :foo :bar))
    (t/assert-throws? RuntimeException
      "Invalid number of arguments 0 for function 'arity-1'. Expected 1"
      (arity-1))
    (t/assert-throws? RuntimeException
      "Invalid number of arguments 2 for function 'arity-1'. Expected 1"
      (arity-1 :foo :bar))
    (t/assert-throws? RuntimeException
      "Invalid number of arguments 0 for function 'arity-2'. Expected 2"
      (arity-2))
    (t/assert-throws? RuntimeException
      "Invalid number of arguments 1 for function 'arity-2'. Expected 2"
      (arity-2 :foo))
    (t/assert-throws? RuntimeException
      "Wrong number of arguments 2 for function 'arity-0-or-1'. Expected 1,0"
      (arity-0-or-1 :foo :bar))
    (t/assert-throws? RuntimeException
      "Wrong number of arguments 3 for function 'arity-0-or-1'. Expected 1,0"
      (arity-0-or-1 :foo :bar :baz))
    (t/assert-throws? RuntimeException
      "Wrong number of arguments 2 for function 'arity-1-or-3'. Expected 3,1"
      (arity-1-or-3 :foo :bar))
    (t/assert-throws? RuntimeException
      "Wrong number of arguments 0 for function 'arity-1-or-3'. Expected 3,1"
      (arity-1-or-3))
    (t/assert-throws? RuntimeException
      "Wrong number of arguments 2 for function 'arity-0-or-1-or-3-or-more'. Expected 1,0,3 or more"
      (arity-0-or-1-or-3-or-more :foo :bar))))
