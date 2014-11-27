(ns pixie.tests.test-docs
  (require pixie.test :as t))

; validate the examples in the docs by checking whether the included
; results match the actual results you get by evaluating the examples.

(defn check-examples [ns]
  (let [ns (the-ns ns)
        syms (keys (ns-map ns))]
    (doseq [sym syms]
      (let [meta (meta @(resolve sym))
            examples (get meta :examples)]
        (doseq [example examples]
          (if (contains? example 2)
            (do
              (t/assert= (eval (read-string (first example)))
                         (third example)))
            (eval (read-string (first example)))))))))

(t/deftest test-stdlib-docs
  (check-examples 'pixie.stdlib))
