(ns pixie.io
  (:require [pixie.streams :as st :refer :all]
            [pixie.io-blocking :as io-blocking]
            [pixie.uv :as uv]
            [pixie.stacklets :as st]
            [pixie.ffi :as ffi]
            [pixie.ffi-infer :as ffi-infer]))

(uv/defuvfsfn fs_open [path flags mode] :result)
(uv/defuvfsfn fs_read [file bufs nbufs offset] :result)
(uv/defuvfsfn fs_write [file bufs nbufs offset] :result)
(uv/defuvfsfn fs_close [file] :result)


(def DEFAULT-BUFFER-SIZE 1024)

(deftype FileStream [fp offset uvbuf]
  IInputStream
  (read [this buffer len]
    (assert (<= (buffer-capacity buffer) len)
            "Not enough capacity in the buffer")
    (let [_ (pixie.ffi/set! uvbuf :base buffer)
          _ (pixie.ffi/set! uvbuf :len (buffer-capacity buffer))
          read-count (fs_read fp uvbuf 1 offset)]
      (assert (not (neg? read-count)) "Read Error")
      (set-field! this :offset (+ offset read-count))
      (set-buffer-count! buffer read-count)
      read-count))
  ISeekableStream
  (position [this]
    offset)
  (rewind [this]
    (set-field! this :offset 0))
  (seek [this pos]
    (set-field! this :offset pos))
  IDisposable
  (-dispose! [this]
    (dispose! uvbuf)
    (fs_close fp))
  IReduce
  (-reduce [this f init]
    (let [buf (buffer DEFAULT-BUFFER-SIZE)
          rrf (preserving-reduced f)]
      (loop [acc init]
        (let [read-count (read this buf DEFAULT-BUFFER-SIZE)]
          (if (> read-count 0)
            (let [result (reduce rrf acc buf)]
              (if (not (reduced? result))
                (recur result)
                @result))
            acc))))))


(defn open-read
  {:doc "Open a file for reading, returning a IInputStream"
   :added "0.1"}
  [filename]
  (assert (string? filename) "Filename must be a string")
  (->FileStream (fs_open filename uv/O_RDONLY 0) 0 (uv/uv_buf_t)))


(defn read-line
  "Read one line from input-stream for each invocation.
   nil when all lines have been read"
  [input-stream]
  (let [line-feed (into #{} (map int [\newline \return]))
        buf (buffer 1)]
    (loop [acc []]
      (let [len (read input-stream buf 1)]
        (cond
          (and (pos? len) (not (line-feed (first buf))))
          (recur (conj acc (first buf)))

          (and (zero? len) (empty? acc)) nil

          :else (apply str (map char acc)))))))

(defn line-seq
  "Returns the lines of text from input-stream as a lazy sequence of strings.
   input-stream must implement IInputStream"
  [input-stream]
  (when-let [line (read-line input-stream)]
    (cons line (lazy-seq (line-seq input-stream)))))

(deftype FileOutputStream [fp offset uvbuf]
  IOutputStream
  (write [this buffer]
    (loop [buffer-offset 0]
      (let [_ (pixie.ffi/set! uvbuf :base (ffi/ptr-add buffer buffer-offset))
            _ (pixie.ffi/set! uvbuf :len (- (count buffer) buffer-offset))
            write-count (fs_write fp uvbuf 1 offset)]
        (when (neg? write-count)
          (throw (uv/uv_err_name read-count)))
        (set-field! this :offset (+ offset write-count))
        (if (< (+ buffer-offset write-count) (count buffer))
          (recur (+ buffer-offset write-count))
          write-count))))
  IDisposable
  (-dispose! [this]
    (fclose fp)))

(deftype BufferedOutputStream [downstream idx buffer]
  IByteOutputStream
  (write-byte [this val]
    (pixie.ffi/pack! buffer idx CUInt8 val)
    (set-field! this :idx (inc idx))
    (when (= idx (buffer-capacity buffer))
      (set-buffer-count! buffer (buffer-capacity buffer))
      (write downstream buffer)
      (set-field! this :idx 0)))
  IDisposable
  (-dispose! [this]
    (set-buffer-count! buffer idx)
    (write downstream buffer))
  IFlushableStream
  (flush [this]
    (set-buffer-count! buffer idx)
    (set-field! this :idx 0)
    (write downstream buffer)))

(deftype BufferedInputStream [upstream idx buffer]
  IByteInputStream
  (read-byte [this]
    (when (= idx (count buffer))
      (set-field! this :idx 0)
      (read upstream buffer (buffer-capacity buffer)))
    (let [val (nth buffer idx)]
      (set-field! this :idx (inc idx))
      val))
  IDisposable
  (-dispose! [this]
    (dispose! buffer)))

(defn buffered-output-stream
  ([downstream]
   (buffered-output-stream downstream DEFAULT-BUFFER-SIZE))
  ([downstream size]
    (->BufferedOutputStream downstream 0 (buffer size))))

(defn buffered-input-stream
  ([upstream]
   (buffered-input-stream upstream DEFAULT-BUFFER-SIZE))
  ([upstream size]
   (let [b (buffer size)]
     (set-buffer-count! b size)
     (->BufferedInputStream upstream size b))))

(defn throw-on-error [result]
  (when (neg? result)
    (throw (uv/uv_err_name result)))
  result)

(defn open-write
  {:doc "Open a file for writing, returning a IOutputStream"
   :added "0.1"}
  [filename]
  (assert (string? filename) "Filename must be a string")
  (->FileOutputStream (throw-on-error (fs_open filename
                                               (bit-or uv/O_WRONLY uv/O_CREAT)
                                               uv/S_IRWXU))
                      0
                      (uv/uv_buf_t)))


(defn file-output-rf [filename]
  (let [fp (buffered-output-stream (open-write filename)
                                   DEFAULT-BUFFER-SIZE)]
    (fn ([] 0)
      ([_] (dispose! fp))
      ([_ chr]
       (assert (integer? chr))
       (write-byte fp chr)
       nil))))

(defn stream-output-rf [output-stream]
  (let [fp (buffered-output-stream output-stream
                                   DEFAULT-BUFFER-SIZE)]
    (fn ([] 0)
      ([_] (dispose! fp))
      ([_ chr]
       (assert (integer? chr))
       (write-byte fp chr)
       nil))))

(defn write-stream [output-stream val]
  (transduce (map int)
             (stream-output-rf output-stream)
             (str val)))

(defn spit [filename val]
  (transduce (map int)
             (file-output-rf filename)
             (str val)))

(defn slurp [filename]
  (let [c (open-read filename)
        result (transduce
                (map char)
                string-builder
                c)]
    (dispose! c)
    result))

(defn run-command [command]
  (st/apply-blocking io-blocking/run-command command))


(comment
  (st/apply-blocking println "FROM OTHER THREAD <---!!!!!")


  (tcp-server "0.0.0.0" 4242 nil))
(comment
  (defmacro make-readline-async []
    `(let [libname ~(ffi-infer/compile-library {:prefix "pixie.io.readline"
                                                :includes ["uv.h" "editline/readline.h"]})]))

  (ffi-infer/compile-library))
