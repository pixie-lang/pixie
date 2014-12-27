(ns pixie.ffi-infer
  (require pixie.io :as io))

(defmulti emit-infer-code :op)

(defmethod emit-infer-code :constant
  [{:keys [name]}]
  (str "std::cout << \"{:name " (keyword name)" :value \" << " name
       "<< \" :type \" << TypeOf( " name ") "
       "<< \"}\" << std::endl; \n"))

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
  (str "PixieChecker::DumpType<typeof(" + name + ")>);"))

(defn start-string []
  " #include \"pixie/PixieChecker.hpp\"



      int main() {
        std::cout << \"[\";
")

(defn end-string []
  " std::cout << \"]\" << std::endl;
return 0;
      }")

(do (require pixie.io :as io )
    (io/run-command "cat /tmp/tmp.cpp"))

{:op :struct
 :name "stat"
 :interesting-fields #{:st_size}}


(io/spit "/tmp/tmp.cpp" (str (start-string)
                             (apply str (map emit-infer-code
                                             [ {:op :constant :name "RAND_MAX"}
                                               {:op :sizeof :name "int"}
                                               {:op :group
                                                :ops [ {:op :sizeof-struct :name "stat"}
                                                       {:op :offsetof-struct :struct-name "stat" :member-name "st_size"}]}]))
                                 (end-string)))

(do (io/spit "/tmp/tmp.cpp" (str (start-string)
                             (apply str (map emit-infer-code
                                             [ {:op :constant :name "RAND_MAX"}
                                               {:op :sizeof :name "int"}
                                               {:op :group
                                                :ops [ {:op :sizeof-struct :name "stat"}
                                                       {:op :struct-member-type :struct-name "stat" :member-name "st_size"}]}]))
                                 (end-string)))
    (io/run-command "c++ /tmp/tmp.cpp -o /tmp/a.out && /tmp/a.out"))

(spit )
(io/run-command "ls")
