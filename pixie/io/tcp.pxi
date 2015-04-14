(ns pixie.io.tcp
  (:require [pixie.stacklets :as st]
            [pixie.uv :as uv]
            [pixie.ffi :as ffi]))

(defrecord TCPServer [ip port on-connect uv-server bind-addr on-connection-cb])

(defrecord TCPStream [uv-client])

(defn launch-tcp-client-from-server [svr]
  (assert (instance? TCPServer svr) "Requires a TCPServer as the first argument")
  (let [client (uv/uv_tcp_t)]
    (uv/uv_tcp_init (uv/uv_default_loop) client)
    (if (= 0 (uv/uv_accept (:uv-server svr) client))
      (do (st/spawn-from-non-stacklet #((:on-connect svr)
                                  (->TCPStream client)))
          svr)
      (do (uv/uv_close client nil)
          svr))))



(defn tcp-server [ip port on-connection]
    (assert (string? ip) "Ip should be a string")
    (assert (integer? port) "Port should be a int")

    (let [server (uv/uv_tcp_t)
          bind-addr (uv/sockaddr_in)
          _ (uv/throw-on-error (uv/uv_ip4_addr ip port bind-addr))
          on-new-connetion (atom nil)
          tcp-server (->TCPServer ip port on-connection server bind-addr on-new-connetion)]
      (reset! on-new-connetion
              (ffi/ffi-prep-callback
               uv/uv_connection_cb
               (fn [server status]
                 (launch-tcp-client-from-server tcp-server))))
      (uv/uv_tcp_init (uv/uv_default_loop) server)
      (uv/uv_tcp_bind server bind-addr 0)
      (uv/throw-on-error (uv/uv_listen server 128 @on-new-connetion))
      (st/yield-control)
      tcp-server))
