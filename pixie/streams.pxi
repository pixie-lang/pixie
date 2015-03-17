(ns pixie.streams)

(defprotocol IInputStream
  (read [this buffer len] "Reads multiple bytes into a buffer, returns the number of bytes read"))

(defprotocol IOutputStream
  (write [this buffer]))

(defprotocol IByteInputStream
  (read-byte [this]))

(defprotocol IByteOutputStream
  (write-byte [this byte]))
