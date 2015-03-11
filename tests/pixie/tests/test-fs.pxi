(ns pixie.tests.test-fs
  (require pixie.test :as t)
  (require pixie.fs :as fs))

(t/deftest test-file-comparisons
  "All these paths are the same"
  (let [dir-a "tests/pixie/tests/fs/parent"
        dir-b "tests/pixie/tests/fs/../fs/parent"
        dir-c "tests/pixie/tests/fs/../fs/parent/../../fs/parent"
        file-a (str dir-a "/foo.txt")
        file-b (str dir-b "/foo.txt")
        file-c (str dir-c "/foo.txt")]
    (t/assert= (= (fs/dir dir-a)
                  (fs/dir dir-b)
                  (fs/dir dir-c))
               true)

    (t/assert= (= (fs/file file-a)
                  (fs/file file-b)
                  (fs/file file-c))
               true)

    (t/assert= (count (distinct [(fs/dir dir-a)
                                 (fs/dir dir-b)
                                 (fs/dir dir-c)]))
               1)
    (t/assert= (count (distinct [(fs/file file-a)
                                 (fs/file file-b)
                                 (fs/file file-c)]))
               1)))

(t/deftest test-walking
  (let [dir-a "tests/pixie/tests/fs"]
    (t/assert= (set (fs/walk (fs/dir dir-a)))
               #{(fs/dir  (str dir-a "/parent"))
                 (fs/file (str dir-a "/parent/foo.txt"))
                 (fs/file (str dir-a "/parent/bar.txt"))
                 (fs/dir  (str dir-a "/parent/child"))
                 (fs/file (str dir-a "/parent/child/foo.txt"))
                 (fs/file (str dir-a "/parent/child/bar.txt"))})

    (t/assert= (set (fs/walk-files (fs/dir dir-a)))
               #{(fs/file (str dir-a "/parent/foo.txt"))
                 (fs/file (str dir-a "/parent/bar.txt"))
                 (fs/file (str dir-a "/parent/child/foo.txt"))
                 (fs/file (str dir-a "/parent/child/bar.txt"))})

    (t/assert= (set (fs/walk-dirs (fs/dir dir-a)))
               #{(fs/dir  (str dir-a "/parent"))
                 (fs/dir  (str dir-a "/parent/child"))})))

(t/deftest test-list
  (let [dir-a "tests/pixie/tests/fs/parent"]
    (t/assert= (set (fs/list (fs/dir dir-a)))
               #{(fs/file (str dir-a "/foo.txt"))
                 (fs/file (str dir-a "/bar.txt"))
                 (fs/dir  (str dir-a "/child"))})))

(t/deftest test-rel?
  (let [dir-a  (fs/dir  "tests/pixie/tests/fs")
        dir-b  (fs/dir  "tests/pixie/tests/fs/parent")
        dir-c  (fs/dir  "tests/pixie/tests/fs/parent/child")
        file-a (fs/file "tests/pixie/tests/fs/parent/foo.txt")
        file-b (fs/file "tests/pixie/tests/fs/parent/bar.txt")
        file-c (fs/file "tests/pixie/tests/fs/parent/child/foo.txt")]
    ;; Test directory-directory comparisons
    (t/assert= (fs/rel dir-a dir-a) ".")
    (t/assert= (fs/rel dir-a dir-b) "..")
    (t/assert= (fs/rel dir-a dir-c) "../..")
    (t/assert= (fs/rel dir-c dir-b) "child")
    (t/assert= (fs/rel dir-c dir-a) "parent/child")
    ;; Test file-file comparisons
    (t/assert= (fs/rel file-a file-a) ".")
    (t/assert= (fs/rel file-a file-b) "../foo.txt")
    (t/assert= (fs/rel file-a file-c) "../../foo.txt")
    (t/assert= (fs/rel file-c file-a) "../child/foo.txt")
    (t/assert= (fs/rel file-c file-b) "../child/foo.txt")
    ;; Test file-directory comparisons
    (t/assert= (fs/rel file-a dir-a) "parent/foo.txt")
    (t/assert= (fs/rel file-a dir-b) "foo.txt")
    (t/assert= (fs/rel file-a dir-c) "../foo.txt")))

(t/deftest test-basename?
  (let [dir-a  (fs/dir  "tests/pixie/tests/fs")
        dir-b  (fs/dir  "tests/pixie/tests/fs/parent")
        dir-c  (fs/dir  "tests/pixie/tests/fs/parent/child")
        file-a (fs/file "tests/pixie/tests/fs/parent/foo.txt")
        file-b (fs/file "tests/pixie/tests/fs/parent/bar.txt")
        file-c (fs/file "tests/pixie/tests/fs/parent/child/foo.txt")]
    ;; Test directory-directory comparisons
    (t/assert= (fs/basename dir-a) "fs")
    (t/assert= (fs/basename dir-b) "parent")
    (t/assert= (fs/basename dir-c) "child")
    (t/assert= (fs/basename file-a) "foo.txt")
    (t/assert= (fs/basename file-b) "bar.txt")
    (t/assert= (fs/basename file-c) "foo.txt")))

(t/deftest test-exists?
  (let [real-dir  (fs/dir "tests/pixie/tests/fs/parent")
        fake-dir  (fs/dir "tests/pixie/tests/fs/parent/fake-dir")
        fake-file (fs/dir "tests/pixie/tests/fs/parent/fake-file")]
    (t/assert= (fs/exists? real-dir)  true)
    (t/assert= (fs/exists? fake-dir)  false)
    (t/assert= (fs/exists? fake-file) false)))
