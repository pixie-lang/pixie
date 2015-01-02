(ns pixie.tests.test-ffi
  (require pixie.test :as t))



(t/deftest test-buffer-ffi
  (let [fp (fopen "README.md" "r")
        b (buffer 1024)]
    (t/assert= 10 (fread b 1 10 fp))
    (t/assert= 91 (nth b 0))))

(t/deftest test-arity-check
  (let [sscanf-2 (ffi-fn libc "sscanf" [CCharP CCharP] CInt)
        sscanf-* (ffi-fn libc "sscanf" [CCharP CCharP] CInt :variadic? true)]
    (try
      (sscanf-2 "too few arguments")
      (t/assert false)
      (catch ex (t/assert= (type ex) RuntimeException)))

    (try
      (sscanf-2 "too" "many" "arguments")
      (t/assert false)
      (catch ex (t/assert= (type ex) RuntimeException)))

    (try
      (sscanf-* "too few arguments")
      (t/assert false)
      (catch ex (t/assert= (type ex) RuntimeException)))

    (sscanf-2 "string" "fmt")
    (sscanf-* "string" "fmt")
    (sscanf-* "string" "fmt" "optional arg1" "optional arg2")
    (t/assert true)))
