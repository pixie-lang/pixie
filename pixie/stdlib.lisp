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
              ([xform rf coll]
                (let [f (xform rf)
                      result (-reduce coll f (f))]
                      (f result)))
              ([xform rf init coll]
                (let [f (xform rf)
                      result (-reduce coll f init)]
                      (f result)))))


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

(extend -str (type-by-name "pixie.stdlib.PersistentVector")
  (fn [v]
    (apply str "[" (conj (transduce (interpose ", ") conj v) "]"))))