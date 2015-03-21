(ns pixie.csp
  (require pixie.stacklets :as st)
  (require pixie.buffers :as b)
  (require pixie.channels :as chans))

(def chan chans/chan)

(defn close!
  "Closes the channel, future writes will be rejected, future reads will
   drain the channel before returning nil."
  [c]
  (chans/-close! c))

(def -null-callback (fn [_] nil))

(defn put!
  "Puts the value into the channel, calling the optional callback when the operation has
   completed."
  ([c v]
   (chans/-put! c v -null-callback))
  ([c v f]
   (chans/-put! c v f)))

(defn take!
  "Takes a value from a channel, calling the provided callback when completed"
  ([c f]
   (chans/-take! c f)))

(defn >! [c v]
  (st/call-cc (fn [k]
                (chans/-put! c v (partial st/run-and-process k)))))

(defn <! [c]
  (st/call-cc (fn [k]
                (chans/-take! c (partial st/run-and-process k)))))


(defmacro go [& body]
  `(let [ret-chan# (chans/chan 1)]
     (st/spawn (put! ret-chan# (do ~@body))
               (close! ret-chan#))
     ret-chan#))


(extend -reduce chans/IReadPort
        (fn [c f init]
          (loop [acc init]
            (if (reduced? acc)
              @acc
              (let [v (<! c)]
                (if (nil? v)
                  acc
                  (recur (f acc v))))))))


(defn alts!
  ([ops]
   (st/call-cc (fn [k]
                 (chans/alts! ops (partial st/run-and-process k) {}))))
  ([ops & opts]
   (st/call-cc (fn [k]
                 (chans/alts! ops (partial st/run-and-process k) (apply hashmap opts))))))
