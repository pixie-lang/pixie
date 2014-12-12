(ns pixie.preload
  (require pixie.string :as s))

(defn load-all-pxi-files
  "Only used by preloading, loads all found .pxi files"
  []
  (println "Looking for pxi files...")
  (foreach [path @load-paths]
           (println "Looking for files in:" path)
           (foreach [desc (pixie.path/file-list path)]
                    (if (= (nth desc 1) :file)
                      (let [filename (nth desc 2)]
                        (if (and (pixie.string/ends-with filename ".pxi")
                                 (not (= filename "preload.pxi"))
                                 (not (= filename "stdlib.pxi")))
                          (if (pixie.string/starts-with (nth desc 0) "./pixie")
                            (let [fullpath (str (nth desc 0) "/" filename)]
                              (println "Loading" fullpath)
                              (load-file fullpath)))))))))

(load-all-pxi-files)