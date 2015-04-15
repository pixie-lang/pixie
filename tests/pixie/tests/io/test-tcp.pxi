(ns pixie.test.io.test-tcp
  (:require [pixie.io.tcp :refer :all]
            [pixie.io :refer [read write]]
            [pixie.stacklets :as st]
            [pixie.async :as async]))

(defn on-client [conn]
  (let [b (buffer 1024)]
    (read conn b 1024)
    (write conn b)
    (dotimes [x 1000]
      (st/yield-control))
    (println "Done Writing..")))

(tcp-server "0.0.0.0" 4242 on-client)
