(ns pixie.io)

(def fopen (ffi-fn libc "fopen" [CCharP CCharP] CVoidP))
(def fread (ffi-fn libc "fread" [CVoidP CInt CInt CVoidP] CInt))
(def fgetc (ffi-fn libc "fgetc" [CVoidP] CInt))
(def fclose (ffi-fn libc "fclose" [CVoidP] CInt))
(def popen (ffi-fn libc "popen" [CCharP CCharP] CVoidP))
(def pclose (ffi-fn libc "pclose" [CVoidP] CInt))


(defprotocol IInputStream
  (read [this] "Read a single character")
  (read-byte [this buffer len] "Reads multiple bytes into a buffer, returns the number of bytes read"))

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
    (fclose buffer))
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


(deftype ProcessInputStream [fp]
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

