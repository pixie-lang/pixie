(ns pixie.channels
  (require pixie.stacklets :as st)
  (require pixie.buffers :as b))

(defprotocol ICancelable
  (-canceled? [this] "Determines if a request (such as a callback) that can be canceled")
  (-commit! [this]))

(defprotocol IReadPort
  (-take! [this cfn] "Take a value from this port passing it to a cancellable function"))

(defprotocol IWritePort
  (-put! [this itm cfn] "Write a value to this port passing true if the write succeeds and the
                         callback isn't canceled"))

(defprotocol ICloseable
  (-close! [this] "Closes the channel, future writes will be rejected, future reads will
                   drain the channel before returning nil."))

(deftype OpCell [val cfn]
  IIndexed
  (-nth [this idx]
    (cond
     (= idx 0) val
     (= idx 1) cfn
     :else (throw "Index out of range")))
  (-nth-not-found [this idx not-found]
    (cond
     (= idx 0) val
     (= idx 1) cfn
     :else not-found))
  ICounted
  (-count [this]
    2)
  ICancelable
  (-canceled? [this]
    (canceled? cfn)))

(defn canceled? [this]
  (-canceled? this))


(defn -move-puts-to-buffer [puts buffer]
  (loop []
    (if (or (b/full? buffer)
            (b/empty-buffer? puts))
      nil
      (let [[val cfn] (b/remove! puts)]
        (if (cancelled? cfn)
          (recur)
          (do (st/-run-later (partial cfn true))
              (b/add! buffer val)
              (recur)))))))

(defn -get-non-canceled! [buffer]
  (loop []
    (if (b/empty-buffer? buffer)
      nil
      (let [v (b/remove! buffer)]
        (if (canceled? v)
          (recur)
          v)))))


(deftype MultiReaderWriterChannel [puts takes buffer closed? ops-since-last-clean]
  IReadPort
  (-take! [this cfn]
    (if (canceled? cfn)
      false
      (if (and closed?
               (b/empty-buffer? buffer)
               (b/empty-buffer? puts))
        (do (-commit! cfn)
            (st/-run-later (partial cfn nil))
            false)
        (if (not (b/empty-buffer? buffer))
          (do (-commit! cfn)
              (st/-run-later (partial cfn (b/remove! buffer)))
              (-move-puts-to-buffer puts buffer))

          (if-let [[v pcfn] (-get-non-canceled! puts)]
            (do (-commit! pcfn)
                (-commit! cfn)
                (st/-run-later (partial pcfn true))
                (st/-run-later (partial cfn v))
                true)
            (do (set-field! this :ops-since-last-clean (inc ops-since-last-clean))
                (b/add-unbounded! takes cfn)
                true))))))
  IWritePort
  (-put! [this val cfn]
    (if (or (canceled? cfn))
      false
      (if closed?
        (do (-commit! cfn)
            (st/-run-later (partial cfn false))
            false)
        (if-let [tfn (-get-non-canceled! takes)]
          (do (-commit! cfn)
              (-commit! tfn)
              (st/-run-later (partial tfn val))
              (st/-run-later (partial cfn true))
              true)
          (if (not (b/full? buffer))
            (do (b/add! buffer val)
                (-commit! cfn)
                (st/-run-later (partial cfn true))
                true)
            (do (b/add-unbounded! puts (->OpCell val cfn))
                (set-field! this :ops-since-last-clean (inc ops-since-last-clean))
                true))))))
  ICloseable
  (-close! [this]
    (set-field! this :closed? true)
    (when (not (b/empty-buffer? takes))
      (loop []
        (when-let [tfn (-get-non-canceled! takes)]
          (-commit! tfn)
          (st/-run-later (partial tfn nil))
          (recur))))))

(defn chan
  "Creates a CSP channel with the given buffer. If an integer is provided as the argument
   creates a channel with a fixed buffer of that size. "
  ([]
   (chan 0))
  ([size-or-buffer]
    (if (= 0 size-or-buffer)
      (->MultiReaderWriterChannel (b/ring-buffer 8)
                                  (b/ring-buffer 8)
                                  b/null-buffer
                                  false
                                  0)
      (if (integer? size-or-buffer)
        (->MultiReaderWriterChannel (b/ring-buffer 8)
                                    (b/ring-buffer 8)
                                    (b/fixed-buffer size-or-buffer)
                                    false
                                    0)
        (->MultiReaderWriterChannel (b/ring-buffer 8)
                                    (b/ring-buffer 8)
                                    size-or-buffer
                                    false
                                    0)))))

(deftype AltHandler [atm f]
  ICancelable
  (-canceled? [this]
    @atm)
  (-commit! [this]
    (reset! atm true))
  IFn
  (-invoke [this & args]
    (apply f args)))

(defn alt-handlers [fns]
  (mapv (partial ->AltHandler (atom false)) fns))

(extend -canceled? IFn
        (fn [this] false))

(extend -commit! IFn
        (fn [this] nil))
