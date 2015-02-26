(ns pixie.stacklets
  (require pixie.uv :as uv))

(def stacklet-loop-h (atom nil))

(defn -spawn-thread [fn]
  (let [[h val] (@stacklet-loop-h [:spawn fn])]
    (reset! stacklet-loop-h h)
    (println h val)
    val))

(defn enqueue [q itm]
  ; TODO: Rewrite this crappy impl
  (vec (conj (seq q) itm)))

(defn dequeue [q]
  [(ith q -1)
   (pop q)])


(defn yield-control []
  (let [[h] (@stacklet-loop-h [:yield nil])]
    (reset! stacklet-loop-h h)
    nil))


(defmacro spawn [& body]
  `(let [f (fn [h# _]
             (reset! stacklet-loop-h h#)
             (try
               (println "spawn" h#)
                                        ;(reset! stacklet-loop-h h#)
               (let [result# (do ~@body)]
                 (println "returning " result#)
                 (@stacklet-loop-h [:spawn-end result#]))
               (catch e (println e))))
         [h# val#] (@stacklet-loop-h [:spawn f])]
     (reset! stacklet-loop-h h#)
     val#))

(defn -with-stacklets [fn]
  (let [[h [op arg]] ((new-stacklet fn) nil)]
    (println h op arg)
    (loop [op op
           arg arg
           this_h h
           tasks []]
      (println "in loop" op arg this_h tasks)
      (cond
       (= op :spawn) (let [wh (new-stacklet arg)
                           [h [op arg]] (this_h nil)]
                       (recur op arg h (enqueue tasks wh)))
       (= op :yield) (let [tasks (enqueue tasks this_h)
                           [task tasks] (dequeue tasks)
                           [h [op arg]] (task nil)]
                       (recur op arg h tasks))
       (= op :spawn-end) (if (empty? tasks)
                           arg
                           (let [[task tasks] (dequeue tasks)
                                 [h [op arg]] (task nil)]
                             (recur op arg h tasks)))
       :else (assert false (str "Unkown command " op " " arg))))))


(defmacro with-stacklets [& body]
  `(-with-stacklets
    (fn [h# _]
      (try
        (println h# _)
        (reset! stacklet-loop-h h#)
        (let [result# (do ~@body)]
          (@stacklet-loop-h [:spawn-end result#]))
        (catch e
            (println e))))))

(with-stacklets (spawn (dotimes [x 10]
                         (yield-control)
                         (println x)))
  (spawn (dotimes [x 10]
                         (yield-control)
                         (println x)))(yield-control))
