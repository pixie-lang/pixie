(ns pixie.tests.test-numbers
  (require pixie.test :as t))

(t/deftest integer-literals
  (t/assert=  0xa  10)
  (t/assert= -0xa -10)
  (t/assert=  012  10)
  (t/assert= -012 -10)
  (t/assert=  2r1010 10)
  (t/assert= -2r1010 -10))

(t/deftest float-literals
  (t/assert=  10. 10.0)
  (t/assert= -10. -10.0)
  (t/assert=  1e1 10.0)
  (t/assert= -1e1 -10.0)
  (t/assert=  1e-1 0.1)
  (t/assert= -1e-1 -0.1))

(t/deftest mixed-float-ops
  (t/assert= (+ 1/2 0.5) 1.0)
  (t/assert= (+ 0 1.0) 1.0))

(t/deftest ratio-literals
  (t/assert=  3/4 (/ 3 4))
  (t/assert= -3/4 (/ -3 4))
  (t/assert=  6/8 3/4)
  (t/assert=  9/12 3/4)
  (t/assert=  3/1 3))

(t/deftest ratio-from-divide
  (t/assert= (/ 3 4) 3/4))

(t/deftest ratio-ops
  (t/assert= (+ 1/2 1/2) 1)
  (t/assert= (- 1/2 1/2) 0)
  (t/assert= (* 1/2 1/2) 1/4)
  (t/assert= (/ 1/2 1/2) 1))

(t/deftest ratio-accessors
  (doseq [[r n d] [[3/2 3 2] [1/9 1 9] [-3/89 -3 89]]]
    (t/assert= (numerator r) n)
    (t/assert= (denominator r) d)))

(t/deftest test-int
  (doseq [[x i] [[1 1] [3.0 3] [3.5 3] [3.999 3] [3/2 1]]]
    (t/assert= (int x) i)))

(t/deftest test-float
  (doseq [[x f] [[1 1.0] [3 3.0] [3.333 3.333] [3/2 1.5] [1/7 (/ 1.0 7.0)]]]
    (t/assert= (float x) f)))

(t/deftest rem-types
  (t/assert= Integer (type (rem 5 3)))
  (t/assert= Float (type (rem 5.0 3)))
  (t/assert= Ratio (type (rem 7/2 3)))
  (t/assert= Float (type (rem 7/2 3.0))))

(t/deftest quot-types
  (t/assert= Integer (type (quot 5 3)))
  (t/assert= Float (type (quot 5.0 3)))
  (t/assert= Integer (type (quot 7/2 3/7)))
  (t/assert= Float (type (quot 7/2 3.0))))

(t/deftest test-big-int-eq
  (t/assert (-num-eq 1N 1))
  (t/assert (-num-eq 1 1N))
  ;(t/assert= 1N 1) this fails, should it?
  (t/assert= 1 1N))

(t/deftest test-promotion
  (t/assert= BigInteger (type (reduce * 1 (range 1 100))))
  (t/assert (-num-eq 1000000000000000000000N (* 10000000 
                                                10000000 
                                                10000000))))
