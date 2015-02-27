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
                                     (enqueue tasks [k nil])
                                     (uv/uv_timer_stop timer)
                                     (-dispose! @cb))))
     (uv/uv_timer_init (uv/uv_default_loop) timer)
     (uv/uv_timer_start timer @cb args 0))))


(defmacro defuvfsfn [nm args return]
  (let [kw (keyword (str "pixie.uv/" (name nm)))]
    `(do (defn ~nm ~args
           (let [[h# result#] (@stacklet-loop-h [~kw ~args])]
             (reset! stacklet-loop-h h#)
             result#))
         (defmethod async-fn ~kw
           [f# ~args k# tasks#]
           (let [cb# (atom nil)]
             (reset! cb# (ffi-prep-callback uv/uv_fs_cb
                                            (fn [req#]
                                              (enqueue tasks# [k# (~return req#)])
                                              (uv/uv_fs_req_cleanup req#)
                                              (-dispose! @cb#))))
             (~(symbol (str "pixie.uv/uv_fs_" (name nm)))
              (uv/uv_default_loop)
              (uv/uv_fs_t)
              ~@args
              @cb#))))))

((var defuvfsfn) 'open '[path flags mode] :result)

(defuvfsfn open [path flags mode] :result)

(keyword "foo/bar")

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
                       (enqueue tasks [wh nil])
                       (recur op arg h))
       (= op :yield) (let [_ (enqueue tasks [this_h nil])
                           [task val] (dequeue tasks)
                           [h [op arg]] (task val)]
                       (recur op arg h))
       (= op :spawn-end) (do (when (empty? @tasks)
                               (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_ONCE))
                             (if (empty? @tasks)
                               :done
                               (let [[task val] (dequeue tasks)
                                     [h [op arg]] (task val)]
                                 (recur op arg h))))
       :else (do (async-fn op arg this_h tasks)
                 (when (empty? @tasks)
                   (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_ONCE))
                 (if (empty? @tasks)
                   :done
                   (let [[task val] (dequeue tasks)
                         [h [op arg]] (task val)]
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

(with-stacklets (open "/tmp/foo-bar-baz" uv/O_WRONLY uv/O_CREAT))
