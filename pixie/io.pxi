(ns pixie.io)

(def fopen (ffi-fn libc "fopen" [CCharP CCharP] CVoidP))
(def fread (ffi-fn libc "fread" [CVoidP CInt CInt CVoidP] CInt))
(def fgetc (ffi-fn libc "fgetc" [CVoidP] CInt))
(def fputc (ffi-fn libc "fputc" [CInt CVoidP] CInt))
(def fwrite (ffi-fn libc "fwrite" [CVoidP CInt CInt CVoidP] CInt))
(def fclose (ffi-fn libc "fclose" [CVoidP] CInt))
(def popen (ffi-fn libc "popen" [CCharP CCharP] CVoidP))
(def pclose (ffi-fn libc "pclose" [CVoidP] CInt))


(defprotocol IInputStream
  (read-byte [this] "Read a single character")
  (read [this buffer len] "Reads multiple bytes into a buffer, returns the number of bytes read"))

(defprotocol IOutputStream
  (write-byte [this byte])
  (write [this buffer]))

(defprotocol IClosable
  (close [this] "Closes the stream"))

(def DEFAULT-BUFFER-SIZE 1024)

(deftype FileStream [fp]
  IInputStream
  (read [this buffer len]
    (assert (<= (buffer-capacity buffer) len)
            "Not enough capacity in the buffer")
    (let [read-count (fread buffer 1 len fp)]
      (set-buffer-count! buffer read-count)
      read-count))
  (read-byte [this]
    (fgetc buffer))
  IClosable
  (close [this]
    (fclose fp))
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
  IOutputStream
  (write-byte [this val]
    (assert (integer? val) "Value must be a int")
    (fputc val fp))
  (write [this buffer]
    (fwrite buffer 1 (count buffer) fp))
  IClosable
  (close [this]
    (fclose fp)))

(defn file-output-rf [filename]
  (let [fp (->FileOutputStream (fopen filename "w"))]
    (fn ([] 0)
      ([cnt] (close fp) cnt)
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
    (close c)
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
  {:doc "Open a process for reading, returning a IInputStream"
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
