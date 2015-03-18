(ns pixie.tests.test-buffers
  (require pixie.test :refer :all)
  (require pixie.buffers :refer :all))


(deftest test-adding-and-removing-from-buffer
  (let [buffer (ring-buffer 10)]
    (dotimes [x 100]
      (add! buffer x)
      (assert= x (remove! buffer)))))

(deftest test-adding-multiple-items
  (let [buffer (ring-buffer 10)]
    (dotimes [x 10]
      (add! buffer x))
    (dotimes [x 10]
      (assert= x (remove! buffer)))))

(deftest test-adding-multiple-items-with-resize
  (dotimes [y 100]
    (let [buffer (ring-buffer 2)]
      (dotimes [x y]
        (add-unbounded! buffer x))
      (dotimes [x y]
        (assert= x (remove! buffer))))))


(def drain-buffer (partial into []))

(deftest test-dropping-buffer
  (let [buf (dropping-buffer 4)]
    (dotimes [x 5]
      (println (count buf) "x" x)
      (add! buf x))
    (assert= [0 1 2 3] (drain-buffer buf))))
