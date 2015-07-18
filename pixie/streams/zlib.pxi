(ns pixie.streams.zlib
  (:require [pixie.streams.zlib.ffi :as zlib.ffi]
            [pixie.ffi :as ffi]
            [pixie.streams :refer :all]))

(defprotocol IZStream
  (version [this])
  (set-input! [this]
    "Should be called before deflate! to set a new chunk of input
    to deflate")
  
  (full-output? [this]
    "Returns true if the ouput buffer is full of deflated (compressed) data")
  
  (reset-output-buffer! [this]
    "Make the output buffer ready to be refilled with data")
 
  (consumed-input? [this]
    "Returns true if zlib has finished reading the input-buffer") 

  (set-output-buffer-count! [this]
    "Set the buffers count so down stream can safely read the buffer")

  ;; Deflation
  (deflate-init! [this opts]
    "Set up the compression with desired parameters")

  ;; Inflation
  (inflate-init! [this opts]
    "Set up decompression with desired parameters")

  ;; In/deflate depending on what the stream has been
  ;; initialized as
  (flate! [this down-stream mode]
    "Compress/decompress")

  (flate-end!
    "Cleanup"))

(defn handle-errors! [status]
  (cond
    (= status zlib.ffi/Z_ERRNO)
    (throw [::Error "Something went wrong"])
    
    (= status zlib.ffi/Z_STREAM_ERROR)
    (throw [::Error "The stream doesn't appear to be a valid zlib/gzip stream"])

    (= status zlib.ffi/Z_DATA_ERROR)
    (throw [::Error "There was something wrong with the data"])


    ;; TODO go through the different status and show
    ;; appropriate messages
    (neg? status)
    (throw [::Error "There was something wrong with the data"])))


;; This wraps the C data structure and stores some information about
;; how its been initialized: :deflate or :inflate.
(deftype ZStream [z-stream inited]
  IZStream
  (version [this]
    (zlib.ffi/zlibVersion))

  (full-output? [this]
    (zero? (get z-stream :avail_out)))

  (consumed-input? [this]
    (zero? (get z-stream :avail_in)))

  (reset-output-buffer! [this output-buffer]
    (ffi/set! z-stream :next_out  output-buffer)
    (ffi/set! z-stream :avail_out (buffer-capacity output-buffer)))

  (set-output-buffer-count! [this output-buffer]
    (let [fill-count (- (buffer-capacity output-buffer) 
                        (get z-stream :avail_out))]
      (set-buffer-count! output-buffer fill-count)))

  (set-input! [this input-buffer]
    (ffi/set! z-stream :next_in input-buffer)
    (ffi/set! z-stream :avail_in (count input-buffer)))

  (deflate-init! [this opts]
    (assert (nil? inited) "ZStream can only be initialized once.")
    (let [status (zlib.ffi/deflateInit2_ 
                   z-stream 
                   (get opts :level zlib.ffi/Z_BEST_COMPRESSION) ;level
                   zlib.ffi/Z_DEFLATED         ;method
                   (+ 15 16)          ;window (set for gz header)
                   8                  ;memlevel
                   zlib.ffi/Z_DEFAULT_STRATEGY ;strategy
                   (version this)    ;version
                   (ffi/struct-size zlib.ffi/z_stream))]
      (assert (= zlib.ffi/Z_OK status) "Failed to initiate zstream")
      (set-field! this :inited :deflate)))

  (inflate-init! [this opts]
    (assert (nil? inited) "ZStream can only be initialized once.")
    (let [status (zlib.ffi/inflateInit2_ 
                   z-stream 
                   (+ 15 16)          ;window (set for gz header)
                   (version this)    ;version
                   (ffi/struct-size zlib.ffi/z_stream))]
      (assert (= zlib.ffi/Z_OK status) "Failed to initiate zstream")
      (set-field! this :inited :inflate)))

  (flate! [this output-buffer mode]
    (case inited
      :inflate 
      (let [status (zlib.ffi/inflate z-stream mode)]
        (handle-errors! status)
        (set-output-buffer-count! this output-buffer)
        status)

      :deflate 
      (let [status (zlib.ffi/deflate z-stream mode)]
        (handle-errors! status)
        (set-output-buffer-count! this output-buffer)
        status)

      (assert false "ZStream must be initialized before calling flate!")))
  
  (flate-end! [this]
    (case inited
      :inflate
      (zlib.ffi/inflateEnd z-stream)
      
      :deflate
      (zlib.ffi/deflateEnd z-stream)
     
      (assert false "ZStream must be initialized before calling flate-end!"))))

(defn z-stream []
  (let [z-stream (zlib.ffi/z_stream)]
    ;; Set all the callbacks to NULL so zlib uses its default ones.
    (ffi/set! z-stream :avail_in 0)
    (ffi/set! z-stream :zalloc nil)
    (ffi/set! z-stream :opaque nil)
    (ffi/set! z-stream :zfree  nil)
    (->ZStream z-stream nil)))

(deftype GZInputStream
  [up-stream input-buffer z-stream]
  IDisposable
  (-dispose! [this]
    (flate-end! z-stream))

  IInputStream
  (read [this buffer len]
    (set-buffer-count! buffer 0)
    (reset-output-buffer! z-stream buffer)
    ;; We keep reading from upstream until we have filled our output buffer
    (loop []
      (when (consumed-input? z-stream)
        ;; If z-stream has finished reading the input-buffer we last gave it,
        ;; give it a new one.
        (read up-stream input-buffer (buffer-capacity input-buffer))
        (set-input! z-stream input-buffer))
      (flate! z-stream buffer zlib.ffi/Z_NO_FLUSH)
      (if-not (empty? input-buffer)
        (if (full-output? z-stream) 
          ;; The buffer is now filled up
          (count buffer)
          ;; We can still do some more de/compression
          (recur))
        0))))

(deftype GZOutputStream
  [down-stream output-buffer z-stream]
  IOutputStream
  (write [this input-buffer]
    (set-input! z-stream input-buffer)
    (loop []
      (reset-output-buffer! z-stream output-buffer)
      (flate! z-stream output-buffer zlib.ffi/Z_NO_FLUSH)
      (when-not (empty? output-buffer)
        (write down-stream output-buffer))
      ;; if there is still more 'flating to do, do it.
      (when (full-output? z-stream)
        (recur))))

  IFlushableStream
  (flush [this]
    (loop []
      (reset-output-buffer! z-stream output-buffer)
      (flate! z-stream output-buffer zlib.ffi/Z_FINISH)
      (write down-stream output-buffer)
      (when (full-output? z-stream)
        (recur)))
    (when (satisfies? IFlushableStream down-stream)
      (flush down-stream)))

  IDisposable
  (-dispose! [this]
    (flate-end! z-stream)
    (when (satisfies? IDisposable down-stream)
      (-dispose! down-stream))))

(defn compressing-output-stream 
  "Takes a down-stream IInputStream and a buffer to store compressed chunks"
  [down-stream output-buffer opts]
  (->GZOutputStream down-stream output-buffer (deflate-init! (z-stream) opts)))

(defn decompressing-output-stream 
  "Takes a down-stream IInputStream and a buffer to store compressed chunks"
  [down-stream output-buffer opts]
  (->GZOutputStream down-stream output-buffer (inflate-init! (z-stream) opts)))

(defn decompressing-input-stream 
  "Takes a down-stream IInputStream and a buffer to store compressed chunks"
  [up-stream input-buffer opts]
  (->GZInputStream up-stream input-buffer (inflate-init! (z-stream) opts)))

(defn compressing-input-stream 
  "Takes a down-stream IInputStream and a buffer to store compressed chunks"
  [up-stream input-buffer opts]
  (->GZInputStream up-stream input-buffer (deflate-init! (z-stream) opts)))
