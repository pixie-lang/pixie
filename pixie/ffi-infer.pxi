(ns pixie.ffi-infer
  (require pixie.io :as io))

(defmulti emit-infer-code :op)

(defmethod emit-infer-code :const
  [{:keys [name]}]
  (str "std::cout << \"{:value \" << " name " << \" :type \" "
       ";\n PixieChecker::DumpValue(" name "); \n std::cout << \"}\" << std::endl;  "))

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


(defn run-infer [config cmds]
  (io/spit "/tmp/tmp.cpp" (str (start-string)
                               (apply str (map emit-infer-code
                                               cmds))
                               (end-string)))
  (let [result (read-string (io/run-command (str "c++ /tmp/tmp.cpp -I"
                                                 (first @load-paths)
                                                 " -o /tmp/a.out && /tmp/a.out")))]
    `(do ~@(map generate-code cmds result))))


(def *config* nil)
(set-dynamic! (var *config*))
(def *bodies* nil)
(set-dynamic! (var *bodies*))


(defmacro with-config [config & body]
  `(binding [*config* ~config
             *bodies* (atom [])]
     ~@body
     (eval (run-infer *config* @*bodies*))))

(defmacro defcfn [nm]
  (let [name-str (name nm)]
    `(swap! *bodies* conj (assoc {:op :function} :name ~name-str))))

(defmacro defconst [nm]
  (let [name-str (name nm)]
    `(swap! *bodies* conj (assoc {:op :const} :name ~name-str)))  )


(comment

  (with-config {}
    (defconst RAND_MAX)
    (defcfn atof))


  )
