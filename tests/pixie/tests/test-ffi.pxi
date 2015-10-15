(ns pixie.tests.test-ffi
  (require pixie.test :as t)
  (require pixie.math :as m))



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

(t/deftest test-ffi-infer
  (t/assert= 0.5 (m/asin (m/sin 0.5))))


(t/deftest test-ffi-callbacks
  (let [MAX 255
        qsort-cb (pixie.ffi/ffi-callback [CVoidP CVoidP] CInt)
        qsort (ffi-fn libc "qsort" [CVoidP CInt CInt qsort-cb] CInt)

        buf (buffer MAX)]
    (using [cb (pixie.ffi/ffi-prep-callback qsort-cb (fn [x y]
                                         (if (> (pixie.ffi/unpack x 0 CUInt8)
                                                (pixie.ffi/unpack y 0 CUInt8))
                                           -1
                                           1)))]
           (dotimes [x MAX]
             (pixie.ffi/pack! buf x CUInt8 x))
           (qsort buf MAX 1 cb)

           (dotimes [x (dec MAX)]
             (t/assert (> (pixie.ffi/unpack buf x CUInt8)
                          (pixie.ffi/unpack buf (inc x) CUInt8)))))))

(t/deftest test-size
  (t/assert= (pixie.ffi/struct-size (pixie.ffi/c-struct "struct" 1234 [])) 1234))


(t/deftest test-double-coercion
  (t/assert= (m/sin 1) (m/sin 1.0))
  (let [big (reduce * 1 (range 1 100))]
    (t/assert= (m/sin big) (m/sin (float big))))
  (t/assert= (m/sin (/ 1 2)) (m/sin (float (/ 1 2)))))
