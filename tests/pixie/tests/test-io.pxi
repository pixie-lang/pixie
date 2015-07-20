(ns pixie.tests.test-io
  (require pixie.test :as t)
  (require pixie.streams :as st :refer :all)
  (require pixie.streams.utf8 :as utf8 :refer :all)
  (require pixie.io :as io)
  (require pixie.streams.zlib :as zlib))

(t/deftest test-file-reduction
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (t/assert= (transduce (map identity)
                          count-rf
                          f)
               91)))

(t/deftest test-process-reduction
  (let [f (io/run-command "ls tests/pixie/tests/test-io.txt")]
    (t/assert= f "tests/pixie/tests/test-io.txt\n")))

(t/deftest test-read-into-buffer
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (let [buf (buffer 16)]
      (io/read f buf 4)
      (t/assert= (transduce (map char) string-builder buf) "This")

      (io/read f buf 4)
      (t/assert= (transduce (map char) string-builder buf) " is ")


      (io/read f buf 0)
      (t/assert= (transduce (map char) string-builder buf) "")
      
      (t/assert-throws? (io/read f buf 17))
      (t/assert-throws? (io/read f buf -2)))))

(t/deftest test-read-line
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (io/read-line f)
    (t/assert= (io/read-line f) "Second line.")
    (t/assert= (io/read-line f) nil)))

(t/deftest test-line-seq
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")
        s (io/line-seq f)]
    (t/assert= (last s) "Second line.")))

(t/deftest test-seek
  (let [f (io/open-read "tests/pixie/tests/test-io.txt")]
    (io/read-line f)
    (t/assert= (io/read-line f) "Second line.")
    (io/rewind f)
    (io/read-line f)
    (t/assert= (io/read-line f) "Second line.")
    (io/seek f (- (position f) 6))
    (t/assert= (io/read-line f) "line.")))

(t/deftest test-slurp-spit
  (let [val (vec (range 1280))]
    (io/spit "test.tmp" val)
    (t/assert= val (read-string (io/slurp "test.tmp"))))
  (t/assert-throws? (io/slurp 1))
  (t/assert-throws? (io/slurp :foo))
  (t/assert= "I love 🍺 . This is a thumbs up 👍\n" 
             (io/slurp "tests/pixie/tests/test-io-utf8.txt")))

(defn compress-content [output-stream content]
  (transduce (map identity)
             (-> output-stream
                 (zlib/compressing-output-stream (buffer 512) {})
                 (io/buffered-output-stream 1024)
                 utf8/utf8-output-stream-rf)
             (str content)))

(defn compress-and-decompress-content [output-stream content]
  (transduce (map identity)
             (-> output-stream
                 (zlib/decompressing-output-stream (buffer 512) {})
                 (zlib/compressing-output-stream (buffer 512) {})
                 (io/buffered-output-stream 1024)
                 utf8/utf8-output-stream-rf)
             (str content)))

(t/deftest test-write-compressed
  (io/run-command "rm compressed-output.gz")
  (compress-content (io/open-write "compressed-output.gz") (range 1000))
  ;; decompress the file with zcat
  (io/run-command "zcat compressed-output.gz > compressed-output.txt")
  (t/assert= (range 1000) (read-string (io/slurp "compressed-output.txt")))

  ;; Wrapping an IInputStream in decompressing-stream should get the same result
  (t/assert= (range 1000) (read-string (io/slurp 
                                         (zlib/decompressing-input-stream 
                                           (io/open-read "compressed-output.gz")
                                           (buffer 512) {})))))

;; sticking a compressor into a decompressor should result in the original data
(t/deftest test-decompression
  (compress-and-decompress-content (io/open-write "decompressed-output.txt") (range 1000))
  (t/assert= (range 1000) (read-string (io/slurp "decompressed-output.txt"))))
