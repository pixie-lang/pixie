(ns pixie.stacklets
  (require pixie.uv :as uv))

;; If we don't do this, compiling this file doesn't work since the def will clear out
;; the existing value.

(if (undefined? (var stacklet-loop-h))
  (def stacklet-loop-h (atom nil)))



;; Yield

(defn run-and-process
  ([k]
   (run-and-process k nil))
  ([k val]
   (let [[h f] (k val)]
     (f h))))

(defn call-cc [f]
  (let [[h val] (@stacklet-loop-h f)]
    (reset! stacklet-loop-h h)
    val))

(defn -run-later [f]
  (let [a (uv/uv_async_t)
        cb (atom nil)]
    (reset! cb (ffi-prep-callback uv/uv_async_cb
                                  (fn [handle]
                                    (try
                                      (uv/uv_close a close_cb)
                                      (-dispose! @cb)
                                      (f)
                                      (catch ex (println ex))))))
    (uv/uv_async_init (uv/uv_default_loop) a @cb)
    (uv/uv_async_send a)))


(defn yield-control []
  (call-cc (fn [k]
             (-run-later (partial run-and-process k)))))

(def close_cb (ffi-prep-callback uv/uv_close_cb
                                 pixie.ffi/free))

;;; Sleep
(defn sleep [ms]
  (let [f (fn [k]
            (let [cb (atom nil)
                  timer (uv/uv_timer_t)]
              (reset! cb (ffi-prep-callback uv/uv_timer_cb
                                            (fn [handle]
                                              (try
                                                (run-and-process k)
                                                (uv/uv_timer_stop timer)
                                                (-dispose! @cb)
                                                (catch ex
                                                    (println ex))))))
              (uv/uv_timer_init (uv/uv_default_loop) timer)
              (uv/uv_timer_start timer @cb ms 0)))]
    (call-cc f)))

;; Spawn
(defn -spawn [start-fn]
  (call-cc (fn [k]
             (-run-later (fn []
                           (run-and-process (new-stacklet start-fn))))
             (-run-later (partial run-and-process k)))))

(defmacro spawn [& body]
  `(-spawn (fn [h# _]
            (try
              (reset! stacklet-loop-h h#)
              (let [result# (do ~@body)]
                (call-cc (fn [_] nil)))
              (catch e
                  (println e))))))




(defn -with-stacklets [fn]
  (let [[h f] ((new-stacklet fn) nil)]
    (f h)
    (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_DEFAULT)))

(defmacro with-stacklets [& body]
  `(-with-stacklets
    (fn [h# _]
      (try
        (reset! stacklet-loop-h h#)
        (let [result# (do ~@body)]
          (call-cc (fn [_] nil)))
        (catch e
            (println e))))))

(defn run-with-stacklets [f]
  (with-stacklets
    (f)))


(deftype Promise [val pending-callbacks delivered?]
  IDeref
  (-deref [self]
    (if delivered?
      val
      (do
        (call-cc (fn [k]
                   (swap! pending-callbacks conj
                          (fn [v]
                            (-run-later (partial run-and-process k v)))))))))
  IFn
  (-invoke [self v]
    (assert (not delivered?) "Can only deliver a promise once")
    (set-field! self :val v)
    (println  @pending-callbacks)
    (doseq [f @pending-callbacks]
      (f v))
    (reset! pending-callbacks nil)
    nil))

(defn promise []
  (->Promise nil (atom []) false))
