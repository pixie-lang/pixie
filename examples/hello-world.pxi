#!./pixie-vm

(defn greet [name]
  (println (str "Hello, " (or name "World") "!")))

(greet (first program-arguments))
