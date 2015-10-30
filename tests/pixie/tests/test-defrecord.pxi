(ns pixie.test.test-defrecord
  (require pixie.test :as t))

(defrecord Three [one two three])

(def t1 (->Three 1 2 3))
(def t2 (->Three 1 2 3))
(def t3 (map->Three {:one 1, :two 2, :three 3}))
(def t4 (->Three 1 2 4))
(def t5 (->Three 3 4 5))

(t/deftest test-satisfies
  (foreach [t [t1 t2 t3 t4 t5]]
           (t/assert= t t)
           (t/assert (satisfies? IRecord t))
           (t/assert (satisfies? IAssociative t))
           (t/assert (satisfies? ILookup t))))

(t/deftest test-record-pred
  (t/assert (record? t1)))

(t/deftest test-eq
  (t/assert= t1 t2)
  (t/assert= t2 t3)
  (t/assert= t3 t1)
  (foreach [t [t1 t2 t3]]
           (t/assert (not (= t (assoc t :one 42))))
           (t/assert (not (= t t4)))
           (t/assert (not (= t t5)))))

(t/deftest test-ilookup
  (foreach [t [t1 t2 t3]]
           (t/assert (satisfies? ILookup t))
           (t/assert= (get t :one) 1)
           (t/assert= (get t :two) 2)
           (t/assert= (get t :three) 3)
           (t/assert= (get t :oops) nil)
           (t/assert= (get t :oops 'not-found) 'not-found)))

(t/deftest test-iassociative
  (foreach [t [t1 t2 t3]]
           (t/assert (satisfies? IAssociative t))
           (t/assert= t (assoc t4 :three 3))
           (let [t' (assoc t :one 42)
                 t-oops (try (assoc t :oops 'never-found)
                             (catch ex t))]
             (t/assert (not (= t t')))
             (t/assert= (get t' :one) 42)
             (t/assert= t t-oops)
             (t/assert (not (contains? t-oops :oops)))
             (t/assert= (get t-oops :oops) nil))

           (t/assert (contains? t :one))
           (t/assert (contains? t :two))
           (t/assert (contains? t :three))))

(t/deftest test-record-metadata
  (t/assert= nil (meta t1))
  (t/assert= :foo (-> t1 (with-meta :foo) meta)))


(t/deftest ireduce []
  (t/assert= [[:one 1] [:two 2] [:three 3]] (reduce conj [] t1))
  (t/assert= [1 2 3] (vals t1))
  (t/assert= [:one :two :three] (keys t1)))
