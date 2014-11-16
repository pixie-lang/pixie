#!./pixie-vm

(defn greet [name]
  (print (str "Hello, " (or name "World") "!")))

(greet (first program-arguments))
