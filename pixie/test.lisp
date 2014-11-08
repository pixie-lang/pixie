(ns pixie.test)

(def tests (atom {}))


(def ^:dynamic *stats*)

(def ^:dynamic *current-test*)


(defmacro deftest [nm & body]
  `(do (defn ~nm []
         (print "Running: " (str (namespace (var ~nm)) "/" (name (var ~nm))))
         (try
           ~@body
           (swap! *stats* update-in [:pass] (fnil inc 0))
           (catch ex
               (print "while running " ~(name nm) " " (quote (do ~@body)))

               (swap! *stats* update-in [:fail] (fnil inc 0))
               (print (str ex))
               (swap! *stats* update-in [:errors] (fnil conj []) ex))))
       (swap! tests assoc (symbol (str (namespace (var ~nm)) "/" (name (var ~nm)))) ~nm)))



(defn run-tests []
  (push-binding-frame!)
  (set! (var *stats*) (atom {:fail 0 :pass 0}))
  (print "Running: " (count@tests) " tests")

  (foreach [test @tests]
           ((val test)))

  (let [stats @*stats*]
    (print stats)
    (pop-binding-frame!)
    stats))


(defn load-all-tests []
  (print "Looking for tests...")
  (foreach [path @load-paths]
           (print "Looking for tests in: " path)
           (foreach [desc (pixie.path/file-list path)]
                    (if (= (nth desc 1) :file)
                      (let [filename (nth desc 2)]
                        (if (pixie.string/starts-with filename "test-")
                          (if (pixie.string/ends-with filename ".lisp")
                            (let [fullpath (str (nth desc 0) "/" filename)]
                              (print "Loading " fullpath)
                              (load-file fullpath)))))))))


(defmacro assert= [x y]
  `(let [xr# ~x
         yr# ~y]
     (assert (= xr# yr#) (str (show '~x xr#) " != " (show '~y yr#)))))

(defn show
  ([val] (if (instance? String val) (-repr val) val))
  ([orig res]
     (if (= orig res)
       (show orig)
       (str (show orig) " = " (show res)))))
