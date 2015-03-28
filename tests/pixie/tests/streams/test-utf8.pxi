(ns pixie.streams.test-utf8
 (require pixie.streams.utf8 :refer :all)
 (require pixie.io :as io)
 (require pixie.test :refer :all))


(deftest test-writing-ints
  (using [os (-> (io/open-write "/tmp/pixie-utf-test.txt")
             (io/buffered-output-stream 1024)
             utf8-output-stream)]
         (dotimes [x 32000]
           (write-char os (char x))))
  (using [is (-> (io/open-read "/tmp/pixie-utf-test.txt")
               (io/buffered-input-stream 1024)
               utf8-input-stream)]
       (dotimes [x 32000]
         (assert= x (int (read-char is))))))
