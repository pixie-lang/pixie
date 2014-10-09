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

(extend -reduce (type-by-name "pixie.stdlib.Cons") seq-reduce)
(extend -reduce (type-by-name "pixie.stdlib.Array") indexed-reduce)

(extend -str (type-by-name "pixie.stdlib.Bool")
  (fn [x]
    (if (identical? x true)
      "true"
      "false")))

(extend -str (type-by-name "pixie.stdlib.Nil") (fn [x] "nil"))

(extend -hash (type-by-name "pixie.stdlib.Integer") hash-int)

(extend -eq (type-by-name "pixie.stdlib.Integer") -num-eq)

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


(def + (fn + [& rest] (reduce -add 0 rest)))


(def doit (fn []
            (let [a (create-stacklet (fn [h v] (h 42)))
                  b (create-stacklet (fn [h v] (h (a 0))))]
                  (b 4))))