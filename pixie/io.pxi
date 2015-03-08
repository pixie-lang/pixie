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
