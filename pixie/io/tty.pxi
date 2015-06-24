(ns pixie.io.tty
  (:require [pixie.stacklets :as st]
            [pixie.streams :refer [IInputStream read IOutputStream write]]
            [pixie.uv :as uv]
            [pixie.io.common :as common]
            [pixie.io.uv-common :as uv-common]
            [pixie.system :as sys]))

(deftype TTYInputStream [uv-client]
  IInputStream
  (read [this buf len]
    (uv/cb-stream-reader uv-client buf len))
  IDisposable
  (-dispose! [this]
    (uv/uv_close uv-client st/close_cb))
  IReduce
  (-reduce [this f init]
    (common/stream-reducer this f init)))

(deftype TTYOutputStream [uv-client uv-write-buf]
  IOutputStream
  (write [this buffer]
    (uv-common/cb-stream-writer uv-client uv-write-buf buffer))
  IDisposable
  (-dispose! [this]
    (dispose! uv-write-buf)
    (uv/uv_close uv-client st/close_cb)))

(defn tty-output-stream [fd]
  ;(assert (= uv/UV_TTY (uv/uv_guess_handle fd)) "fd is not a TTY")
  (let [buf (uv/uv_buf_t)
        tty (uv/uv_tty_t)]
    (uv/uv_tty_init (uv/uv_default_loop) tty fd 0)
    (->TTYOutputStream tty buf)))

(defn tty-input-stream [fd]
  ;(assert (= uv/UV_TTY (uv/uv_guess_handle fd)) "fd is not a TTY")
  (let [tty (uv/uv_tty_t)]
    (uv/uv_tty_init (uv/uv_default_loop) tty fd 0)
    (->TTYInputStream tty)))

(def stdin  (tty-input-stream  sys/stdin))
(def stdout (tty-output-stream sys/stdout))
(def stderr (tty-output-stream sys/stderr))
