(def reset! -reset!)

(def map (fn map [f]
             (fn [xf]
                 (fn
                  ([] (xf))
                  ([result] (xf result))
                  ([result item] (xf result (f item)))))))

(def conj (fn conj
           ([] [])
           ([result] result)
           ([result item] (-conj result item))))

(def transduce (fn transduce
              ([f coll]
                (let [result (-reduce coll f (f))]
                      (f result)))

              ([xform rf coll]
                (let [f (xform rf)
                      result (-reduce coll f (f))]
                      (f result)))
              ([xform rf init coll]
                (let [f (xform rf)
                      result (-reduce coll f init)]
                      (f result)))))

(def reduce (fn [rf init col]
              (-reduce col rf init)))


(def interpose
     (fn interpose [val]
       (fn [xf]
           (let [first? (atom true)]
                (fn
                 ([] (xf))
                 ([result] (xf result))
                 ([result item] (if @first?
                                    (do (reset! first? false)
                                        (xf result item))
                                  (xf (xf result val) item))))))))


(def preserving-reduced
  (fn [rf]
    (fn [a b]
      (let [ret (rf a b)]
        (if (reduced? ret)
          (reduced ret)
          ret)))))

(def cat
  (fn cat [rf]
    (let [rrf (preserving-reduced rf)]
      (fn
        ([] (rf))
        ([result] (rf result))
        ([result input]
           (reduce rrf result input))))))


(def seq-reduce (fn seq-reduce
                  [coll f init]
                  (loop [init init
                         coll (seq coll)]
                    (if (reduced? init)
                      @init
                      (if (seq coll)
                        (recur (f init (first coll))
                               (seq (next coll)))
                        init)))))

(def indexed-reduce (fn indexed-reduce
                      [coll f init]
                      (let [max (count coll)]
                      (loop [init init
                             i 0]
                        (if (reduced? init)
                          @init
                          (if (-eq i max)
                            init
                            (recur (f init (nth coll i)) (+ i 1))))))))

(extend -reduce Cons seq-reduce)
(extend -reduce PersistentList seq-reduce)
(extend -reduce LazySeq seq-reduce)

(extend -reduce Array indexed-reduce)

(extend -str Bool
  (fn [x]
    (if (identical? x true)
      "true"
      "false")))

(extend -str Nil (fn [x] "nil"))

(extend -hash Integer hash-int)

(extend -eq Integer -num-eq)

(def ordered-hash-reducing-fn
  (fn ordered-hash-reducing-fn
    ([] (new-hash-state))
    ([state] (finish-hash-state state))
    ([state itm] (update-hash-ordered! state itm))))


(extend -str PersistentVector
  (fn [v]
    (apply str "[" (conj (transduce (interpose ", ") conj v) "]"))))




(extend -str Cons
  (fn [v]
    (apply str "(" (conj (transduce (interpose ", ") conj v) ")"))))

(extend -str PersistentList
  (fn [v]
    (apply str "(" (conj (transduce (interpose ", ") conj v) ")"))))

(extend -str LazySeq
  (fn [v]
    (apply str "(" (conj (transduce (interpose ", ") conj v) ")"))))

(extend -hash PersistentVector
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))


(def stacklet->lazy-seq
  (fn [f]
    (let [val (f nil)]
      (if (identical? val :end)
        nil
        (cons val (lazy-seq* (fn [] (stacklet->lazy-seq f))))))))

(def sequence
  (fn
    ([data]
       (let [f (create-stacklet
                 (fn [h]
                   (reduce (fn ([h item] (h item) h)) h data)
                   (h :end)))]
          (stacklet->lazy-seq f)))
    ([xform data]
        (let [f (create-stacklet
                 (fn [h]
                   (transduce xform
                              (fn ([] h)
                                ([h item] (h item) h)
                                ([h] (h :end)))
                              data)))]
          (stacklet->lazy-seq f)))))

(extend -seq PersistentVector sequence)

(def concat (fn [& args] (transduce cat conj args)))

(def defn (fn [nm & rest] `(def ~nm (fn ~nm ~@rest))))
(set-macro! defn)

(defn defmacro [nm & rest]
  `(do (defn ~nm ~@rest)
       (set-macro! ~nm)
       ~nm))
(set-macro! defmacro)


(defn +
  ([] 0)
  ([x] x)
  ([x y] (-add x y))
  ([x y z] (-add x (-add y z)))
  ([x y z & rest] (-add x (-add y (-add z (reduce -add 0 rest))))))

(def inc (fn [x] (+ x 1)))

(def dec (fn [x] (- x 1)))


(def slot-tp (create-type :slot [:val]))

(defn ->Slot [x]
  (let [inst (new slot-tp)]
    (set-field! inst :val x)))

(defn get-val [inst]
  (get-field inst :val))