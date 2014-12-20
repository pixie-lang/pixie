(ns pixie.test
  (require pixie.string :as s))

(def tests (atom {}))


(def ^:dynamic *stats*)

(def ^:dynamic *current-test*)


(defmacro deftest [nm & body]
  `(do (defn ~nm []
         (println "Running:" (str (namespace (var ~nm)) "/" (name (var ~nm))))
         (try
           ~@body
           (swap! *stats* update-in [:pass] (fnil inc 0))
           (catch ex
               (println "while running" ~(name nm) " " (quote (do ~@body)))

               (swap! *stats* update-in [:fail] (fnil inc 0))
               (println (str ex))
               (swap! *stats* update-in [:errors] (fnil conj []) ex))))
       (swap! tests assoc (symbol (str (namespace (var ~nm)) "/" (name (var ~nm)))) ~nm)))



(defn run-tests [& args]
  (push-binding-frame!)
  (set! (var *stats*) (atom {:fail 0 :pass 0}))

  (let [match (or (first args) "")
        tests (transduce (comp (filter #(>= (s/index-of (str (key %1)) match) 0))
                               (map val))
                         conj
                         @tests)]
    (println "Running:" (count tests) "tests")

    (foreach [test tests]
             (test)))

  (let [stats @*stats*]
    (println stats)
    (pop-binding-frame!)
    stats))


(defn load-all-tests []
  (println "Looking for tests...")
  (foreach [path @load-paths]
           (println "Looking for tests in:" path)
           (foreach [[dir desc filename] (pixie.path/file-list path)]
                    (if (= desc :file)
                      (if (pixie.string/starts-with filename "test-")
                        (if (pixie.string/ends-with filename ".pxi")
                          (let [fullpath (str dir "/" filename)]
                            (println "Loading" fullpath)
                            (load-file fullpath))))))))


(defmacro assert= [x y]
  `(let* [xr# ~x
          yr# ~y]
     (assert (= xr# yr#) (str (show '~x xr#) " != " (show '~y yr#)))))

(defmacro assert [x]
  `(let [x# ~x]
     (assert x# (str '~x " is " x#))))

(defn show
  ([orig res]
     (if (= orig res)
       (pr-str orig)
       (str (pr-str orig) " = " (pr-str res)))))
