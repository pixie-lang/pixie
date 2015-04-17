(ns io-test
  (:require [pixie.io :as io]
            [pixie.system :as sys]
            [pixie.io.tty :as tty]))

(io/write-stream tty/stdout "This is on STDOUT\n")
(io/write-stream tty/stderr "This is on STDERR\n")

(loop []
  (let [input (io/read-line tty/stdin)]
    (io/write-stream tty/stdout (str "You typed: " input "\n"))
    (recur)))
