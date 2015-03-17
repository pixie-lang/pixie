(ns pixie.ffi-infer
  (require pixie.io-blocking :as io))

(defn -add-rel-path [rel]
  (swap! load-paths conj (str (first @load-paths) "/" rel)))

(-add-rel-path "lib")
(-add-rel-path "include")
(-add-rel-path "../lib")
(-add-rel-path "../include")


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

(defmethod emit-infer-code :raw-struct
  [{:keys [name members]}]
  (str "std::cout << \"{:size \" << sizeof(struct " name ")"
       " << \" :infered-members [\" << "
       (apply str
              (map (fn [member]
                     (str "\"{:type  \"; PixieChecker::DumpValue((new (struct " name "))->" member "); "
                          " std::cout << \":offset \" << offsetof(struct " name ", " member ") << \" }\" << \n "))
                   members))
       "\"]}\" << std::endl;"))

(defmethod emit-infer-code :struct
  [{:keys [name members]}]
  (str "std::cout << \"{:size \" << sizeof(" name ")"
       " << \" :infered-members [\" << "
       (apply str
              (map (fn [member]
                     (str "\"{:type  \"; PixieChecker::DumpValue((new (" name "))->" member "); "
                          " std::cout << \":offset \" << offsetof(" name ", " member ") << \" }\" << \n "))
                   members))
       "\"]}\" << std::endl;"))

(defmethod emit-infer-code :callback
  [{:keys [name]}]
  (str "PixieChecker::DumpType<__typeof__(" name ")>();"))


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

(defmulti edn-to-ctype (fn [n _]
                         (:type n)))

(defn callback-type [{:keys [arguments returns]} in-struct?]
  `(ffi-callback ~(vec (map (fn [x] (edn-to-ctype x in-struct?))
                            arguments))
                 ~(edn-to-ctype returns in-struct?)))

(defmethod edn-to-ctype :pointer
  [{:keys [of-type] :as ptr} in-struct?]
  (cond
   (and (= of-type {:signed? true :size 1 :type :int})
        (not in-struct?)) 'pixie.stdlib/CCharP
   (= (:type of-type) :function) (callback-type of-type in-struct?)
   :else 'pixie.stdlib/CVoidP))

(defmethod edn-to-ctype :float
  [{:keys [size]} _]
  (cond
   (= size 8) 'pixie.stdlib/CDouble
   :else (assert False "unknown type")))

(defmethod edn-to-ctype :void
  [_ _]
  `pixie.stdlib/CVoid)

(def int-types {[8 true] 'pixie.stdlib/CInt8
                [8 false] 'pixie.stdlib/CUInt8
                [16 true] 'pixie.stdlib/CInt16
                [16 false] 'pixie.stdlib/CUInt16
                [32 true] 'pixie.stdlib/CInt32
                [32 false] 'pixie.stdlib/CUInt32
                [64 true] 'pixie.stdlib/CInt64
                [64 false] 'pixie.stdlib/CUInt64})

(defmethod edn-to-ctype :int
  [{:keys [size signed?] :as tp} _]
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
  `(def ~(symbol name)
     (ffi-fn *library* ~name
             ~(vec (map (fn [x] (edn-to-ctype x false))
                       arguments))
             ~(edn-to-ctype returns false))))

(defmethod generate-code :raw-struct
  [{:keys [name members]} {:keys [size infered-members]}]
  `(def ~(symbol name)
     (pixie.ffi/c-struct ~name ~size [~@(map (fn [name {:keys [type offset]}]
                                               `[~(keyword name) ~(edn-to-ctype type true) ~offset])
                                             members infered-members)])))

(defmethod generate-code :struct
  [{:keys [name members]} {:keys [size infered-members]}]
  `(def ~(symbol name)
     (pixie.ffi/c-struct ~name ~size [~@(map (fn [name {:keys [type offset]}]
                                               `[~(keyword name) ~(edn-to-ctype type true) ~offset])
                                             members infered-members)])))

(defmethod generate-code :type
  [{:keys [name members]} {:keys [size infered-members]}]
  `(def ~(symbol name)
     (pixie.ffi/c-struct ~name ~size [~@(map (fn [name {:keys [type offset]}]
                                               `[~(keyword name) ~(edn-to-ctype type true) ~offset])
                                             members infered-members)])))

(defmethod generate-code :callback
  [{:keys [name]} {:keys [of-type]}]
  `(def ~(symbol name)
     ~(callback-type of-type false)))


(defn run-infer [config cmds]
  (io/spit "/tmp/tmp.cpp" (str (start-string)
                               (apply str (map emit-infer-code
                                               cmds))
                               (end-string)))
  (println @load-paths)
  (let [cmd-str (str "c++ "
                     (apply str (interpose " " pixie.platform/c-flags))
                     "  /tmp/tmp.cpp "
                     (apply str (map (fn [x] ( str " -I " x " "))
                                     @load-paths))
                     (apply str " " (interpose " " (:cxx-flags *config*)))
                     " -o /tmp/a.out && /tmp/a.out")
        _ (println cmd-str)
        result (read-string (io/run-command cmd-str))
        gen (vec (map generate-code cmds result))]
    `(do ~@gen)))

(defn full-lib-name [library-name]
  (if (= library-name "c")
    pixie.platform/lib-c-name
    (str "lib" library-name "." pixie.platform/so-ext)))

(defmacro with-config [config & body]
  (binding [*config* config
            *bodies* (atom [])
            *library* (ffi-library (full-lib-name (:library config)))]
     (doseq [b body]
       (eval b))
     `(binding [*library* (ffi-library ~(full-lib-name (:library config)))]
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

(defmacro defc-raw-struct [nm members]
  `(swap! *bodies* conj (assoc {:op :raw-struct}
                          :name ~(name nm)
                          :members ~(vec (map name members))) ))

(defmacro defctype [nm members]
  `(swap! *bodies* conj (assoc {:op :type}
                          :name ~(name nm)
                          :members ~(vec (map name members))) ))

(defmacro defccallback [nm]
  `(swap! *bodies* conj (assoc {:op :callback}
                          :name ~(name nm))))


(defn compile-library [{:keys [prefix includes]} & source]
  (let [c-name (str "/tmp/" prefix ".c")
        source-header (apply str (map (fn [i]
                                        (str "#include \"" i "\"\n"))
                                      includes))
        source (apply str source-header (interpose "\n\n" source))
        lib-name (str "/tmp/" prefix "-" (hash source) "." pixie.platform/so-ext)
        cmd (str "cc -dynamic-lang "
                 c-name
                 (apply str (map (fn [x] ( str " -I " x " "))
                                 @load-paths))

                         " -o "
                         lib-name)]
    (io/spit c-name source)
    (println cmd)
    (io/run-command cmd)))




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
