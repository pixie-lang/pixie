(ns pixie.test.test-bits
  (require pixie.test :as t))

(t/deftest test-bit-clear
  (t/assert= (bit-clear 0 0) 0)
  (t/assert= (bit-clear 2r11111 7) 2r11111)

  (t/assert= (bit-clear 2r111 0) 2r110)
  (t/assert= (bit-clear 2r111 1) 2r101)
  (t/assert= (bit-clear 2r111 2) 2r011))

(t/deftest test-bit-set
  (t/assert= (bit-set 2r111 0) 2r111)
  (t/assert= (bit-set 2r000 1) 2r010))

(t/deftest test-bit-flip
  (t/assert= (bit-flip 2r101 0) 2r100)
  (t/assert= (bit-flip 2r101 1) 2r111))

(t/deftest test-bit-test
  (t/assert= (bit-test 2r101 0) true)
  (t/assert= (bit-test 2r101 1) false))

(t/deftest test-bit-and
  (t/assert= (bit-and 0 0) 0)
  (t/assert= (bit-and 2r101 2r101) 2r101)
  (t/assert= (bit-and 2r101 2r101) 2r101)
  (t/assert= (bit-and 2r101 0) 0))

(t/deftest test-bit-or
  (t/assert= (bit-or 0 0) 0)
  (t/assert= (bit-or 2r101 2r010) 2r111)
  (t/assert= (bit-or 2r111 2r010) 2r111)
  (t/assert= (bit-or 2r111 2r111) 2r111)
  (t/assert= (bit-or 2r101 0) 2r101))

(t/deftest test-bit-xor
  (t/assert= (bit-xor 0 0) 0)
  (t/assert= (bit-xor 2r101 2r010) 2r111)
  (t/assert= (bit-xor 2r111 2r010) 2r101)
  (t/assert= (bit-xor 2r111 2r111) 2r000)
  (t/assert= (bit-xor 2r101 0) 2r101))

(t/deftest test-bit-shift-left
  (t/assert= (bit-shift-left 0 0) 0)
  (t/assert= (bit-shift-left 2r101 0) 2r101)

  (t/assert= (bit-shift-left 0 7) 0)
  (t/assert= (bit-shift-left 2r001 2) 2r100)
  (t/assert= (bit-shift-left 2r111 2) 2r11100))

(t/deftest test-bit-shift-right
  (t/assert= (bit-shift-right 0 0) 0)
  (t/assert= (bit-shift-right 2r101 0) 2r101)

  (t/assert= (bit-shift-right 0 7) 0)
  (t/assert= (bit-shift-right 2r001 2) 0)
  (t/assert= (bit-shift-right 2r111 2) 2r001)
  (t/assert= (bit-shift-right 2r1011010 2) 2r10110))
