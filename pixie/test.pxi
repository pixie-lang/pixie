(ns pixie.test
  (require pixie.string :as s)
  (require pixie.fs :as fs))

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
  (let [dirs      (distinct (map fs/dir @load-paths))
        pxi-files (->> dirs
                       (mapcat fs/walk-files)
                       (filter #(fs/extension? % "pxi"))
                       (filter #(s/starts-with (fs/basename %) "test-"))
                       (distinct))]
    (foreach [file pxi-files]
             (println "Loading " file)
             (load-file (fs/abs file)))))


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
