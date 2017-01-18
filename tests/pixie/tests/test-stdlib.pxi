(ns pixie.tests.test-stdlib
  (require pixie.test :as t))

(t/deftest test-identity
  (let [vs [nil true false [1 2 3] #{1 2 3} :oops]]
    (doseq [v vs]
      (t/assert= (identity v) v))))

(t/deftest test-map
  (t/assert= (map inc [1 2 3]) [2 3 4])
  (t/assert= (map + [1 2 3] [4 5 6]) [5 7 9])
  (t/assert= (map + [1 2 3] [4 5 6] [7 8 9]) [12 15 18])
  (t/assert= (map + [1 2 3] (repeat 7)) [8 9 10])
  (let [value (map identity [1 2 3])]
    (t/assert= (seq value) [1 2 3])
    (t/assert= (seq value) [1 2 3])))

(t/deftest test-mapcat
  (t/assert= (mapcat identity []) [])
  (t/assert= (mapcat first [[[1 2]] [[3] [:not :present]] [[4 5 6]]]) [1 2 3 4 5 6]))

(t/deftest test-indexed
  (t/assert= (map-indexed (fn [& xs] xs) []) [])
  (t/assert= (map-indexed (fn [& xs] xs) [:a :b]) [[0 :a] [1 :b]])
  (t/assert= (transduce (map-indexed (fn [& xs] xs)) conj [:a :b]) [[0 :a] [1 :b]])

  (t/assert= (keep-indexed (constantly true) []) [])
  (t/assert= (keep-indexed (constantly nil) []) [])
  (t/assert= (keep-indexed (fn [i x] [i x]) [:a :b]) [[0 :a] [1 :b]])

  (t/assert= (transduce (keep-indexed (constantly true)) conj [:a :b]) [true true])
  (t/assert= (transduce (keep-indexed (constantly nil)) conj [:a :b]) [])
  (t/assert= (transduce (keep-indexed (fn [i x] [i x])) conj [:a :b]) [[0 :a] [1 :b]])

  (let [even-index? (fn [i x]
                        (when (even? i)
                          x))]
    (t/assert= (transduce (keep-indexed even-index?) conj [:a :b :c :d])
               [:a :c])
    (t/assert= (transduce (map-indexed even-index?) conj [:a :b :c :d])
               [:a nil :c nil])

    (t/assert= (transduce (comp (keep-indexed even-index?)
                                (take 3))
                          conj
                          [:a :b :c :d :e :f])
               [:a :c :e])
    (t/assert= (transduce (comp (map-indexed even-index?)
                                (take 3))
                          conj
                          [:a :b :c :d])
               [:a nil :c])))

(t/deftest test-reductions
  (t/assert= (reductions + nil)
             [0])
  (t/assert= (reductions + [1 2 3 4 5])
             [1 3 6 10 15])
  (t/assert= (reductions + 10 [1 2 3 4 5])
             [10 11 13 16 20 25]))

(t/deftest test-str
  (t/assert= (str nil) "nil")
  (t/assert= (str true) "true")
  (t/assert= (str false) "false")
  (t/assert= (str \a) "a")
  (t/assert= (str \u269b) "⚛")
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
  (t/assert= (str [1 {:a 1} "hey"]) "[1 {:a 1} hey]")
  (t/assert= (seq (map identity "iterable")) '(\i \t \e \r \a \b \l \e))
  (t/assert= (str (repeat 3 7)) "(7 7 7)")
  (t/assert= (str (range 3)) "(0 1 2)"))

(t/deftest test-repr
  (t/assert= (-repr nil) "nil")
  (t/assert= (-repr true) "true")
  (t/assert= (-repr false) "false")
  (t/assert= (-repr \a) "\\a")
  (t/assert= (-repr \u00fa) "\\u00fa")
  (t/assert= (-repr \u0fab) "\\u0fab")
  (t/assert= (-repr \u269b) "\\u269b")
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

  (t/assert= (-repr [1 {:a 1} "hey"]) "[1 {:a 1} \"hey\"]")
  (t/assert= (-repr (repeat 3 7)) "(7 7 7)")
  (t/assert= (-repr (range 3)) "(0 1 2)"))

(t/deftest test-nth
  ;; works if the index is found
  (t/assert= (nth [1 2 3] 1) 2)
  (t/assert= (nth '(1 2 3) 1) 2)
  (t/assert= (nth (make-array 3) 2) nil)
  (t/assert= (nth (repeat 4 1) 3) 1)
  (t/assert= (nth (range 4) 1) 1)
  (t/assert= (nth "hithere" 1) \i)

  ;; throws error for bad index
  (try
    (nth [1 2 3] 99)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth '(1 2 3) 99)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth (make-array 3) 99)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth (range 4) 99)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth "hithere" 99)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth [] 0)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth '() 0)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth (repeat 99 nil) 99)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))
  (try
    (nth (range 0 0) 0)
    (catch ex (t/assert= (ex-msg ex) "Index out of Range")))

  ;; if not-found is specified, uses that for out of range
  (t/assert= (nth [1 2 3] 99 :default) :default)
  (t/assert= (nth '(1 2 3) 99 :default) :default)
  (t/assert= (nth (make-array 3) 99 :default) :default)
  (t/assert= (nth (repeat 4 1) 99 :default) :default)
  (t/assert= (nth (range 4) 99 :default) :default)
  (t/assert= (nth "hithere" 99 :default) :default)

  (t/assert= (nth [1 2 3] 1 :default) 2)
  (t/assert= (nth '(1 2 3) 1 :default) 2)
  (t/assert= (nth (make-array 3) 2 :default) nil)
  (t/assert= (nth (repeat 4 1) 3 :default) 1)
  (t/assert= (nth (range 4) 1 :default) 1)
  (t/assert= (nth "hithere" 1 :deafult) \i))

(t/deftest test-get-on-vector
  (t/assert= (get [1 2 3] 0) 1)
  (t/assert= (get [1 2 3] 1) 2)
  (t/assert= (get [1 2 3] 2) 3)
  (t/assert= (get [1 2 3] 4) nil)
  (t/assert= (get [1 2 3] 5) nil)
  (t/assert= (get [1 2 3] 5 :not-found) :not-found))

(t/deftest test-first
  (t/assert= (first []) nil)
  (t/assert= (first '()) nil)
  (t/assert= (first (make-array 0)) nil)
  (t/assert= (first {}) nil)
  (t/assert= (first #{}) nil)

  (t/assert= (first {:a 1}) (map-entry :a 1))
  (t/assert= (first #{:a}) :a)

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
    (t/assert= (last (repeat 3 nil)) nil)
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
  (t/assert= (empty? (repeat '())) false)
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
  (t/assert= (not-empty? (repeat 0 'x)) false)
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
    (t/assert= (set (keys v)) #{:a :b :c})
    (t/assert= (transduce (keys) conj! v) (keys v))))

(t/deftest test-vals
  (let [v {:a 1 :b 2 :c 3}]
    (t/assert= (set (vals v)) #{1 2 3})
    (t/assert= (transduce (vals) conj! v) (vals v))))

(t/deftest test-select-keys
  (let [m ^{:k :v} {:a 1 :b 2}]
    (t/assert= (select-keys m [:a :b]) m)
    (t/assert= :v
               (-> (select-keys m [:a])
                   meta
                   :k))
    (t/assert= (select-keys m [:a :not-found]) {:a 1})
    (t/assert= (select-keys m nil) {})
    (t/assert= (select-keys {} [:a]) {})))

(t/deftest test-empty
  (t/assert= (empty '(1 2 3)) '())
  (t/assert= (empty (list 1 2 3)) '())
  (t/assert= (empty (lazy-seq)) '())
  (t/assert= (empty '()) '())
  (t/assert= (empty [1 2 3]) [])
  (t/assert= (empty (make-array 3)) (make-array 0))
  (t/assert= (empty {:a 1, :b 2, :c 3}) {})
  (t/assert= (empty #{1 2 3}) #{}))

(t/deftest test-count
  (t/assert= (count nil) 0)
  (t/assert= (count '()) 0)
  (t/assert= (count '(1 2 '(3 4))) 3)
  (t/assert= (count '(nil nil nil)) 3)
  (t/assert= (count (cons 1 [2 3])) 3)
  (t/assert= (count (list)) 0)
  (t/assert= (count (list 1 2 3)) 3)
  (t/assert= (count []) 0)
  (t/assert= (count [1 2 3]) 3)
  (t/assert= (count {}) 0)
  (t/assert= (count {:a 1, :b 2, :c 3}) 3)
  (t/assert= (count (first (seq {:a 1, :b 2, :c 3}))) 2)
  (t/assert= (count #{}) 0)
  (t/assert= (count (conj #{1 2 3} 3)) 3)
  (t/assert= (count (lazy-seq '())) 0)
  (t/assert= (count (lazy-seq '(1 2 3))) 3)
  (t/assert= (count (cons 1 (lazy-seq [2 3]))) 3)
  (t/assert= (count (range 0 -9 -3)) 3)
  (t/assert= (count "") 0)
  (t/assert= (count "123") 3)
  (t/assert= (count (make-array 3)) 3))

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
  (t/assert= (fn? and) true)
  (t/assert= (fn? "foo") false)
  (t/assert= (fn? (let [x 8] (fn [y] (+ x y)))) true))

(t/deftest test-coll?
  (t/assert= (coll? '()) true)
  (t/assert= (coll? []) true)
  (t/assert= (coll? {:foo "bar"}) true)
  (t/assert= (coll? #{:foo :bar}) true)
  (t/assert= (coll? #(%)) false)
  (t/assert= (coll? :foo) false)
  (t/assert= (coll? "foo") false)
  (t/assert= (coll? 1) false))

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

(t/deftest test-rand-int
  (let [vs (repeatedly 10 #(rand-int 4))]
    (t/assert (every? #(and (>= % 0) (< % 4)) vs)))
  (let [vs (repeatedly 10 #(rand-int 0))]
    (t/assert (every? zero? vs))))

(t/deftest test-some
  (t/assert= (some even? [2 4 6 8]) true)
  (t/assert= (some odd?  [2 4 6 8]) false)
  (t/assert= (some even? [2 3 6 8]) true)
  (t/assert= (some even? [1 3 5 8]) true)
  (t/assert= (some even? []) false)
  (t/assert= (some odd? [2]) false)
  (t/assert= (some #{:x :y} [:a :b :x :y]) :x)
  (t/assert= (some #{:x :y} [:a :b :c :y]) :y)
  (t/assert= (some #{:x :y} [:a :b :c :d]) false))

(t/deftest test-filter
  (t/assert= (vec (filter (fn [x] true) [])) [])
  (t/assert= (vec (filter (fn [x] false) [])) [])
  (t/assert= (vec (filter (fn [x] true) [1 2 3 4])) [1 2 3 4])
  (t/assert= (vec (filter (fn [x] false) [1 2 3 4])) [])
  (t/assert= (vec (filter (fn [x] true))
                  [1 2 3 4])
              [1 2 3 4])
  (t/assert= (vec (filter (fn [x] false))
                  [1 2 3 4])
              [])
  (t/assert= (seq (filter (fn [x] true) [])) nil)
  (t/assert= (seq (filter (fn [x] false) [])) nil)
  (t/assert= (seq (filter (fn [x] true) [1 2 3 4])) '(1 2 3 4))
  (t/assert= (seq (filter (fn [x] false) [1 2 3 4])) nil)
  (t/assert= (into {} (filter (fn [[_ v]] (odd? v)) {:a 1, :b 2, :c 3, :d 4}))
             {:a 1 :c 3}))

(t/deftest test-remove
  (t/assert= (remove even? [1 2 3 4 5]) '(1 3 5)))

(t/deftest test-distinct
  (t/assert= (seq (distinct [1 2 3 2 1])) '(1 2 3))
  (t/assert= (vec (distinct) [1 1 2 2 3 3]) [1 2 3])
  (t/assert= (vec (distinct) [nil nil nil]) [nil]))

(t/deftest test-merge
  (t/assert= (merge nil) nil)
  (t/assert= (merge {}) {})
  (t/assert= (merge {:a 1} nil) {:a 1})

  (t/assert= (merge {} {:a 1, :b 2}) {:a 1, :b 2})
  (t/assert= (merge {:a 1} {:b 2}) {:a 1, :b 2})
  (t/assert= (merge {} {:a 1} {:b 2}) {:a 1, :b 2})

  (t/assert= (merge {:a 1} {:a 2, :b 3}) {:a 2, :b 3})
  (t/assert= (merge {:a 1, :b 4} {:a 2} {:a 3}) {:a 3, :b 4}))

(t/deftest test-merge-with
  (t/assert= (merge-with identity nil) nil)
  (t/assert= (merge-with identity {}) {})

  (t/assert= (merge-with identity {} {:a 1, :b 2}) {:a 1, :b 2})
  (t/assert= (merge-with identity {:a 1} {:b 2}) {:a 1, :b 2})

  (t/assert= (merge-with (fn [a b] a) {:a 1} {:a 2}) {:a 1})
  (t/assert= (merge-with (fn [a b] a) {:a 1} {:a 2} {:a 3}) {:a 1})
  (t/assert= (merge-with (fn [a b] b) {:a 1} {:a 2}) {:a 2})

  (t/assert= (merge-with + {:a 21} {:a 21}) {:a 42})
  (t/assert= (merge-with + {:a 21} {:a 21, :b 1}) {:a 42, :b 1}))

(t/deftest test-for
  (t/assert= (for [x [1 2 3]] x) [1 2 3])
  (t/assert= (for [x [1 2 3] y [:a :b :c]] [x y])
             [[1 :a] [1 :b] [1 :c]
              [2 :a] [2 :b] [2 :c]
              [3 :a] [3 :b] [3 :c]])
  (t/assert= (for [x [[1 2 3]]
                   y x]
               y)
             [1 2 3]))

(t/deftest test-doto
  (let [a (atom 0)]
    (t/assert= a (doto a (swap! + 3) (swap! str)))
    (t/assert= @a "3")))

(t/deftest test-into
  (t/assert= [1 3] (into [] (comp (map inc) (filter odd?)) (range 3)))
  (t/assert= {:a 1 :b 2} (into {} [[:a 1] [:b 2]])))

(t/deftest test-ex-msg
  (try
    (throw [::something "This is an exception"])
    (catch e
        (t/assert= (ex-msg e) "This is an exception")
        (t/assert= (ex-data e) ::something))))

(t/deftest test-ex-filtering
  (let [f (fn [val]
            (try
              (try
                (throw [val "Some failure"])
                (catch ::catch-this ex
                  :found))
              (catch ex
                  :not-found)))]
    (t/assert= (f ::catch-this) :found)
    (t/assert= (f :something-else) :not-found))

  (let [f (fn [val]
            (try
              (try
                (throw [val "Some failure"])
                (catch (= ::catch-this (ex-data ex)) ex
                  :found))
              (catch ex
                  :not-found)))]
    (t/assert= (f ::catch-this) :found)
    (t/assert= (f :something-else) :not-found)))

(t/deftest test-repeat
  (t/assert= (seq (repeat 3 1)) '(1 1 1))
  (t/assert= (seq (repeat 0 1)) nil)
  (t/assert= (count (repeat 4096 'x)) 4096)
  (t/assert= (count (repeat 0 'x)) 0))

(t/deftest test-range
  (t/assert= (= (-seq (range 10))
                '(0 1 2 3 4 5 6 7 8 9))
             true))

(t/deftest test-ns
  ;; Create a namespace called foo
  (in-ns :foo)
  (def bar :humbug)
  (defn baz [x y] (+ x y))
  ;; Back into the text namespace
  (in-ns :pixie.tests.test-stdlib)
  (t/assert= (set (keys (ns-map 'foo)))
             #{'bar 'baz}))

(t/deftest test-ns-aliases
  (in-ns :ns-to-require)
  (in-ns :my-fake-ns)
  (require ns-to-require :as some-alias)
  (in-ns :pixie.tests.test-stdlib)
  (t/assert= {'some-alias (the-ns 'ns-to-require)
              'pixie.stdlib (the-ns 'pixie.stdlib)}
             (ns-aliases (the-ns 'my-fake-ns))))

(t/deftest test-while
  (t/assert=  (while (pos? 0) true ) nil)
  (t/assert=  (while (pos? 0) false) nil)
  (t/assert=  0 (let [x (atom 10)
                  cnt (atom 0)]
                 (while (pos? @x)
                   (do (swap! x dec)
                       (swap! cnt inc)))
                    @x))
  (t/assert=  10 (let [x (atom 10)
                  cnt (atom 0)]
                 (while (pos? @x)
                   (do (swap! x dec)
                       (swap! cnt inc)))
                    @cnt)))

(t/deftest test-loop
  (t/assert=
   [3 -3]
   (loop [[a b :as vs] [0 0]]
     (if (> a 2)
       vs
       (recur [(inc a) (dec b)]))))
  (t/assert=
   3
   (loop [a 1]
     (if (> a 2)
       a
       (recur (inc a))))))

(t/deftest test-take
  (t/assert= (take 0 [1 2 3 4]) ())
  (t/assert= (take 1 [1 2 3 4]) [1])
  (t/assert= (take 2 [1 2 3 4]) [1 2])
  (t/assert= (take 3 [1 2 3 4]) [1 2 3])
  (t/assert= (transduce (take 0) conj [1 2 3 4]) [])
  (t/assert= (transduce (take 1) conj [1 2 3 4]) [1])
  (t/assert= (transduce (take 2) conj [1 2 3 4]) [1 2])
  (t/assert= (transduce (take 3) conj [1 2 3 4]) [1 2 3])
  (t/assert= (transduce (take 10) conj [1 2 3 4]) [1 2 3 4])
  (t/assert= (transduce (comp (take 2) (take 1)) conj [1 2 3 4]) [1])
  (t/assert= (transduce (comp (take 1) (take 2)) conj [1 2 3 4]) [1])

  (let [call-count (atom 0)
        inc-call-count! (fn [x]
                          (swap! call-count inc)
                          x)]
    (t/assert= (transduce (comp (map inc-call-count!) (take 2)) conj (range 10))
               [0 1])
    (t/assert= @call-count 2)
    (t/assert= (transduce (comp (take 2) (map inc-call-count!)) conj (range 10))
               [0 1])
    (t/assert= @call-count 4)))

(t/deftest test-drop
  (t/assert= (drop 0 [1 2 3 4]) [1 2 3 4])
  (t/assert= (drop 1 [1 2 3 4]) [2 3 4])
  (t/assert= (drop 2 [1 2 3 4]) [3 4])
  (t/assert= (drop 3 [1 2 3 4]) [4])
  (t/assert= (transduce (drop 0) conj [1 2 3 4]) [1 2 3 4])
  (t/assert= (transduce (drop 1) conj [1 2 3 4]) [2 3 4])
  (t/assert= (transduce (drop 2) conj [1 2 3 4]) [3 4])
  (t/assert= (transduce (drop 3) conj [1 2 3 4]) [4])
  (t/assert= (transduce (drop 10) conj [1 2 3 4]) [])
  (t/assert= (transduce (comp (drop 1) (take 2)) conj [1 2 3 4]) [2 3])
  (t/assert= (transduce (comp (take 2) (drop 1)) conj [1 2 3 4]) [2]))

(t/deftest test-take-while
  (t/assert= (take-while pos? [1 2 3 -1]) [1 2 3])
  (t/assert= (take-while pos? [-1 2]) ())
  (t/assert= (transduce (take-while even?) conj [2 4 6 7 8]) [2 4 6])
  (t/assert= (transduce (take-while even?) conj [0 2] [1 4 6]) [0 2])
  (t/assert= (transduce (take-while even?) conj [1 3] [2 4 6 7 8]) [1 3 2 4 6])
  (t/assert= (transduce (comp (take-while even?) (take 2)) conj [1 3] [2 4 6 7 8]) [1 3 2 4]))

(t/deftest test-drop-while
  (t/assert= (drop-while pos? [1 2 3 -1]) [-1])
  (t/assert= (drop-while pos? [-1 2]) [-1 2])
  (t/assert= (transduce (drop-while even?) conj [2 4 6 7 8]) [7 8])
  (t/assert= (transduce (drop-while even?) conj [0 2] [1 4 6]) [0 2 1 4 6])
  (t/assert= (transduce (drop-while even?) conj [0 2] [2 4 6 7 8]) [0 2 7 8])
  (t/assert= (transduce (comp (drop-while even?) (take 2)) conj [0 2] [2 4 6 7 8]) [0 2 7 8]))

(t/deftest test-cycle
  (t/assert= (cycle ()) ())
  (t/assert= (cycle nil) ())
  (t/assert= (take 5 (cycle '(1 2))) '(1 2 1 2 1))
  (t/assert= (take 3 (cycle [nil])) '(nil nil nil)))

(t/deftest test-eduction
  ;; one xform
  (t/assert= [1 2 3 4 5]
             (eduction (map inc) (range 5)))
  ;; multiple xforms
  (t/assert= ["2" "4"]
             (eduction (map inc) (filter even?) (map str) (range 5)))
  ;; materialize at the end
  (t/assert= [1 1 2 1 2 3 1 2 3 4]
             (vec (->> (range 5)
                       (eduction (mapcat range) (map inc)))))
  (t/assert= {1 4, 2 3, 3 2, 4 1}
             (->> (range 5)
                  (eduction (mapcat range) (map inc))
                  frequencies))
  (t/assert= ["tac" "god" "hsif" "drib" "kravdraa"]
             (->> ["cat" "dog" "fish" "bird" "aardvark"]
                  (eduction (map pixie.string/reverse))
                  (seq)))
  ;; expanding transducer with nils
  (t/assert= '(1 2 3 nil 4 5 6 nil)
             (seq (eduction cat [[1 2 3 nil] [4 5 6 nil]]))))

(t/deftest test-trace
  (try
    (/ 0 0)
    (catch e
        (t/assert= (first (trace e)) {:type :runtime
                                      :data :pixie.stdlib/AssertionException
                                      :msg "Divide by zero"})
        (t/assert= (second (trace e)) {:type :native :name "_div"} ))))

(t/deftest test-tree-seq
  (t/assert= (vec (filter string?
                          (tree-seq map?
                                    :ch
                                    {:ch [{:ch ["a" "b"]}
                                          {:ch ["c" "d"]}
                                          {:ch [{:ch ["e" {:ch ["f"]}]}]}]})))
             ["a" "b" "c" "d" "e" "f"]))

(t/deftest test-group-by
  (t/assert= (group-by :age [{:name "banjo" :age 3}
                             {:name "mary"  :age 3}
                             {:name "boris" :age 7}])
             {3  [{:name "banjo" :age 3}
                  {:name "mary"  :age 3}]
              7  [{:name "boris" :age 7}]})
  (t/assert= (group-by even? (range 1 5))
             {true [2 4]
              false [1 3]}))


(t/deftest test-frequencies
  (t/assert= (frequencies [1 2 3 4 3 2 1])
             {1 2, 2 2, 3 2, 4 1}))

(t/deftest test-condp
  (t/assert-throws? RuntimeException
    "No matching clause!"
    (condp :dont-call-me :dont-use-me))
  (let [f (fn [x]
            (condp = x
              1 :one
              2 :two
              :whatever))]
    (t/assert= (f 1) :one)
    (t/assert= (f 2) :two)
    (t/assert= (f 9) :whatever)))

(t/deftest test-case
  (t/assert-throws? RuntimeException
    "No matching clause!"
    (case :no-matter-what))
  (let [f (fn [x]
            (case x
              1 :one
              2 :two
              #{3 4} :large
              :toolarge))]
    (t/assert= (f 1) :one)
    (t/assert= (f 2) :two)
    (t/assert= (f 3) :large)
    (t/assert= (f 4) :large)
    (t/assert= (f 9) :toolarge)))

(t/deftest test-instance?
  (t/assert= (instance? Keyword :a) true)
  (t/assert= (instance? Keyword 'a) false)
  (t/assert= (instance? [Symbol Keyword] :a) true)
  (t/assert= (instance? [Symbol Keyword] 'a) true)
  (t/assert= (instance? [Symbol Keyword] 42) false)
  (t/assert= (instance? [] :x) false)
  (t/assert-throws? RuntimeException
    "c must be a type"
    (instance? :not-a-type 123))
  (t/assert-throws? RuntimeException
    "c must be a type"
    (instance? [Keyword :also-not-a-type] 123)))

(t/deftest test-types-are-types
  (t/assert= Type (type Keyword))
  (t/assert= Type (type Integer))
  (t/assert= Type (type Number))
  (t/assert= Type (type Object))
  (t/assert= Type (type Type)))

(t/deftest test-satisfies?
  (t/assert= (satisfies? IIndexed [1 2]) true)
  (t/assert= (satisfies? IIndexed '(1 2)) false)
  (t/assert= (satisfies? [] :xyz) true)
  (t/assert= (satisfies? [ILookup IIndexed] [1 2]) true)
  (t/assert= (satisfies? [ILookup IIndexed] {1 2}) false)
  (t/assert-throws? RuntimeException
    "proto must be a Protocol"
    (satisfies? :not-a-proto 123))
  (t/assert-throws? RuntimeException
    "proto must be a Protocol"
    (satisfies? [IIndexed :also-not-a-proto] [1 2]))
  (defprotocol IFoo (foo [this]))
  (extend-protocol IFoo
    Number
    (foo [this] this))
  (t/assert= (satisfies? IFoo 1) true)
  (t/assert= (satisfies? IFoo 1.0) true)
  (t/assert= (satisfies? IFoo 1/2) true)
  (t/assert= (satisfies? IFoo \a) false))

(t/deftest test-reduce
 (t/assert= 300 (reduce + (repeat 100 3)))
 (t/assert= 0 (reduce + (repeat 0 3)))
 (t/assert= [9 9 9] (reduce (partial map +) (repeat 0) (repeat 3 (repeat 3 3))))
 (t/assert= 5050 (reduce + (range 101)))
 (t/assert= 3628800 (reduce * (range 1 11)))
 (t/assert= 5051 (reduce + 1 (range 101))))

(t/deftest test-comp
  (t/assert= 5 ((comp inc inc inc inc) 1))
  (t/assert= :xyz ((comp) :xyz)))

(t/deftest test-atom
  (let [a (atom 0)]
    (t/assert= 1 (swap! a inc))
    (t/assert= 2 (swap! a inc))
    (t/assert= 3 (reset! a 3))
    (t/assert= :bar (-> a (with-meta {:foo :bar}) meta :foo))))

(t/deftest pre-post-conds
  (let [f (fn ([a] {:pre [(even? a)] :post [(= % 6)]} (/ a 2))
            ([a b] {:pre [(= (+ 1 a) b)] :post [(odd? %)]} (+ a b)))]
    (t/assert= 6 (f 12))
    (t/assert-throws? RuntimeException
                      "Assert failed: (even? a)"
                      (f 13))
    (t/assert-throws? RuntimeException
                      "Assert failed: (= % 6)"
                      (f 14))
    (t/assert= 15 (f 7 8))
    (t/assert-throws? RuntimeException
                      "Assert failed: (= (+ 1 a) b)"
                      (f 1 1))))

(t/deftest test-lazyseq-conj
  (t/assert= '(1 2 3) (conj (lazy-seq '(2 3)) 1)))

(t/deftest map-entry-seq
  (let [m (map-entry :a 1)]
    (t/assert= (seq m) '(:a 1))
    ;; vectors are equal to seqs if their indexed values are equal
    ;; thus, a vector of length 2 is equal to a map-entry's seq IFoo
    ;; their values are equal
    (t/assert= [:a 1] m)
    (t/assert= '(:a 1) m)))

(t/deftest map-entry-equals
  (let [m (map-entry :a 1)]
    (t/assert= m m)
    (t/assert= m (map-entry :a 1))
    (t/assert= m [:a 1])
    (t/assert= m '(:a 1))))

(t/deftest test-vary-meta
  (t/assert= 42 (-> {} (vary-meta assoc :foo 42) meta :foo)))

(t/deftest test-memoize
  (let [f (memoize rand)]
    (t/assert= (f) (f))))

(t/deftest test-iterate
  (t/assert= (take 5 (iterate inc 5)) '(5 6 7 8 9))
  (t/assert= (reduce (fn [a v] (reduced "foo")) 0 (iterate inc 1)) "foo")
  (t/assert= (reduce (fn [a v] (if (< a 10) (+ a v) (reduced a))) 0 (iterate (partial + 2) 1)) 16))

(t/deftest test-sequence-empty-sequences
  (t/assert= '() (take 1 (sequence (map inc) '())))
  (t/assert= '() (take 1 (sequence (map inc) [])))
  (t/assert= '() (take 1 (sequence (map inc) #{})))
  (t/assert= '() (take 1 (sequence (map inc) {}))))

(t/deftest test-sequence-non-empty-sequences
  (t/assert= '(1 3) (take 2 (sequence (comp
                                       (filter even?)
                                       (map inc)) (range 3))))
  (t/assert= '(1) (take 1 (sequence (distinct) (repeat 4 1)))))

(t/deftest test-sequence-early-terminating-sequences
  (t/assert= '() (take 5 (sequence (filter (fn [x] false)) (repeat 8 8))))
  (t/assert= '(1 2) (take 3 (sequence (map identity) [1 2])))
  (t/assert= #{[:a 1] [:b 2]} (into #{} (take 3 (sequence (filter (fn [[k v]]
                                                                    (keyword? k)) {:a 1
                                                                                   :b 2
                                                                                   "c" 3
                                                                                   "d" 4}))))))
