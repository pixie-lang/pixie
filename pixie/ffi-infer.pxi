(ns pixie.ffi-infer
  (require pixie.io :as io))

(defmulti emit-infer-code :op)

(defmethod emit-infer-code :const
  [{:keys [name]}]
  (str "std::cout << \"{:value \" << " name " << \" :type \" "
       ";\n PixieChecker::DumpValue(" name "); \n std::cout << \"}\" << std::endl;  "))

(defmethod emit-infer-code :sizeof-struct
  [{:keys [name]}]
  (str "std::cout << \"{:name " (keyword name)" :sizeof \" << sizeof(struct " name
       ") << \"}\" << std::endl; \n"))

(defmethod emit-infer-code :sizeof
  [{:keys [name]}]
  (str "std::cout << \"{:name " (keyword name)" :sizeof \" << sizeof( " name
       ") << \"}\" << std::endl; \n"))

(defmethod emit-infer-code :offsetof-struct
  [{:keys [struct-name member-name]}]
  (str "std::cout << \"{:name " (keyword member-name)" :offsetof \" << offsetof(struct " struct-name ", "
       member-name
       ") << \"}\" << std::endl; \n"))

(defmethod emit-infer-code :struct-member-type
  [{:keys [struct-name member-name]}]
  (str "std::cout << \"{:name " (keyword member-name)" :type \" << WeakTypeOf((new struct " struct-name ")->"
       member-name
       ") << \"}\" << std::endl; \n"))

(defmethod emit-infer-code :group
  [{:keys [ops]}]
  (str "std::cout << \"[\" << std::endl; "
       (apply str (map emit-infer-code ops))
       "std::cout << \"]\" << std::endl; "))

(defmethod emit-infer-code :function
  [{:keys [name]}]
  (str "PixieChecker::DumpType<typeof(" name ")>(); \n"))



(defn start-string []
  " #include \"pixie/PixieChecker.hpp\"
#include \"stdlib.h\"


      int main() {
        std::cout << \"[\";
")

(defn end-string []
  " std::cout << \"]\" << std::endl;
return 0;
      }")

;; To Ctype conversion

(defmulti edn-to-ctype :type)

(defmethod edn-to-ctype :pointer
  [{:keys [of-type] :as ptr}]
  (cond
   (= of-type {:signed? true :size 1 :type :int}) 'pixie.stdlib/CCharP))

(defmethod edn-to-ctype :float
  [{:keys [size]}]
  (cond
   (= size 8) 'pixie.stdlib/CDouble
   :else (assert False "unknown type")))

;; Code Generation
(defmulti generate-code (fn [input output]
                          (:op input)))

(defmethod generate-code :const
  [{:keys [name]} {:keys [value type]}]
  `(def ~(symbol name) ~value))

(defmethod generate-code :function
  [{:keys [name]} {:keys [type arguments returns]}]
  (assert (= type :function) (str name " is not infered to be a function"))
  `(def ~(symbol name) (ffi-fn libc ~name ~(vec (map edn-to-ctype arguments)) ~(edn-to-ctype returns))))



(io/spit "/tmp/tmp.cpp" (str (start-string)
                             (apply str (map emit-infer-code
                                             [{:op :const :name "RAND_MAX"}]))
                                 (end-string)))

(do (io/spit "/tmp/tmp.cpp" (str (start-string)
                             (apply str (map emit-infer-code
                                             [ {:op :const :name "RAND_MAX"}]))
                                 (end-string)))
    (io/run-command (str "c++ /tmp/tmp.cpp -I" (first @load-paths) " -o /tmp/a.out && /tmp/a.out"))

    )

(do (io/spit "/tmp/tmp.cpp" (str (start-string)
                             (apply str (map emit-infer-code
                                             [ {:op :const :name "RAND_MAX"}]))
                                 (end-string)))
    (read-string (io/run-command (str "c++ /tmp/tmp.cpp -I" (first @load-paths) " -o /tmp/a.out && /tmp/a.out")))

    )

(defn run-infer [cmd]
  (io/spit "/tmp/tmp.cpp" (str (start-string)
                               (apply str (map emit-infer-code
                                               [ cmd]))
                               (end-string)))
  (let [result (first (read-string (io/run-command (str "c++ /tmp/tmp.cpp -I"
                                                        (first @load-paths)
                                                        " -o /tmp/a.out && /tmp/a.out"))))]
    (println result)
    (generate-code cmd result)))

(run-infer {:op :function :name "atof"})


(defmacro defcglobal [nm]
  (run-infer {:op :const :name (name nm)}))

(defmacro deflibcfn [nm]
  (run-infer {:op :function :name (name nm)}))

(defcglobal RAND_MAX)

(deflibcfn "atof")

RAND_MAX
