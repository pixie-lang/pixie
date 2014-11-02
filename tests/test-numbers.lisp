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
