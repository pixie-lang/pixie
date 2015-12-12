(ns pixie.io.tcp
  (:require [pixie.stacklets :as st]
            [pixie.streams :refer [IInputStream read IOutputStream write]]
            [pixie.io.common :as common]
            [pixie.uv :as uv]
            [pixie.io.uv-common :as uv-common]
            [pixie.ffi :as ffi]))

(defrecord TCPServer [ip port on-connect uv-server bind-addr on-connection-cb]
  IDisposable
  (-dispose! [this]
    (uv/uv_close uv-server st/close_cb)
    (dispose! @on-connection-cb)
    (dispose! bind-addr)))

(deftype TCPStream [uv-client uv-write-buf]
  IInputStream
  (read [this buffer len]
    (uv-common/cb-stream-reader uv-client buffer len))
  IOutputStream
  (write [this buffer]
    (uv-common/cb-stream-writer uv-client uv-write-buf buffer))
  IDisposable
  (-dispose! [this]
    (dispose! uv-write-buf)
    (uv/uv_close uv-client st/close_cb))
  IReduce
  (-reduce [this f init]
    (common/stream-reducer this f init)))

(defn launch-tcp-client-from-server [svr]
  (assert (instance? TCPServer svr) "Requires a TCPServer as the first argument")
  (let [client (uv/uv_tcp_t)]
    (uv/uv_tcp_init (uv/uv_default_loop) client)
    (if (= 0 (uv/uv_accept (:uv-server svr) client))
      (do (st/spawn-from-non-stacklet #((:on-connect svr)
                                        (->TCPStream client (uv/uv_buf_t))))
          svr)
      (do (uv/uv_close client nil)
          svr))))

(defn tcp-server
  "Creates a TCP server on the given ip (as a string) and port (as an integer). Returns a TCPServer that can be
  shutdown with dispose!. on-connection is a function that will be passed a TCPStream for each connecting client."
  [ip port on-connection]
    (assert (string? ip) "Ip should be a string")
    (assert (integer? port) "Port should be a int")

    (let [server (uv/uv_tcp_t)
          bind-addr (uv/sockaddr_in)
          _ (uv/throw-on-error (uv/uv_ip4_addr ip port bind-addr))
          on-new-connection (atom nil)
          tcp-server (->TCPServer ip port on-connection server bind-addr on-new-connection)]
      (reset! on-new-connection
              (ffi/ffi-prep-callback
               uv/uv_connection_cb
               (fn [server status]
                 (launch-tcp-client-from-server tcp-server))))
      (uv/uv_tcp_init (uv/uv_default_loop) server)
      (uv/uv_tcp_bind server bind-addr 0)
      (uv/throw-on-error (uv/uv_listen server 128 @on-new-connection))
      (st/yield-control)
      tcp-server))


(defn tcp-client
  "Creates a TCP connection to the given ip (as a string) and port (an integer). Returns a TCPStream."
  [ip port]
  (let [client-addr (uv/sockaddr_in)
        uv-connect (uv/uv_connect_t)
        client (uv/uv_tcp_t)
        cb (atom nil)]
    (uv/throw-on-error (uv/uv_ip4_addr ip port client-addr))
    (uv/uv_tcp_init (uv/uv_default_loop) client)
    (st/call-cc (fn [k]
               (reset! cb (ffi/ffi-prep-callback
                           uv/uv_connect_cb
                           (fn [_ status]
                             (try
                               (dispose! @cb)
                               (dispose! uv-connect)
                               (dispose! client-addr)
                               (st/run-and-process k (or (st/exception-on-uv-error status)
                                                         (->TCPStream client (uv/uv_buf_t))))
                               (catch ex
                                   (println ex))))))
               (uv/uv_tcp_connect uv-connect client client-addr @cb)))))
