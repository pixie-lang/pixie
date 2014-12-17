(ns pixie.ffi-infer
  (require pixie.io :as io))

(defmulti emit-infer-code :op)

(defmethod emit-infer-code :constant
  [{:keys [name]}]
  (str "cout << \"{:name " (keyword name) " :value \" << " name " << \"}\" << std::endl; \n"))

(defn start-string []
  " #include <stdio.h>
      #include <iostream>
      int main() {
")

(defn end-string []
  " return 0;
      }")


(println (str (start-string)
              (emit-infer-code {:op :constant :name "foo"})
              (end-string)))

()
(io/run-command "ls")
