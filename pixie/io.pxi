(ns pixie.io)

(def fopen (ffi-fn libc "fopen" [String String] VoidP))
(def fread (ffi-fn libc "fread" [Buffer Integer Integer VoidP] Integer))
(def fgetc (ffi-fn libc "fgetc" [VoidP] Integer))
(def fclose (ffi-fn libc "fclose" [VoidP] Integer))


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
