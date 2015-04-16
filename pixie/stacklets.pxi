(ns pixie.stacklets
  (:require [pixie.uv :as uv]
            [pixie.ffi :as ffi]))

;; If we don't do this, compiling this file doesn't work since the def will clear out
;; the existing value.

(when (undefined? (var stacklet-loop-h))
  (def stacklet-loop-h (atom nil))
  (def running-threads (atom 0))
  (def main-loop-running? (atom false))
  (def main-loop-lock (-create-lock))
  (-acquire-lock main-loop-lock true))



;; Yield

(defrecord ThrowException [ex])

(defn run-and-process
  ([k]
   (run-and-process k nil))
  ([k val]
   (let [[h f] (k val)]
     (f h))))

(defn exception-on-uv-error [result]
  (when (neg? result)
    (->ThrowException (str "UV Error: " (uv/uv_err_name result)))))


(defn call-cc [f]
  (let [frames (-get-current-var-frames nil)
        [h val] (@stacklet-loop-h f)]
    (reset! stacklet-loop-h h)
    (-set-current-var-frames nil frames)
    (if (instance? ThrowException val)
      (throw (:ex val))
      val)))

(defn -run-later [f]
  (let [a (uv/uv_async_t)
        cb (atom nil)]
    (reset! cb (ffi/ffi-prep-callback uv/uv_async_cb
                                  (fn [handle]
                                    (try
                                      (uv/uv_close a close_cb)
                                      (-dispose! @cb)
                                      (f)
                                      (catch ex (println ex))))))
    (uv/uv_async_init (uv/uv_default_loop) a @cb)
    (uv/uv_async_send a)
    (when (not @main-loop-running?)
      (reset! main-loop-running? true)
      (-release-lock main-loop-lock))
    nil))


(defn yield-control []
  (call-cc (fn [k]
             (-run-later (partial run-and-process k)))))

(def close_cb (ffi/ffi-prep-callback uv/uv_close_cb
                                 pixie.ffi/dispose!))

;;; Sleep
(defn sleep [ms]
  (let [f (fn [k]
            (let [cb (atom nil)
                  timer (uv/uv_timer_t)]
              (reset! cb (ffi/ffi-prep-callback uv/uv_timer_cb
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
  `(let [frames (-get-current-var-frames nil)]
     (-spawn (fn [h# _]
               (-set-current-var-frames nil frames)
               (try
                 (swap! running-threads inc)
                 (reset! stacklet-loop-h h#)
                 (let [result# (do ~@body)]
                   (swap! running-threads dec)
                   (call-cc (fn [_] nil)))
                 (catch e
                     (println e)))))))


(defn spawn-from-non-stacklet [f]
  (let [s (new-stacklet (fn [h _]
                          (try
                            (reset! stacklet-loop-h h)
                            (swap! running-threads inc)
                            (f)
                            (swap! running-threads dec)
                            (call-cc (fn [_] nil))
                            (catch e
                                (println e)))))]
    (-run-later
     (fn []
       (run-and-process s)))))


(defn -with-stacklets [fn]
  (swap! running-threads inc)
  (reset! main-loop-running? true)
  (let [[h f] ((new-stacklet fn) nil)]
    (f h)
    (loop []
      (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_DEFAULT)
      (when (> @running-threads 0)
        (reset! main-loop-running? false)
        (-acquire-lock main-loop-lock true)
        (recur)))))

(defmacro with-stacklets [& body]
  `(-with-stacklets
    (fn [h# _]
      (try
        (reset! stacklet-loop-h h#)
        (let [result# (do ~@body)]
          (swap! running-threads dec)
          (call-cc (fn [_] nil)))
        (catch e
            (println e))))))

(defn run-with-stacklets [f]
  (with-stacklets
    (f)))

(defprotocol IThreadPool
  (-execute [this work-fn]))

;; Super basic Thread Pool, yes, this should be improved

(deftype ThreadPool []
  IThreadPool
  (-execute [this work-fn]
    (-thread (fn [] (work-fn)))))

(def basic-thread-pool (->ThreadPool))

(defn -run-in-other-thread [work-fn]
  (-execute basic-thread-pool work-fn))


(defn apply-blocking [f & args]
  (call-cc (fn [k]
             (-run-in-other-thread
              (fn []
                (let [result (apply f args)]
                  (-run-later (fn [] (run-and-process k result)))))))))
