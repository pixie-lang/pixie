(ns pixie.io.tty
  (:require [pixie.stacklets :as st]
            [pixie.streams :refer [IInputStream read IOutputStream write]]
            [pixie.uv :as uv]
            [pixie.io :as io]
            [pixie.system :as sys]
            [pixie.ffi :as ffi]))

(deftype TTYInputStream [uv-client uv-write-buf]
  IInputStream
  (read [this buffer len]
    (assert (<= (buffer-capacity buffer) len)
            "Not enough capacity in the buffer")
    (let [alloc-cb (uv/-prep-uv-buffer-fn buffer len)
          read-cb (atom nil)]
      (st/call-cc (fn [k]
                 (reset! read-cb (ffi/ffi-prep-callback
                                  uv/uv_read_cb
                                  (fn [stream nread uv-buf]
                                    (set-buffer-count! buffer nread)
                                    (try
                                      (dispose! alloc-cb)
                                      (dispose! @read-cb)
                                      ;(dispose! uv-buf)
                                      (uv/uv_read_stop stream)
                                      (st/run-and-process k (or
                                                             (st/exception-on-uv-error nread)
                                                             nread))
                                      (catch ex
                                          (println ex))))))
                 (uv/uv_read_start uv-client alloc-cb @read-cb))))))

(deftype TTYOutputStream [uv-client uv-write-buf]
  IOutputStream
  (write [this buffer]
    (let [write-cb (atom nil)
          uv_write (uv/uv_write_t)]
      (ffi/set! uv-write-buf :base buffer)
      (ffi/set! uv-write-buf :len (count buffer))
      (st/call-cc
       (fn [k]
         (reset! write-cb (ffi/ffi-prep-callback
                          uv/uv_write_cb
                          (fn [req status]
                            (try
                              (dispose! @write-cb)
                              (st/run-and-process k status)
                              (catch ex
                                  (println ex))))))
         (uv/uv_write uv_write uv-client uv-write-buf 1 @write-cb)))))

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
  (let [buf (uv/uv_buf_t)
        tty (uv/uv_tty_t)]
    (uv/uv_tty_init (uv/uv_default_loop) tty fd 0)
    (->TTYInputStream tty buf)))

(def stdin  (tty-input-stream  sys/stdin))
(def stdout (tty-output-stream sys/stdout))
(def stderr (tty-output-stream sys/stderr))
