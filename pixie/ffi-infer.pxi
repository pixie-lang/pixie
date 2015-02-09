(ns pixie.ffi-infer
  (require pixie.io :as io))

(def *config* nil)
(set-dynamic! (var *config*))
(def *bodies* nil)
(set-dynamic! (var *bodies*))
(def *library* nil)
(set-dynamic! (var *library*))


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
  (str "PixieChecker::DumpType<__typeof__(" name ")>(); \n"))

(defmethod emit-infer-code :struct
  [{:keys [name members]}]
  (str "std::cout << \"{:size \" << sizeof(struct " name ")"
       " << \" :infered-members [\" << "
       (apply str
              (map (fn [member]
                     (str "\"{:type  \"; PixieChecker::DumpValue((new (struct " name "))->" member "); "
                          " std::cout << \":offset \" << offsetof(struct " name ", " member ") << \" }\" << \n "))
                   members))
       "\"]}\" << std::endl;"))


(defn start-string []
  (str (apply str (map (fn [i]
                         (str "#include \"" i "\"\n"))
                       (:includes *config*)))
       "#include \"pixie/PixieChecker.hpp\"
   #include \"stdlib.h\"


      int main(int argc, char* argv[]) {
        std::cout << \"[\";
"))

(defn end-string []
  " std::cout << \"]\" << std::endl;
return 0;
      }")

;; To Ctype conversion

(defmulti edn-to-ctype :type)

(defmethod edn-to-ctype :pointer
  [{:keys [of-type] :as ptr}]
  (cond
   (= of-type {:signed? true :size 1 :type :int}) 'pixie.stdlib/CCharP
   :else 'pixie.stdlib/CVoidP))

(defmethod edn-to-ctype :float
  [{:keys [size]}]
  (cond
   (= size 8) 'pixie.stdlib/CDouble
   :else (assert False "unknown type")))


(def int-types {[8 true] 'pixie.stdlib/CInt8
                [8 false] 'pixie.stdlib/CUInt8
                [16 true] 'pixie.stdlib/CInt16
                [16 false] 'pixie.stdlib/CUInt16
                [32 true] 'pixie.stdlib/CInt32
                [32 false] 'pixie.stdlib/CUInt32
                [64 true] 'pixie.stdlib/CInt64
                [64 false] 'pixie.stdlib/CUInt64})

(defmethod edn-to-ctype :int
  [{:keys [size signed?] :as tp}]
  (let [tp-found (get int-types [(* 8 size) signed?])]
    (assert tp-found (str "No type found for " tp))
    tp-found))

;; Code Generation
(defmulti generate-code (fn [input output]
                          (:op input)))

(defmethod generate-code :const
  [{:keys [name]} {:keys [value type]}]
  `(def ~(symbol name) ~value))

(defmethod generate-code :function
  [{:keys [name]} {:keys [type arguments returns]}]
  (assert (= type :function) (str name " is not infered to be a function"))
  `(def ~(symbol name) (ffi-fn *library* ~name ~(vec (map edn-to-ctype arguments)) ~(edn-to-ctype returns))))

(defmethod generate-code :struct
  [{:keys [name members]} {:keys [size infered-members]}]
  `(def ~(symbol name)
     (pixie.ffi/c-struct ~name ~size [~@(map (fn [name {:keys [type offset]}]
                                               `[~(keyword name) ~(edn-to-ctype type) ~offset])
                                             members infered-members)])))



(defn run-infer [config cmds]
  (io/spit "/tmp/tmp.cpp" (str (start-string)
                               (apply str (map emit-infer-code
                                               cmds))
                               (end-string)))
  (let [cmd-str (str "c++ -m64 -std=c++11 /tmp/tmp.cpp -I"
                                                 (first @load-paths)
                                                 (apply str " " (interpose " " (:cxx-flags *config*)))
                                                 " -o /tmp/a.out && /tmp/a.out")
        _ (println cmd-str)
        result (read-string (io/run-command cmd-str))]
    `(do ~@(map generate-code cmds result))))

(defmacro with-config [config & body]
  (binding [*config* config
            *bodies* (atom [])
            *library* (ffi-library (str "lib" (:library config) "." pixie.platform/so-ext))]
     (doseq [b body]
       (eval b))
     `(let [*library* (ffi-library ~(str "lib" (:library config) "." pixie.platform/so-ext))]
                ~(run-infer *config* @*bodies*))))

(defmacro defcfn [nm]
  (let [name-str (name nm)]
    `(swap! *bodies* conj (assoc {:op :function} :name ~name-str))))

(defmacro defconst [nm]
  (let [name-str (name nm)]
    `(swap! *bodies* conj (assoc {:op :const} :name ~name-str))))

(defmacro defcstruct [nm members]
  `(swap! *bodies* conj (assoc {:op :struct}
                          :name ~(name nm)
                          :members ~(vec (map name members))) ))




(comment

(with-config {:library "SDL"
              :cxx-flags ["`sdl2-config --cflags --libs`"]
              :includes ["SDL.h"]
              }
  (defconst SDL_INIT_EVERYTHING)
  (defcfn SDL_Init)

  (defconst SDL_WINDOW_SHOWN))

(f/with-config {:library "c"
              :cxx-flags ["-lc"]
              :includes ["sys/stat.h"]
              }
  (f/defcstruct stat [:st_dev
                    :st_ino
                    :st_mode
                    :st_nlink
                    :st_uid
                    :st_gid
                      :st_size])
  (f/defcfn lstat64))





(let [s (stat)]
  (pixie.ffi/set! s :st_size 42)
  (println (str "\n" (:st_size s)))
  (println (str "\n" (lstat64 "/tmp/tmp.cpp" s)))
  (println "filesize " (:st_size s) " " (:st_uid s) " " (:st_gid s)))

(with-config {:library "c"
              :cxx-flags ["-lc"]
              :includes ["ctime.h"]})


(f/with-config {:library "c"
                :cxx-flags ["-lc"]
                :includes ["time.h"]
                }
  (def time_t (pixie.ffi/c-struct :time_t 8 [[:val CInt 0 ]]))
  (f/defcfn time)
  (f/defcstruct tm [:tm_sec
                    :tm_min
                    :tm_hour
                    :tm_mday
                    :tm_mon
                    :tm_year
                    :tm_wday
                    :tm_yday
                    :tm_isdst])
  (f/defcfn localtime))



(type (pixie.ffi/cast (localtime (time_t)) tm))


(let [t (time_t)
      _ (time t)
      tmi (pixie.ffi/cast (localtime t) tm)]

  (println (- (:tm_hour tmi) 12) " " (:tm_min tmi)))

  )
