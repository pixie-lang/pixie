(ns pixie.io
  (require pixie.streams :as st :refer :all)
  (require pixie.uv :as uv)
  (require pixie.stacklets :as st)
  (require pixie.ffi :as ffi))

(defmacro defuvfsfn [nm args return]
  `(defn ~nm ~args
     (let [f (fn [k#]
               (let [cb# (atom nil)]
                 (reset! cb# (ffi-prep-callback uv/uv_fs_cb
                                                (fn [req#]
                                                  (try
                                                    (st/run-and-process k# (~return (pixie.ffi/cast req# uv/uv_fs_t)))
                                                    (uv/uv_fs_req_cleanup req#)
                                                    (-dispose! @cb#)
                                                    (catch e (println e))))))
                 (~(symbol (str "pixie.uv/uv_" (name nm)))
                  (uv/uv_default_loop)
                  (uv/uv_fs_t)
                  ~@args
                  @cb#)))]
       (st/call-cc f))))

(defuvfsfn fs_open [path flags mode] :result)
(defuvfsfn fs_read [file bufs nbufs offset] :result)
(defuvfsfn fs_write [file bufs nbufs offset] :result)
(defuvfsfn fs_close [file] :result)


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
  (read-byte [this]
    (assert false "Does not support read-byte, wrap in a buffering reader"))
  IClosable
  (close [this]
    (pixie.ffi/free uvbuf)
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
  (write-byte [this val]
    (assert false))
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
  IClosable
  (close [this]
    (fclose fp)))

(deftype BufferedOutputStream [downstream idx buffer]
  IOutputStream
  (write-byte [this val]
    (pixie.ffi/pack! buffer idx CUInt8 val)
    (set-field! this :idx (inc idx))
    (when (= idx (buffer-capacity buffer))
      (set-buffer-count! buffer (buffer-capacity buffer))
      (write downstream buffer)
      (set-field! this :idx 0)))
  IClosable
  (close [this]
    (set-buffer-count! buffer idx)
    (write downstream buffer)))

(defn buffered-output-stream [downstream size]
  (->BufferedOutputStream downstream 0 (buffer size)))


(defn throw-on-error [result]
  (when (neg? result)
    (throw (uv/uv_err_name result)))
  result)

(defn open-write
  {:doc "Open a file for reading, returning a IInputStream"
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
      ([_] (close fp) nil)
      ([_ chr]
       (assert (integer? chr))
       (write-byte fp chr)
       nil))))


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
    (close c)
    result))

(println (slurp "/tmp/a.txt"))

(deftype ProcessInputStream [fp]
  IInputStream
  (read [this buffer len]
    (assert (<= (buffer-capacity buffer) len)
            "Not enough capacity in the buffer")
    (let [read-count (fread buffer 1 len fp)]
      (set-buffer-count! buffer read-count)
      read-count))
  (read-byte [this]
    (fgetc fp))
  IClosable
  (close [this]
    (pclose fp))
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


(defn popen-read
  {:doc "Open a file for reading, returning a IInputStream"
   :added "0.1"}
  [command]
  (assert (string? command) "Command must be a string")
  (->ProcessInputStream (popen command "r")))


(defn run-command [command]
  (let [c (->ProcessInputStream (popen command "r"))
        result (transduce
                 (map char)
                 string-builder
                 c)]
    (close c)
    result))
