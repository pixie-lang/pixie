(ns pixie.test.io.test-tcp
  (:require [pixie.io.tcp :refer :all]
            [pixie.async :as async]))


(tcp-server "0.0.0.0" 4242 #(println "FOOOOO " %))
