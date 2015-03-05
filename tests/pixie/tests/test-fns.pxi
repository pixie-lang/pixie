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
        multi-arity (fn arity-0-or-1)]
    (try
      (arity-0 :foo)
      (catch e
        (t/assert= 
         (ex-msg e) 
         "Invalid number of arguments 1 for function 'arity-0'. Expected 0")))
    (try
      (arity-0 :foo :bar)
      (catch e
        (t/assert= 
         (ex-msg e) 
         "Invalid number of arguments 2 for function 'arity-0'. Expected 0")))
    (try
      (arity-1)
      (catch e
        (t/assert= 
         (ex-msg e) 
         "Invalid number of arguments 0 for function 'arity-1'. Expected 1")))
    (try
      (arity-1 :foo :bar)
      (catch e
        (t/assert= 
         (ex-msg e) 
         "Invalid number of arguments 2 for function 'arity-1'. Expected 1")))
    (try
      (arity-2)
      (catch e
        (t/assert= 
         (ex-msg e) 
         "Invalid number of arguments 0 for function 'arity-2'. Expected 2")))
    (try
      (arity-2 :foo)
      (catch e
        (t/assert= 
         (ex-msg e) 
         "Invalid number of arguments 1 for function 'arity-2'. Expected 2")))))
