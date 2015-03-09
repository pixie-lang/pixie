(ns pixie.stacklets
  (require pixie.uv :as uv))

;; LibUV seems to act up when we invoke a stacklet from inside a callbac
;; so we compensate by simply storing the stacklets in a task queue
;; and calling them later outside of the libuv loop.

(def stacklet-loop-h (atom nil))



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

(comment (with-stacklets
           (let [p (promise)]
             (spawn @p)
             (spawn @p)
             (spawn (p 42))
             @p)))

(comment


  (with-stacklets
    (let [f (fs_open "/tmp/foo.txt" uv/O_RDONLY uv/S_IRUSR)
          b (uv/new-fs-buf 1024)]
      (println (type (:base b)))
      (let [err (fs_read f b 1 0)]
        (println err)
        (assert (pos? err)))
      (dotimes [x 100]
        (puts (str (char (pixie.ffi/unpack (:base b) x CUInt8)))))
      (println "done"))))

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
