(ns pixie.streams.utf8
  (require pixie.streams :refer :all))

(defprotocol IUTF8OutputStream
  (write-char [this char] "Write a single character to the UTF8 stream"))

(defprotocol IUTF8InputStream
  (read-char [this] "Read a single character from the UTF8 stream"))

(deftype UTF8OutputStream [out]
  IUTF8OutputStream
  (write-char [this ch]
    (let [ch (int ch)]
      (cond
       (<= ch 0x7F) (write-byte out ch)
       (<= ch 0x7FF) (do (write-byte out (bit-or 0xC0 (bit-shift-right ch 6)))
                         (write-byte out (bit-or 0x80 (bit-and ch 0x3F))))
       (<= ch 0xFFFF) (do (write-byte out (bit-or 0xE0 (bit-shift-right ch 12)))
                          (write-byte out (bit-or 0x80 (bit-and (bit-shift-right ch 6) 0x3F)))
                          (write-byte out (bit-or 0x80 (bit-and ch 0x3F))))
       (<= ch 0x1FFFFF) (do (write-byte out (bit-or 0xE0 (bit-shift-right ch 18)))
                            (write-byte out (bit-or 0x80 (bit-and (bit-shift-right ch 12) 0x3F)))
                            (write-byte out (bit-or 0x80 (bit-and (bit-shift-right ch 6) 0x3F)))
                            (write-byte out (bit-or 0x80 (bit-and ch 0x3F))))
       :else (assert false (str "Cannot encode a UTF8 character of code " ch)))))
  IDisposable
  (-dispose! [this]
    (dispose! out)))


(deftype UTF8InputStream [in bad-char]
  IUTF8InputStream
  (read-char [this]
    (let [ch (int (read-byte in))
          [n bytes error?] (cond
                            (>= 0x7F ch) [ch 1]
                            (= 0xC0 (bit-and ch 0xE0)) [(bit-and ch 31) 2 false]
                            (= 0xE0 (bit-and ch 0xF0)) [(bit-and ch 15) 3 false]
                            (= 0xF0 (bit-and ch 0xF8)) [(bit-and ch 7) 4 false]
                            (= 0xF8 (bit-and ch 0xF8)) [(bit-and ch 3) 5 true]
                            (= 0xFC (bit-and ch 0xFE)) [(bit-and ch 1) 6 true]
                            :else [n 1 true])]
      (loop [i (dec bytes)
             n n]
        (if (pos? i)
          (recur (dec i)
                 (bit-or (bit-shift-left n 6)
                         (bit-and (read-byte in) 0x3F)))
          (if error?
            (if bad-char
              bad-char
              (throw (str "Invalid UTF8 character decoded: " n)))
            (char n))))))
  IDisposable
  (-dispose! [this]
    (dispose! in)))

(defn utf8-input-stream
  "Creates a UTF8 decoder that reads characters from the given IByteInputStream. If a bad character is found
   an error will be thrown, unless an optional bad-character marker character is provided."
  ([i]
   (->UTF8InputStream i nil))
  ([i bad-char]
   (->UTF8InputStream i bad-char)))

(defn utf8-output-stream
  "Creates a UTF8 encoder that writes characters to the given IByteOutputStream."
  [o]
  (->UTF8OutputStream o))

(defn utf8-output-stream-rf [output-stream]
  (let [fp (utf8-output-stream output-stream)]
    (fn ([] 0)
      ([_] (dispose! fp))
      ([_ chr]
       (assert (char? chr))
       (write-char fp chr)
       nil))))
