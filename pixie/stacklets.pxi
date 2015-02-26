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
  (swap! q (fn [q] (vec (conj (seq q) itm)))))

(defn dequeue [q]
  (let [itm (ith @q -1)]
    (swap! q pop)
    itm))


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

(defn sleep [ms]
  (let [[h] (@stacklet-loop-h [:sleep ms])]
    (reset! stacklet-loop-h h)
    nil))

(defmulti async-fn (fn [f args k tasks] f))

(defmethod async-fn :sleep
  ([f args k tasks]
   (let [cb (atom nil)
         timer (uv/uv_timer_t)]
     (reset! cb (ffi-prep-callback uv/uv_timer_cb
                                   (fn [handle]
                                     (enqueue tasks k)
                                     (uv/uv_timer_stop timer)
                                     (-dispose! @cb))))
     (uv/uv_timer_init (uv/uv_default_loop) timer)
     (uv/uv_timer_start timer @cb args 0))))

(defn -with-stacklets [fn]
  (let [[h [op arg]] ((new-stacklet fn) nil)
        tasks (atom [])]
    (println h op arg)
    (loop [op op
           arg arg
           this_h h]
      (println "in loop" op arg this_h tasks)
      (cond
                                        ;       (= 0 (count tasks)) (uv/uv_run_loop (uv/uv_default_loop))
       (= op :spawn) (let [wh (new-stacklet arg)
                           [h [op arg]] (this_h nil)]
                       (enqueue tasks wh)
                       (println @tasks)
                       (recur op arg h))
       (= op :yield) (let [_ (enqueue tasks this_h)
                           task (dequeue tasks)
                           [h [op arg]] (task nil)]
                       (recur op arg h))
       (= op :spawn-end) (do (when (empty? @tasks)
                               (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_DEFAULT))
                             (if (empty? @tasks)
                               :done
                               (let [task (dequeue tasks)
                                     [h [op arg]] (task nil)]
                                 (recur op arg h))))
       :else (do (async-fn op arg this_h tasks)
                 (when (empty? @tasks)
                   (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_DEFAULT))
                 (if (empty? @tasks)
                   :done
                   (let [task (dequeue tasks)
                         [h [op arg]] (task nil)]
                     (recur op arg h))))
       :else (assert false (str "Unknown command " op " " arg))))))


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
                         (sleep 100)

                         (println "<- " x)))
  (spawn (dotimes [x 10]
           (sleep 100)
           (println "-> " x)))
  (yield-control))
