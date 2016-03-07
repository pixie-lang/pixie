(ns pixie.test.test-compiler
    (require pixie.test :as t))

(t/deftest test-do
  (t/assert= (do 1) 1)
  (t/assert= (do 1 2) 2)
  (t/assert= (do) nil)
  (t/assert= (do 1 2 3 4 5 6) 6))

(t/deftest test-if
  (t/assert= (if true 42 nil) 42)
  (t/assert= (if false 42 nil) nil)
  (t/assert= (if false 42) nil))

(t/deftest test-let
  (t/assert= (let [] 1) 1)
  (t/assert= (let [x 1]) nil)
  (t/assert= (let []) nil))

(t/deftest test-lists
  (t/assert= (vec '()) [])
  (t/assert= (vec '()) ()))


(defprotocol IMutable
  (mutate! [this]))

(deftype Foo [x]
  IMutable
  (mutate! [this]
    (let [xold x]
      (set-field! this :x 42)
      (t/assert (not (= xold x)))
      (t/assert (= x 42)))))

(t/deftest test-deftype-mutables
  (mutate! (->Foo 0)))

(t/deftest test-recur-must-tail
  (t/assert-throws? 
    (eval 
      '(loop [n 0] 
         (inc (recur n)))))

  (t/assert-throws? 
    (eval 
      '(fn [n]
         (if (zero? n)
           1
           (* n (recur (dec n)))))))

(t/assert-throws? 
    (eval 
      '(fn [n]
         (if (zero? n)
           (* n (recur (dec n)))
           1))))
  
  (t/assert= 
    (eval 
      '(loop [n 0] 
         (if (= 10 n)
           n
           (recur (inc n)))))
    10)

  (t/assert= 
    (eval 
      '(loop [n 0] 
         (if (not= 10 n)
           (recur (inc n))
           n)))
    10))
