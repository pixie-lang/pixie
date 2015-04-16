(ns pixie.streams)

(defprotocol IFlushableStream
  (flush [this] "Flushes all buffers in this stream and applies writes to any parent streams"))

(defprotocol IInputStream
  (read [this buffer len] "Reads multiple bytes into a buffer, returns the number of bytes read"))

(defprotocol IOutputStream
  (write [this buffer]))

(defprotocol IByteInputStream
  (read-byte [this]))

(defprotocol IByteOutputStream
  (write-byte [this byte]))

(defprotocol ISeekableStream
  (position [this])
  (seek [this position])
  (rewind [this]))
