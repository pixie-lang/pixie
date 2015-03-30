;; Before Immutable Opt: 3.9 sec
;; After 3.2 sec

(defprotocol IAdder
  (add-them [this]))

(deftype Adder [a b]
  IAdder
  (add-them [this]
    (set-field! this :b (+ a b))
    b))



(def adder (->Adder 1.0 0))
(println "Starting....")
(dotimes [x (* 1024 1024 1024 20)]
  (assert (= (inc x) (add-them adder))))
(println "Ending....")
