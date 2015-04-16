(ns pixie.test.io.test-tcp
  (:require [pixie.io.tcp :refer :all]
            [pixie.io :refer [buffered-input-stream buffered-output-stream read-byte write-byte]]
            [pixie.streams :refer :all]
            [pixie.stacklets :as st]
            [pixie.async :as async]
            [pixie.uv :as uv]
            [pixie.test :refer :all]))

(deftest test-echo-server
  (let [client-done (async/promise)
        on-client (fn on-client [conn]
                    (let [in (buffered-input-stream conn)
                          out (buffered-output-stream conn)]
                      (try
                        (loop []
                          (let [val (read-byte in)]
                            (write-byte out val)
                            (flush out)
                            (recur)))
                        (catch ex
                            (dispose! in)
                          (dispose! out)

                          (dispose! conn)
                          (client-done true)))))

        server (tcp-server "0.0.0.0" 4242 on-client)]

    (let [client-stream (tcp-client "127.0.0.1" 4242)
          in (buffered-input-stream client-stream)
          out (buffered-output-stream client-stream)]

      (dotimes [x 255]
        (write-byte out x)
        (flush out)
        (assert= x (read-byte in)))
      (dispose! client-stream)
      (assert @client-done)
      (dispose! server))))
