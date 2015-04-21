(ns pixie.system
  (:require [pixie.ffi-infer :as i]))

(i/with-config {:library "c" :imports ["stdio.h"]}
  (i/defconst STDIN_FILENO)
  (i/defconst STDOUT_FILENO)
  (i/defconst STDERR_FILENO))

(def fdopen (ffi-fn libc "fdopen" [CInt CCharP] CVoidP))

(def stdin  STDIN_FILENO)
(def stderr STDOUT_FILENO)
(def stdout STDERR_FILENO)
