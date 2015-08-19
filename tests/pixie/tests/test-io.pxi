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

(t/deftest test-buffered-input-streams
  (let [f (io/buffered-input-stream (io/open-read "tests/pixie/tests/test-io.txt"))]
    (t/assert= (char (io/read-byte f)) \T)
    (t/assert= (char (io/read-byte f)) \h)
    (t/assert= (char (io/read-byte f)) \i)
    (t/assert= (char (io/read-byte f)) \s)))

(t/deftest test-buffered-input-streams-throws-on-non-input-streams
  (let [f (io/buffered-input-stream (io/open-read "tests/pixie/tests/test-io.txt"))]
    (t/assert-throws? (io/buffered-input-stream f))))

(t/deftest test-buffered-input-streams-seek
  ;; We use a buffer size of 4 because the test file isn't huge and i am terrible at
  ;; counting characters...
  (let [f (io/buffered-input-stream (io/open-read "tests/pixie/tests/test-io.txt") 4)]
    ;; Read the first word 'This'
    (t/assert= (position f) 0)
    (t/assert= (char (io/read-byte f)) \T)
    (t/assert= (position f) 1)
    (t/assert= (char (io/read-byte f)) \h)
    (t/assert= (position f) 2)
    (t/assert= (char (io/read-byte f)) \i)
    (t/assert= (position f) 3)
    (t/assert= (char (io/read-byte f)) \s)
    (t/assert= (position f) 4)

    ;; Back to start of file (this is a seek with in the buffer)
    (rewind f)

    ;; Should read the first word again
    (t/assert= (char (io/read-byte f)) \T)
    (t/assert= (position f) 1)
    (t/assert= (char (io/read-byte f)) \h)
    (t/assert= (position f) 2)
    (t/assert= (char (io/read-byte f)) \i)
    (t/assert= (position f) 3)
    (t/assert= (char (io/read-byte f)) \s)
    (t/assert= (position f) 4)

    ;; Skip the space (we will have caused a seek upstream)
    (seek f 5)

    ;; Read 'is'
    (t/assert= (position f) 5)
    (t/assert= (char (io/read-byte f)) \i)
    (t/assert= (position f) 6)
    (t/assert= (char (io/read-byte f)) \s)
    (t/assert= (position f) 7)

    ;; Jump ahead to 'file' (another seek upstream)
    (seek f 15)
    (t/assert= (position f) 15)
    (t/assert= (char (io/read-byte f)) \f)
    (t/assert= (position f) 16)
    (t/assert= (char (io/read-byte f)) \i)
    (t/assert= (position f) 17)
    (t/assert= (char (io/read-byte f)) \l)
    (t/assert= (position f) 18)
    (t/assert= (char (io/read-byte f)) \e)

    ;; Another seek with in a buffer
    (seek f 16)
    (t/assert= (position f) 16)
    (t/assert= (char (io/read-byte f)) \i)))

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
