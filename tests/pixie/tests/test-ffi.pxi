(ns pixie.tests.test-ffi
  (require pixie.test :as t))



(t/deftest test-buffer-ffi
  (let [fp (fopen "README.md" "r")
        b (buffer 1024)]
    (t/assert= 10 (fread b 1 10 fp))
    (t/assert= 91 (nth b 0))))
