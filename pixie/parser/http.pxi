(ns pixie.parser.http
  (:require [pixie.parser :refer :all]))


(defn merge-rf
  ([] {})
  ([acc] acc)
  ([acc itm]
   (merge acc itm)))

(defparser HTTP-REQUEST []
  NEWLINE (and (eat \space)
               (maybe \return)
               \newline)
  NOT-NEWLINE (parse-if (complement #{\newline \return}))
  TO-END-OF-LINE (one+chars NOT-NEWLINE)
  TO-COLON (one+chars (parse-if (complement #{\newline \return \:})))

  WHITESPACE? (eat \space)

  NOT-WHITESPACE (parse-if (complement #{\space \newline \return}))

  REQUEST-LINE (and (one+chars NOT-WHITESPACE) -> method
                    WHITESPACE?
                    (one+chars NOT-WHITESPACE) -> path
                    WHITESPACE?
                    (one+chars NOT-WHITESPACE) -> protocol
                    NEWLINE
                    <- {:method method
                        :path path
                        :protocol protocol})

  HEADER        (and TO-COLON -> k
                     \:
                     WHITESPACE?
                     TO-END-OF-LINE -> v
                     NEWLINE
                     <- {k v})

  REQUEST (and REQUEST-LINE -> request
               (zero+ HEADER merge-rf) -> headers
;               \return
;               \newline
               <- (assoc request :headers headers)))

(def test-request
"GET /foo/bar http/1.1\r\nHost: foo.bar.com\r\n\r\n")

( (:REQUEST HTTP-REQUEST) (string-cursor test-request))
