(ns pixie.fs
  (:require [pixie.path :as path]
            [pixie.string :as string]
            [pixie.uv :as uv]))

(defprotocol IFSPath
  (path [this]
    "Returns the path used to reference the File/Dir/Filesystem Object")

  (rel [this other]
    "Returns the path relative to the other path")

  (abs [this]
    "Returns the absolute path")

  (exists? [this]
    "Returns true if the file exists")

  (basename [this]
    "Returns the basename of the Filesystem Object")

  (permissions [this]
    "Returns a string of the octal permissions")

  (size [this]
    "Returns the size of the file/dir on disk")

  ;; TODO

  (mounted? [this]
    "Returns true if the directory is a mounted"))

(defprotocol IFile
  (extension [this]
    "Returns the extension")

  (extension? [this ext]
    "Returns true if file has extension")

  ;; TODO
  (touch [this]
    "Create the file if it doesn't exist."))

(defprotocol IDir
  (list [this]
    "List files and dirs underneath")

  (empty? [this]
    "Returns true if directory is not empty")

  (walk [this]
    "Recursively returns all files and directories below")

  (walk-files [this]
    "Recursively returns all files underneath")

  (walk-dirs [this]
    "Recursivley returns all directories underneath"))

(defn rel-path [a b]
  (let [paths-a (string/split (abs a) "/")
        paths-b (string/split (abs b) "/")
        ;; Get the common root of the two paths and the bits that diverge
        [common diff-a diff-b] (loop [ra paths-a rb paths-b common []]
                                 (let [ca (first ra)
                                       cb (first rb)]
                                   (if (and ca cb (= ca cb))
                                     (recur (rest ra) (rest rb) (conj common ca))
                                     [common ra rb])))]
    (let [level (- (count diff-a) (count diff-b))]
      (cond
        ;; Same level
        (and (zero? (count diff-a)) (zero? (count diff-b)))
        "."

        ;; If B diverges by one level and a is a Dir we use ".."
        (and (= 1 (count diff-b)) (instance? Dir a))
        ".."

        ;; In all other cases we want to go back to the root,
        :else
        (apply str (interpose "/" (concat (repeat (count diff-b) "..") diff-a)))))))

(defn- assert-existence [f]
    (assert (exists? f) (str "No file or directory at \"" (abs f) "\"")))

(uv/defuvfsfn fs-size pixie.uv/uv_fs_stat [file] :statbuf.st_size)
(uv/defuvfsfn fs-mode pixie.uv/uv_fs_stat [file] :statbuf.st_mode)

(defn- size-of-path [path]
  (assert-existence path)
  (fs-size (abs path)))

(defn- permission-string [n]
  (apply str
         (for [shift [6 3 0]]
           (let [mask (bit-shift-left 7 shift)
                 masked (bit-and mask n)]
             (bit-shift-right masked shift)))))

(defn- permissions-of-path [path]
  (assert-existence path)
  (permission-string (fs-mode (abs path))))

;; File and Dir are just wrappers around paths.
(deftype File [pathz]
  IFSPath
  (path [this] pathz)
  (rel [this other]
    (if (satisfies? IFSPath other)
      (rel-path this other)
      (throw "Second argument must satisfy IFSPath")))

  (abs [this]
    (path/-abs pathz))

  (exists? [this]
    (path/-exists? pathz))

  (basename [this]
    (last (string/split (abs this) "/")))

  (size [this]
    (size-of-path this))

  (permissions [this]
    (permissions-of-path this))

  IFile
  ;; TODO: Sort out regex or make strings partitionable. So we can split at
  ;; #".".
  (extension [this]
    (last (string/split (abs this) ".")))

  (extension? [this ext]
    (string/ends-with? (abs this) ext))

  IObject
  (-hash [this]
    (hash (abs this)))

  (-eq [this other]
    (if (instance? File other)
      (= (abs this) (abs other))
      false))

  (-str [this]
    (str (abs this)))

  (-repr [this]
    (str "<File " (str this) ">")))

(deftype Dir [pathz]
  IFSPath
  (path [this] pathz)

  (rel [this other]
    (if (satisfies? IFSPath other)
      (rel-path this other)
      (throw "Second argument must satisfy IFSPath")))

  (abs [this]
    (path/-abs pathz))

  (exists? [this]
    (path/-exists? pathz))

  (basename [this]
    (last (string/split (abs this) "/")))

  (size [this]
    (size-of-path this))

  (permissions [this]
    (permissions-of-path pathz))

  IDir
  (list [this]
    (vec (map fspath (path/-list-dir pathz))))

  (walk [this]
    (transduce (map #(if (path/-file? %)
                       (->File %)
                       (->Dir  %)))
               conj
               pathz))

  (walk-files [this]
    (filter #(instance? File %)
            (walk this)))

  (walk-dirs [this]
    (filter #(instance? Dir %)
            (walk this)))

  IObject
  (-hash [this]
    (hash (abs this)))

  (-eq [this other]
    (if (instance? Dir other)
      (= (abs this) (abs other))
      false))

  (-str [this]
    (str (abs this)))

  (-repr [this]
    (str "<Dir " (str this) ">")))

;; (deftype Fifo [pathz])

(defn file
  "Returns a file if the path is a file or does not exist. If a different filesystem object exists at the path an error will be thrown."
  [x]
  (let [x (path/-path x)]
    (cond
      (path/-file? x)         (->File x)
      (not (path/-exists? x)) (->File x)
      :else (throw (str "A non-file object exists at path: " x)))))

(defn dir
  "Returns a dir if the path is a dir or does not exist. If a different filesystem object exists at the path an error will be thrown."
  [x]
  (let [x (path/-path x)]
    (cond
      (path/-dir? x)          (->Dir x)
      (not (path/-exists? x)) (->Dir x)
      :else (throw (str "A non-dir object exists at path: " x)))))

(defn fspath
  "Returns either a File or Dir if they exist at the path"
  [x]
  (let [x (path/-path x)]
    (cond
       (path/-file? x) (->File x)
       (path/-dir? x)  (->Dir x)
       :else (throw (str "No file or directory at path: " x)))))


