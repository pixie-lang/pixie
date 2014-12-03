(ns pixie.tests.test-stdlib
  (require pixie.test :as t))

(t/deftest test-identity
  (let [vs [nil true false [1 2 3] #{1 2 3} :oops]]
    (doseq [v vs]
      (t/assert= (identity v) v))))

(t/deftest test-mapcat
  (t/assert= (mapcat identity []) [])
  (t/assert= (mapcat first [[[1 2]] [[3] [:not :present]] [[4 5 6]]]) [1 2 3 4 5 6]))

(t/deftest test-str
  (t/assert= (str nil) "nil")
  (t/assert= (str true) "true")
  (t/assert= (str false) "false")
  (t/assert= (str "hey") "hey")
  (t/assert= (str :hey) ":hey")
  (t/assert= (str 'hey) "hey")

  (t/assert= (str '()) "()")
  (t/assert= (str '(1 2 3)) "(1 2 3)")
  (t/assert= (str [1 2 3]) "[1 2 3]")
  (t/assert= (str #{1}) "#{1}")
  (t/assert= (str {}) "{}")
  (t/assert= (str {:a 1}) "{:a 1}")
  (t/assert= (str (type 3)) "<type pixie.stdlib.Integer>")

  (t/assert= (str [1 {:a 1} "hey"]) "[1 {:a 1} hey]"))

(t/deftest test-repr
  (t/assert= (-repr nil) "nil")
  (t/assert= (-repr true) "true")
  (t/assert= (-repr false) "false")
  (t/assert= (-repr "hey") "\"hey\"")
  (t/assert= (-repr :hey) ":hey")
  (t/assert= (-repr 'hey) "hey")

  (t/assert= (-repr '()) "()")
  (t/assert= (-repr '(1 2 3)) "(1 2 3)")
  (t/assert= (-repr [1 2 3]) "[1 2 3]")
  (t/assert= (-repr #{1}) "#{1}")
  (t/assert= (-repr {}) "{}")
  (t/assert= (-repr {:a 1}) "{:a 1}")
  (t/assert= (-repr (type 3)) "pixie.stdlib.Integer")

  (t/assert= (-repr [1 {:a 1} "hey"]) "[1 {:a 1} \"hey\"]"))

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

(t/deftest test-empty?
  (t/assert= (empty? []) true)
  (t/assert= (empty? '()) true)
  (t/assert= (empty? (make-array 0)) true)
  (t/assert= (empty? {}) true)
  (t/assert= (empty? #{}) true)
  (t/assert= (empty? (range 1 5)) false)

  (t/assert= (empty? [1 2 3]) false)
  (t/assert= (empty? '(1 2 3)) false)
  (let [a (make-array 1)]
    (aset a 0 1)
    (t/assert= (empty? a) false))
  (t/assert= (empty? {:a 1}) false)
  (t/assert= (empty? #{:a :b}) false))

(t/deftest test-not-empty?
  (t/assert= (not-empty? []) false)
  (t/assert= (not-empty? '()) false)
  (t/assert= (not-empty? (make-array 0)) false)
  (t/assert= (not-empty? {}) false)
  (t/assert= (not-empty? #{}) false)
  (t/assert= (not-empty? (range 1 5)) true)

  (t/assert= (not-empty? [1 2 3]) true)
  (t/assert= (not-empty? '(1 2 3)) true)
  (let [a (make-array 1)]
    (aset a 0 1)
    (t/assert= (not-empty? a) true))
  (t/assert= (not-empty? {:a 1}) true)
  (t/assert= (not-empty? #{:a :b}) true))

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

(t/deftest test-assoc
  (t/assert= (assoc {} :a 3) {:a 3})
  (t/assert= (assoc {:a 1} :a 3) {:a 3})

  (t/assert= (assoc [] 0 :ok) [:ok])
  (t/assert= (assoc [1] 0 :ok) [:ok])
  (t/assert= (assoc [1 2 3] 1 :ok) [1 :ok 3]))

(t/deftest test-get-in
  (let [m {:a 1 :b 2 :x {:a 2 :x [1 2 3]}}]
    (t/assert= (get-in m [:a]) 1)
    (t/assert= (get-in m [:missing]) nil)
    (t/assert= (get-in m [:missing] :not-found) :not-found)
    (t/assert= (get-in m [:x :x 0] :not-found) 1)))

(t/deftest test-assoc-in
  (t/assert= (assoc-in {:a {:b 2}} [:a :b] 3) {:a {:b 3}})
  (t/assert= (assoc-in {:a [{:b 2}]} [:a 0 :b] 3) {:a [{:b 3}]})
  ; non existing keys create maps (not vectors, even if the keys are integers)
  (t/assert= (assoc-in {} [:a :b] 3) {:a {:b 3}})
  (t/assert= (assoc-in {} [:a 0 :b] 3) {:a {0 {:b 3}}}))

(t/deftest test-update-in
  (t/assert= (update-in {} [:a :b] (fnil inc 0)) {:a {:b 1}})
  (t/assert= (update-in {:a {:b 2}} [:a :b] inc) {:a {:b 3}})
  (t/assert= (update-in {:a [{:b 2}]} [:a 0 :b] inc) {:a [{:b 3}]}))

(t/deftest test-fn?
  (t/assert= (fn? inc) true)
  (t/assert= (fn? {}) true)
  (t/assert= (fn? #(%)) true)
  (t/assert= (fn? :foo) true)
  (t/assert= (fn? 1) false)
  (t/assert= (fn? and) false)
  (t/assert= (fn? "foo") false)
  (t/assert= (fn? (let [x 8] (fn [y] (+ x y)))) true))

(t/deftest test-macro?
  (t/assert= (macro? and) true)
  (t/assert= (macro? or) true)
  (t/assert= (macro? defn) true)
  (t/assert= (macro? inc) false)
  (t/assert= (macro? 1) false)
  (t/assert= (macro? :foo) false)
  (t/assert= (macro? "foo") false))

(def ^:dynamic *earmuffiness* :low)

(t/deftest test-binding
  (t/assert= *earmuffiness* :low)
  (binding [*earmuffiness* :quite-high]
    (t/assert= *earmuffiness* :quite-high))
  (t/assert= *earmuffiness* :low))

(t/deftest test-every?
  (t/assert= (every? even? [2 4 6 8]) true)
  (t/assert= (every? odd?  [2 4 6 8]) false)
  (t/assert= (every? even? [2 3 6 8]) false)
  (t/assert= (every? even? []) true)
  (t/assert= (every? odd? []) true))

(t/deftest test-some
  (t/assert= (some even? [2 4 6 8]) true)
  (t/assert= (some odd?  [2 4 6 8]) false)
  (t/assert= (some even? [2 3 6 8]) true)
  (t/assert= (some even? [1 3 5 8]) true)
  (t/assert= (some even? []) false)
  (t/assert= (some odd? [2]) false))

(t/deftest test-distinct
  (t/assert= (sequence (distinct) [1 2 3 2 1]) '(1 2 3))
  (t/assert= (vec (distinct) [1 1 2 2 3 3]) [1 2 3])
  (t/assert= (vec (distinct) [nil nil nil]) [nil]))

(t/deftest test-merge
  (t/assert= (merge {}) {})
  (t/assert= (merge {:a 1} nil) {:a 1})

  (t/assert= (merge {} {:a 1, :b 2}) {:a 1, :b 2})
  (t/assert= (merge {:a 1} {:b 2}) {:a 1, :b 2})
  (t/assert= (merge {} {:a 1} {:b 2}) {:a 1, :b 2})

  (t/assert= (merge {:a 1} {:a 2, :b 3}) {:a 2, :b 3})
  (t/assert= (merge {:a 1, :b 4} {:a 2} {:a 3}) {:a 3, :b 4}))

(t/deftest test-for
  (t/assert= (for [x [1 2 3]] x) [1 2 3])
  (t/assert= (for [x [1 2 3] y [:a :b :c]] [x y])
             [[1 :a] [1 :b] [1 :c]
              [2 :a] [2 :b] [2 :c]
              [3 :a] [3 :b] [3 :c]]))
