(ns pixie.io-blocking
  (:require [pixie.streams :as st :refer :all]
            [pixie.io.common :as common]))


(def fopen (ffi-fn libc "fopen" [CCharP CCharP] CVoidP))
(def fseek (ffi-fn libc "fseek" [CVoidP CInt CInt] CInt))
(def ftell  (ffi-fn libc "ftell" [CVoidP] CInt))
(def -rewind (ffi-fn libc "rewind" [CVoidP] CVoidP))
(def fread (ffi-fn libc "fread" [CVoidP CInt CInt CVoidP] CInt))
(def fgetc (ffi-fn libc "fgetc" [CVoidP] CInt))
(def fputc (ffi-fn libc "fputc" [CInt CVoidP] CInt))
(def fwrite (ffi-fn libc "fwrite" [CVoidP CInt CInt CVoidP] CInt))
(def fclose (ffi-fn libc "fclose" [CVoidP] CInt))
(def popen (ffi-fn libc "popen" [CCharP CCharP] CVoidP))
(def pclose (ffi-fn libc "pclose" [CVoidP] CInt))


(deftype FileStream [fp]
  IInputStream
  (read [this buffer len]
    (assert (>= (buffer-capacity buffer) len)
            "Not enough capacity in the buffer")
    (let [read-count (fread buffer 1 len fp)]
      (set-buffer-count! buffer read-count)
      read-count))
  (read-byte [this]
    (fgetc buffer))
  ISeekableStream
  (seek [this pos]
    (fseek fp pos 0))
  (rewind [this]
    (-rewind fp))
  IDisposable
  (-dispose! [this]
    (fclose fp))
  IReduce
  (-reduce [this f init]
    (common/stream-reducer this f init)))

(defn open-read
  {:doc "Open a file for reading, returning a IInputStream"
   :added "0.1"}
  [filename]
  (assert (string? filename) "Filename must be a string")
  (->FileStream (fopen filename "r")))

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

(deftype FileOutputStream [fp]
  IByteOutputStream
  (write-byte [this val]
    (assert (integer? val) "Value must be a int")
    (fputc val fp))
  IOutputStream
  (write [this buffer]
    (fwrite buffer 1 (count buffer) fp))
  IDisposable
  (-dispose! [this]
    (fclose fp)))

(defn file-output-rf [filename]
  (let [fp (->FileOutputStream (fopen filename "w"))]
    (fn ([] 0)
      ([cnt] (dispose! fp) nil)
      ([cnt chr]
       (assert (integer? chr))
       (let [written (write-byte fp chr)]
         (if (= written 0)
           (reduced cnt)
           (+ cnt written)))))))

(defn spit [filename val]
  (transduce (map int)
             (file-output-rf filename)
             (str val)))

(defn slurp [filename]
  (let [c (->FileStream (fopen filename "r"))
        result (transduce
                (map char)
                string-builder
                c)]
    (dispose! c)
    result))

(defn slurp-stream [stream]
  (let [c stream
        result (transduce
                (map char)
                string-builder
                c)]
    (dispose! c)
    result))

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
  IDisposable
  (-dispose! [this]
    (pclose fp))
  IReduce
  (-reduce [this f init]
    (common/stream-reducer this f init)))

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
    (dispose! c)
    result))
