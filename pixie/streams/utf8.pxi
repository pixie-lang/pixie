(ns pixie.streams.utf8
  (require pixie.streams :refer :all))

(defprotocol IUTF8OutputStream
  (write-char [this char]))

(defprotocol IUTF8InputStream
  (read-char [this]))

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
                            (write-byte out (bit-or 0x80 (bit-and ch 0x3F))) ))))
  IDisposable
  (-dispose! [this]
    (dispose! out)))


(deftype UTF8InputStream [in]
  IUTF8InputStream
  (read-char [this]
    (let [ch (int (read-byte in))
          [n bytes] (cond
                      (>= 0x7F ch) [ch 1]
                      (= 0xC0 (bit-and ch 0xE0)) [(bit-and ch 31) 2]
                      (= 0xE0 (bit-and ch 0xF0)) [(bit-and ch 15) 3]
                      (= 0xF0 (bit-and ch 0xF8)) [(bit-and ch 7) 4]
                      :else (assert false (str "Got bad code " ch)))]
      (loop [i (dec bytes)
             n n]
        (if (pos? i)
          (recur (dec i)
                 (bit-or (bit-shift-left n 6)
                         (bit-and (read-byte in) 0x3F)))
          (char n)))))
  IDisposable
  (-dispose! [this]
    (dispose! in)))

(defn utf8-input-stream [i]
  (->UTF8InputStream i))

(defn utf8-output-stream [o]
  (->UTF8OutputStream o))
