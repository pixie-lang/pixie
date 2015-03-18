(ns pixie.async
  (require pixie.stacklets :as st))


(deftype Promise [val pending-callbacks delivered?]
  IDeref
  (-deref [self]
    (if delivered?
      val
      (do
        (st/call-cc (fn [k]
                   (swap! pending-callbacks conj
                          (fn [v]
                            (st/-run-later (partial st/run-and-process k v)))))))))
  IFn
  (-invoke [self v]
    (assert (not delivered?) "Can only deliver a promise once")
    (set-field! self :val v)
    (set-field! self :delivered? true)
    (doseq [f @pending-callbacks]
      (f v))
    (reset! pending-callbacks nil)
    nil))

(defn promise []
  (->Promise nil (atom []) false))

(defmacro future [& body]
  `(let [p# (promise)]
     (st/spawn (p# (do ~@body)))
     p#))
