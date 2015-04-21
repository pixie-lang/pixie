(ns http-server
  (:require [pixie.io.tcp :as tcp]
            [pixie.streams.utf8 :as utf8]
            [pixie.io :refer [buffered-output-stream flush]]
            [pixie.parser :refer [input-stream-cursor]]
            [pixie.parser.http :as http]))

(defn send-response [conn data]
  (using [buffered (buffered-output-stream conn)
          utf-stream (utf8/utf8-output-stream buffered)]
         (utf8/write-string utf-stream (:protocol data))
         (utf8/write-char utf-stream \space)
         (utf8/write-string utf-stream (str (:status data)))
         (utf8/write-string utf-stream "\r\n\r\n")
         (utf8/write-string utf-stream (:body data))))

(defn print-headers [conn]
  (comment
    (doseq [s (slurp conn)]
      (println s (int s))))

  (println ((:REQUEST http/HTTP-REQUEST) (input-stream-cursor conn)))
  (send-response conn {:protocol "HTTP/1.0"
                       :status "200 OK"
                       :body "IT WORKS!!!!"})
  (dispose! conn)
  (println "FINISHED"))

(let [server (tcp/tcp-server "0.0.0.0" 4242 print-headers)]
  (println "Started"))
