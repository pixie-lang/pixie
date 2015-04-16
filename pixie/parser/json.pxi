(ns pixie.parser.json
  (:require [pixie.parser :refer :all]
            [pixie.stdlib :as std]))



;; Basic numeric parser. Supports integers (1, 2, 43), decimals (0.1, 1.1, 1000.11) and exponents (1e42, 1E-2)
(defparser NumberParser []
  NUMBER (and (maybe \-)
              -> sign

              (or (and
                   (parse-if (set "123456789")) -> first
                   (zero+chars digits) -> rest
                   <- (str first rest))
                  (and \0 <- "0"))
              -> integer-digits

              (maybe (and \.
                          (one+chars digits) -> digits
                          <- digits))
              -> fraction-digits


              (maybe (and (parse-if (set "eE"))
                          (maybe (parse-if (set "-+"))) -> exp-sign
                          (one+chars digits) -> exp-digits
                          <- [(std/or exp-sign "") exp-digits]))
              -> exp-data

              <- (std/read-string (str (std/or sign "")
                                   integer-digits
                                   (if fraction-digits (str "." fraction-digits) "")
                                   (if exp-data (apply str "E" exp-data) "")))))

(def valid-escape-chars
  {\\ \\
   \" \"
   \/ \/
   \b \backspace
   \f \formfeed
   \n \newline
   \r \return
   \t \tab})


;; Defines a JSON escaped string parser. Supports all the normal \n \f \r stuff as well
;; as \uXXXX unicode characters
(defparser EscapedStringParser []
  CHAR (or (and \\
                (one-of valid-escape-chars) -> char
                <- (valid-escape-chars char))

           (and \\
                \u
                digits -> d1
                digits -> d2
                digits -> d3
                digits -> d4
                <- (char (std/read-string (str "0x" d1 d2 d3 d4))))

           (parse-if #(not= % \")))

  STRING (and \"
              (zero+chars CHAR) -> s
              \"
              <- s))

;; Basic JSON parser
(defparser JSONParser  [NumberParser EscapedStringParser]

  NULL (sequence "null" <- nil)
  TRUE (sequence "true" <- true)
  FALSE (sequence "false" <- false)
  ARRAY (and \[
             (eat whitespace)
             (zero+ (and ENTRY -> e
                         (maybe \,)
                         <- e)) -> items
                         (eat whitespace)
                         (eat whitespace)
                         \]
                         <- items)
  MAP-ENTRY (and (eat whitespace)
                 STRING -> key
                 (eat whitespace)
                 \:
                 ENTRY -> value
                 (maybe \,)
                 <- [key value])
  MAP (and \{
           (zero+ MAP-ENTRY) -> items
           (eat whitespace)
           \}
           <- (apply hashmap (apply concat items)))
  ENTRY (and
         (eat whitespace)
         (or NUMBER MAP STRING NULL TRUE FALSE ARRAY) -> val
         (eat whitespace)
         <- val)
  ENTRY-AT-END (and ENTRY -> e
                    (eat whitespace)
                    end
                    <- e))

(defn read-string [s]
  (let [c (string-cursor s)
        result ((:ENTRY-AT-END JSONParser) c)]
    (if (failure? result)
      (println (current c) (snapshot c))
      result)))
