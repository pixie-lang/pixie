(ns pixie.io
  (:require [pixie.streams :as st :refer :all]
            [pixie.streams.utf8 :as utf8]
            [pixie.io-blocking :as io-blocking]
            [pixie.io.common :as common]
            [pixie.uv :as uv]
            [pixie.stacklets :as st]
            [pixie.ffi :as ffi]
            [pixie.ffi-infer :as ffi-infer]))

(uv/defuvfsfn fs_open [path flags mode] :result)
(uv/defuvfsfn fs_read [file bufs nbufs offset] :result)
(uv/defuvfsfn fs_write [file bufs nbufs offset] :result)
(uv/defuvfsfn fs_close [file] :result)

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
    (common/stream-reducer this f init)))

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
          (throw [::FileOutputStreamException (uv/uv_err_name write-count)]))
        (set-field! this :offset (+ offset write-count))
        (if (< (+ buffer-offset write-count) (count buffer))
          (recur (+ buffer-offset write-count))
          write-count))))
  IDisposable
  (-dispose! [this]
    (fs_close fp)))

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
    (write downstream buffer)
    (flush this))
  IFlushableStream
  (flush [this]
    (set-buffer-count! buffer idx)
    (set-field! this :idx 0)
    (write downstream buffer)
    (when (satisfies? IFlushableStream downstream)
      (flush downstream))))

(deftype BufferedInputStream [upstream idx buffer]
  IByteInputStream
  (read-byte [this]
    (when (= idx (count buffer))
      (set-field! this :idx 0)
      (read upstream buffer (buffer-capacity buffer)))
    (when (pos? (count buffer))
      (let [val (nth buffer idx)]
        (set-field! this :idx (inc idx))
        val)))
  ISeekableStream
  (position [this]
    (+ (- (position upstream) 
          (count buffer))
       idx))
  (rewind [this]
    (seek this 0))
  (seek [this pos]
    ;; We can be clever about seeking. If we are seeking to somewhere with in
    ;; our current buffer, we can avoid seeking in upstream.
    (let [upper-bounds (position upstream)
          lower-bounds (- upper-bounds (count buffer))]
      (if (and (>= pos lower-bounds)
               (<= pos upper-bounds))
        ;; We're in the buffer window :-)
        (set-field! this :idx (- pos lower-bounds))
        ;; Put the index at the end of the buffer to force a read from upstream
        (do
          (set-field! this :idx (count buffer))
          (seek upstream pos)))))
  IDisposable
  (-dispose! [this]
    (dispose! buffer)))

(defn buffered-output-stream
  ([downstream]
   (buffered-output-stream downstream common/DEFAULT-BUFFER-SIZE))
  ([downstream size]
    (->BufferedOutputStream downstream 0 (buffer size))))

(defn buffered-input-stream
  ([upstream]
   (buffered-input-stream upstream common/DEFAULT-BUFFER-SIZE))
  ([upstream size]
   (let [b (buffer size)]
     (set-buffer-count! b size)
     (->BufferedInputStream upstream size b))))

(defn throw-on-error [result]
  (when (neg? result)
    (throw [::UVException (uv/uv_err_name result)]))
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

(defn spit 
  "Writes the content to output. Output must be a file or an IOutputStream."
  [output content]
  (cond
    (string? output)
    (transduce (map identity)
               (-> output
                   open-write
                   buffered-output-stream
                   utf8/utf8-output-stream-rf)
               (str content))
    
    (satisfies? IOutputStream output)
    (transduce (map identity)
               (-> output
                   buffered-output-stream
                   utf8/utf8-output-stream-rf)
               (str content))
    
    :else (throw [::Exception "Expected a string or IOutputStream"])))

(defn slurp 
  "Reads in the contents of input. Input must be a filename or an IInputStream"
  [input]
  (let [stream (cond
                 (string? input) (open-read input)
                 (satisfies? IInputStream input) input
                 :else (throw [:pixie.io/Exception "Expected a string or an IInputStream"]))
        result (transduce
                 (map char)
                 string-builder
                 (-> stream
                     buffered-input-stream
                     utf8/utf8-input-stream))]
      (dispose! stream)
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
