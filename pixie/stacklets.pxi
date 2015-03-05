(ns pixie.stacklets
  (require pixie.uv :as uv))

;; LibUV seems to act up when we invoke a stacklet from inside a callbac
;; so we compensate by simply storing the stacklets in a task queue
;; and calling them later outside of the libuv loop.

(def stacklet-loop-h (atom nil))

(def thread-count (atom 0))

(defmulti async-fn (fn [f args k] f))

(defmethod async-fn :spawn-end
  [_ _ _]
  (swap! thread-count dec)
  (when (= @thread-count 0)
    (uv/uv_stop (uv/uv_default_loop))))

(def tasks (atom []))

(defn enqueue [q itm]
  ; TODO: Rewrite this crappy impl
  (swap! q (fn [q] (vec (conj (seq q) itm)))))

(defn dequeue [q]
  (let [itm (ith @q -1)]
    (swap! q pop)
    itm))

(comment
  (defn run-and-process [k args]

    (let [[h [op args]] (k args)]
      (async-fn op args h))))

(defn -run-and-process [k args]

    (let [[h [op args]] (k args)]
      (async-fn op args h)))

(defn run-and-process [k]
  (let [[h f] (k nil)]
    (f h)))

;; Yield

(defn switch-back [f]
  (let [[h] (@stacklet-loop-h f)]
    (reset! stacklet-loop-h h)
    nil))

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
  (switch-back (fn [k]
                 (-run-later (partial run-and-process k)))))

(def close_cb (ffi-prep-callback uv/uv_close_cb
                                 (fn [handle]
                                   (pixie.ffi/free handle)
                                   )))

(def tasks (atom []))

(defmethod async-fn :yield
  [_ args k]
  (add-item task-queue [k args]))


;;; Sleep
(defn sleep [ms]
  (let [[h] (@stacklet-loop-h [:sleep ms])]
    (reset! stacklet-loop-h h)
    nil))

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
    (switch-back f)))

(defn -spawn [start-fn]
  (switch-back (fn [k]
                 (-run-later (fn []
                              (run-and-process (new-stacklet start-fn))))
                 (-run-later (partial run-and-process k)))))

(defmacro spawn [& body]
  `(-spawn (fn [h# _]
            (try
              (reset! stacklet-loop-h h#)
              (let [result# (do ~@body)]
                (switch-back (fn [_] nil)))
              (catch e
                  (println e))))))


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
                                              (try
                                                (enqueue tasks# [k# (~return (pixie.ffi/cast req# uv/uv_fs_t))])
                                                (uv/uv_fs_req_cleanup req#)
                                                (-dispose! @cb#)
                                                (catch e (println e))))))
             (~(symbol (str "pixie.uv/uv_fs_" (name nm)))
              (uv/uv_default_loop)
              (uv/uv_fs_t)
              ~@args
              @cb#))))))


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
          (switch-back (fn [_] nil)))
        (catch e
            (println e))))))

(with-stacklets
  (dotimes [x (* 1024 10)]
    (spawn 1)))

(comment


  (dotimes [t 33]
    (-thread (fn [] (dotimes [x 10000]
                     (println t x))))))

(comment
  (defn run-later [f]
    (let [a (uv/uv_async_t)
          cb (atom nil)]
      (println "start yield")
      (reset! cb (ffi-prep-callback uv/uv_async_cb
                                    (fn [handle]
                                      (println "process yield")
                                      (f)
                                      (uv/uv_close a close_cb)
                                      (-dispose! @cb)
                                      (println "done process yield"))))
      (uv/uv_async_init (uv/uv_default_loop) a @cb)
      (uv/uv_async_send a)))

  (defn cfn [x]
    (fn []
      (println x)
      (if (pos? x)
        (run-later (cfn (dec x))))))

  (do (run-later (cfn 10000))
      (uv/uv_run (uv/uv_default_loop) uv/UV_RUN_DEFAULT)))


(comment
  ((var defuvfsfn) 'open '[path flags mode] :result)

  (defuvfsfn open [path flags mode] :result)
  (defuvfsfn read [file bufs nbufs offset] :result)
  (defuvfsfn close [file] :result))


(comment
  (defprotocol IBlockingQueue
    (add-item [this item])
    (remove-item [this]))

  (deftype BlockingQueue [items lock locked]
    IBlockingQueue
    (add-item [this item]
      (enqueue items item)
      (when @locked
        (-release-lock lock)
        (reset! locked false))
      (-yield-thread))
    (remove-item [this]
      (when (empty? @items)
        (reset! locked true)
        (-acquire-lock lock true))
      (dequeue items)))

  (defn blocking-queue []
    (let [l (-create-lock)]
      (-acquire-lock l true)
      (->BlockingQueue (atom []) l (atom true))))

  (def task-queue (blocking-queue))




)
