(ns pixie.test.test-deftype
  (require pixie.test :as t))

(deftype Simple [:val])
(deftype Simple2 [val])

(t/deftest test-simple
  (let [o1 (->Simple 1)
        o2 (->Simple 2)]
    (foreach [obj-and-val [[o1 1] [o2 2]]]
             (let [o (first obj-and-val)
                   v (second obj-and-val)]
               (t/assert= (get-field o :val) v)))))

(deftype MagicalVectorMap [] IMap IVector)

(t/deftest test-satisfies
  (let [mvm (->MagicalVectorMap)]
    (t/assert (satisfies? IVector mvm))
    (t/assert (satisfies? IMap mvm))))

(deftype Count [:val]
  ICounted
  (-count [self] val))

(deftype Count2 [val]
  ICounted
  (-count [self] val))

(t/deftest test-extend
  (let [o1 (->Count 1)
        o2 (->Count 2)]
    (foreach [obj-and-val [[o1 1] [o2 2]]]
             (let [o (first obj-and-val)
                   v (second obj-and-val)]
               (t/assert= (get-field o :val) v)
               (t/assert (satisfies? ICounted o))
               (t/assert= (-count o) v)
               (t/assert= (count o) v)))))

(defprotocol TestObject
  (add [self x & args])
  (one-plus [self x & xs]))

(deftype Three [:one :two :three]
  TestObject
  (add [self x & args]
    (apply + x args))
  (one-plus [self x & xs]
    (apply + one x xs))
  ICounted
  (-count [self] (+ one two three)))

(deftype Three2 [one two three]
  TestObject
  (add [self x & args]
    (apply + x args))
  (one-plus [self x & xs]
    (apply + one x xs))
  ICounted
  (-count [self] (+ one two three)))

(t/deftest test-complex
  (let [o1 (->Three 1 2 3)
        o2 (->Three2 3 4 5)]
    (foreach [obj-and-vals [[o1 1 2 3] [o2 3 4 5]]]
             (let [o (first obj-and-vals)
                   one (second obj-and-vals)
                   two (third obj-and-vals)
                   three (fourth obj-and-vals)]
               (t/assert= (get-field o :one) one)
               (t/assert= (get-field o :two) two)
               (t/assert= (get-field o :three) three)

               (t/assert (satisfies? ICounted o))
               (t/assert= (-count o) (+ one two three))
               (t/assert= (count o) (+ one two three))

               (t/assert= (add o 21 21) 42)
               (t/assert= (one-plus o 9) (+ one 9))))))
