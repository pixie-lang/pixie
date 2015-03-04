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

(defn run-and-process [k args]
  (swap! tasks conj [k args]))

;; Yield

(defn yield-control []
  (let [[h] (@stacklet-loop-h [:yield nil])]
    (reset! stacklet-loop-h h)
    nil))

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

(defmethod async-fn :sleep
  ([f args k]
   (let [cb (atom nil)
         timer (uv/uv_timer_t)]
     (reset! cb (ffi-prep-callback uv/uv_timer_cb
                                   (fn [handle]
                                     (run-and-process k nil)
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
(comment
  ((var defuvfsfn) 'open '[path flags mode] :result)

  (defuvfsfn open [path flags mode] :result)
  (defuvfsfn read [file bufs nbufs offset] :result)
  (defuvfsfn close [file] :result))


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




(defn -with-stacklets [fn]
  (let [[h [op arg]] ((new-stacklet fn) nil)]
    (swap! thread-count inc)
    (async-fn op arg h)
    (loop []
      (let [[k args] (remove-item task-queue)]
        (-run-and-process k args)
        (recur)))))

(defn -with-stacklets [fn]
  (let [new-s (new-stacklet fn)
        [h [op arg]] (new-s nil)]
    (loop [h h
           op op
           arg arg]
      (if (not (= op :spawn-end))
        (let [[h [op arg]] (h nil)]
          (recur h op arg))))))


(defmacro with-stacklets [& body]
  `(-with-stacklets
    (fn [h# _]
      (try
        (reset! stacklet-loop-h h#)
        (let [result# (do ~@body)]
          (@stacklet-loop-h [:spawn-end result#]))
        (catch e
            (println e))))))


(with-stacklets  (dotimes [x 10000]
                     (yield-control)
                     (println x)))

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
