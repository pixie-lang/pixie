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
                         coll coll]
                    (if (reduced? init)
                      @init
                      (if (identical? coll nil)
                        init
                        (recur (f init (first coll))
                               (next coll)))))))

(extend -reduce (type-by-name "pixie.stdlib.Cons") seq-reduce)

(extend -str (type-by-name "pixie.stdlib.Bool")
  (fn [x]
    (if (identical? x true)
      "true"
      "false")))

(extend -str (type-by-name "pixie.stdlib.Nil") (fn [x] "nil"))

(extend -hash (type-by-name "pixie.stdlib.Integer") hash-int)

(def ordered-hash-reducing-fn
  (fn ordered-hash-reducing-fn
    ([] (new-hash-state))
    ([state] (finish-hash-state state))
    ([state itm] (update-hash-ordered! state itm))))


(extend -str (type-by-name "pixie.stdlib.PersistentVector")
  (fn [v]
    (apply str "[" (conj (transduce (interpose ", ") conj v) "]"))))

(extend -hash (type-by-name "pixie.stdlib.PersistentVector")
  (fn [v]
    (transduce ordered-hash-reducing-fn v)))