(ns pixie.tests.test-channels
  (require pixie.test :refer :all)
  (require pixie.channels :refer :all)
  (require pixie.async :refer :all))


(deftest simple-read-and-write
  (let [takep (promise)
        putp (promise)
        c (chan)]
    (assert (-put! c 42 putp))
    (assert (-take! c takep))

    (assert= @takep 42)
    (assert= @putp true)))

(deftest simple-take-before-put
  (let [takep (promise)
        putp (promise)
        c (chan)]
    (assert (-take! c takep))
    (assert (-put! c 42 putp))

    (assert= @takep 42)
    (assert= @putp true)))

(deftest simple-take-before-put-with-buffers
  (let [c (chan 2)
        takesp (mapv (fn [_] (promise))
                     (range 10))
        putsp (mapv (fn [_] (promise))
                    (range 10))]
    (doseq [p takesp]
      (assert (-take! c p)))
    (dotimes [x 10]
      (assert (-put! c x (nth putsp x))))

    (doseq [p putsp]
      (assert= @p true))

    (dotimes [x 10]
      (assert= @(nth takesp x) x))))
