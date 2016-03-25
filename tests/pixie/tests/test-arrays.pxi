(ns pixie.test.test-arrays
  (require pixie.test :as t))

(t/deftest test-array-creation
  (let [a (make-array 10)]
    (t/assert= (count a) 10)
    (t/assert= (alength a) 10)
    (foreach [x a]
             (t/assert= x nil))))

(t/deftest test-alength
  (let [a (make-array 10)]
    (t/assert= (alength a) 10)
    (t/assert-throws? RuntimeException
                      (alength []))))

(t/deftest test-aget-and-aset
  (let [a  (make-array 10)]
    (dotimes [i 10]
      (t/assert= (aget a i) nil))

    (dotimes [i 10]
      (aset a i i))

    (dotimes [i 10]
      (t/assert= (aget a i) i))

    (t/assert-throws? RuntimeException
               (aget a 1.0))

    (t/assert-throws? RuntimeException
               (aset a 1.0 :foo))))

(t/deftest test-aconcat
  (let [a1 (make-array 10)
        a2 (make-array 10)]
    (t/assert= (alength (aconcat a1 a2)) (+ (alength a1) (alength a2)))

    (dotimes [i 10]
      (aset a1 i i)
      (aset a2 i (+ 10 i)))

    (let [a3 (aconcat a1 a2)]
      (dotimes [i 20]
        (t/assert= (aget a3 i) i)))

    (t/assert-throws? RuntimeException
                      (t/aconcat a1 []))

    (t/assert-throws? RuntimeException
                      (t/aconcat a1 '()))))

(t/deftest test-aslice
  (let [a (make-array 10)]
    (dotimes [i 10]
      (aset a i i))

    (let [a1 (aslice a 3)
          a2 (aslice a 7)]
      (foreach [i (range 0 7)]
               (t/assert= (aget a1 i) (+ i 3)))
      (foreach [i (range 0 3)]
               (t/assert= (aget a2 i) (+ i 7))))

    (t/assert-throws? RuntimeException
                      (aslice [1 2 3 4] 0 2))

    (t/assert-throws? RuntimeException
                      (aslice '() 0 2))

    (t/assert-throws? RuntimeException
                      (aslice a 1.0 2))))


(t/deftest test-byte-array-creation
  (let [ba (byte-array 10)]
    (t/assert= (vec ba) [0 0 0 0 0 0 0 0 0 0])
    (t/assert= (count ba) 10)))
