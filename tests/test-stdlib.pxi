(ns pixie.tests.test-stdlib
  (require pixie.test :as t))

(t/deftest test-first
  (t/assert= (first []) nil)
  (t/assert= (first '()) nil)
  (t/assert= (first (make-array 0)) nil)
  (comment (t/assert= (first {}) nil))
  (comment (t/assert= (first #{}) nil))

  (t/assert= (first [1 2 3]) 1)
  (t/assert= (first '(1 2 3)) 1)
  (let [a (make-array 3)]
    (aset a 0 1)
    (aset a 1 2)
    (aset a 2 3)
    (t/assert= (first a) 1)))

(t/deftest test-last
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)]
    (t/assert= (last nil) nil)
    (t/assert= (last []) nil)
    (t/assert= (last (range 0 0)) nil)
    (t/assert= (last v) 5)
    (t/assert= (last l) 5)
    (t/assert= (last r) 5)))

(t/deftest test-butlast
  (let [v [1 2 3 4 5]
        l '(1 2 3 4 5)
        r (range 1 6)
        res '(1 2 3 4)]
    (t/assert= (butlast nil) nil)
    (t/assert= (butlast []) nil)
    (t/assert= (butlast (range 0 0)) nil)
    (t/assert= (butlast v) res)
    (t/assert= (butlast l) res)
    (t/assert= (butlast r) res)))


(t/deftest test-keys
  (let [v {:a 1 :b 2 :c 3}]
    (t/assert= (keys v) #{:a :b :c})
    (t/assert= (transduce (keys) conj! v) (keys v))))

(t/deftest test-vals
  (let [v {:a 1 :b 2 :c 3}]
    (t/assert= (vals v) #{1 2 3})
    (t/assert= (transduce (vals) conj! v) (vals v))))


(t/deftest test-empty
  (t/assert= (empty '(1 2 3)) '())
  (t/assert= (empty (list 1 2 3)) '())
  (t/assert= (empty (lazy-seq)) '())
  (t/assert= (empty '()) '())
  (t/assert= (empty [1 2 3]) [])
  (t/assert= (empty (make-array 3)) (make-array 0))
  (t/assert= (empty {:a 1, :b 2, :c 3}) {})
  (t/assert= (empty #{1 2 3}) #{}))


(t/deftest test-vec
  (let [v '(1 2 3 4 5)]
    (t/assert= (vec v) [1 2 3 4 5])
    (t/assert= (vec (map inc) v) [2 3 4 5 6])))


(t/deftest test-keep
  (let [v [-1 0 1 2 3 4 5]]
    (t/assert= (vec (keep pos?) v) [true true true true true])
    (t/assert= (vec (keep pos? v)) (vec (keep pos?) v))))

(t/deftest test-get-in
  (let [m {:a 1 :b 2 :x {:a 2 :x [1 2 3]}}]
    (t/assert= (get-in m [:a]) 1)
    (t/assert= (get-in m [:missing]) nil)
    (t/assert= (get-in m [:missing] :not-found) :not-found)
    (t/assert= (get-in m [:x :x 0] :not-found) 1)))

(t/deftest test-fn?
  (t/assert= (fn? inc) true)
  (t/assert= (fn? {}) true)
  (t/assert= (fn? #(%)) true)
  (t/assert= (fn? :foo) true)
  (t/assert= (fn? 1) false)
  (t/assert= (fn? and) false)
  (t/assert= (fn? "foo") false)
  (t/assert (fn? (let [x 8] (fn [y] (+ x y)))) true))

