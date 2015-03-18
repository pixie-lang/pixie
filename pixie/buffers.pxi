(ns pixie.buffers)

(defn acopy [src src-start dest dest-start len]
  (loop [cnt 0]
    (when (< cnt len)
      (aset dest
            (+ dest-start cnt)
            (aget src (+ src-start cnt)))
      (recur (inc cnt)))))


(defprotocol IMutableBuffer
  (remove! [this])
  (add! [this])
  (full? [this]))

(defprotocol IResizableMutableBuffer
  (add-unbounded! [this val])
  (resize! [this new-size]))

(deftype RingBuffer [head tail length arr]
  IMutableBuffer
  (remove! [this]
    (when-not (zero? length)
      (let [x (aget arr tail)]
        (aset arr tail nil)
        (set-field! this :tail (int (rem (inc tail) (alength arr))))
        (set-field! this :length (dec length))
        x)))
  (add! [this x]
    (assert (< length (alength arr)))
    (aset arr head x)
    (set-field! this :head (int (rem (inc head) (alength arr))))
    (set-field! this :length (inc length))
    nil)

  (full? [this]
    (= length (alength arr)))


  IResizableMutableBuffer
  (resize! [this new-size]
    (let [new-arr (make-array new-size)]
      (cond
       (< tail head)
       (do (acopy arr tail new-arr 0 length)
           (set-field! this :tail 0)
           (set-field! this :head length)
           (set-field! this :arr new-arr))

       (> tail head)
       (do (acopy arr tail new-arr 0 (- (alength arr) tail))
           (acopy arr 0 new-arr (- (alength arr) tail) head)
           (set-field! this :tail 0)
           (set-field! this :head length)
           (set-field! this :arr new-arr))


       (full? this)
       (do (acopy arr tail new-arr 0 length)
           (set-field! this :tail 0)
           (set-field! this :head length)
           (set-field! this :arr new-arr))


       :else
       (do (set-field! this :tail 0)
           (set-field! this :head 0)
           (set-field! this :arr new-arr)))))

  (add-unbounded! [this val]
    (when (full? this)
      (resize! this (* 2 length)))
    (add! this val))

  ICounted
  (-count [this]
    length))


(defn ring-buffer [size]
  (assert (> size 0) "Can't create a ring buffer of size <= 0")
  (->RingBuffer 0 0 0 (make-array size)))


(defn fixed-buffer [size]
  (ring-buffer size))


(deftype DroppingBuffer [buf]
  IMutableBuffer
  (full? [this]
    false)
  (remove! [this]
    (remove! buf))
  (add! [this val]
    (when-not (full? buf)
      (add! buf val)))

  ICounted
  (-count [this]
    (count buf)))

(defn dropping-buffer [size]
  (->DroppingBuffer (ring-buffer size)))


(deftype SlidingBuffer [buf]
  IMutableBuffer
  (full? [this]
    false)
  (remove! [this]
    (remove! buf))
  (add! [this val]
    (when (full? buf)
      (remove! buf))
    (add! buf val))

  ICounted
  (-count [this]
    (count buf)))


(extend -reduce IMutableBuffer
        (fn [buf f acc]
          (loop [acc acc]
            (if (reduced? acc)
              @acc
              (if (pos? (count buf))
                (recur (f acc (remove! buf)))
                acc)))))
