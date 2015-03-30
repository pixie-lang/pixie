(ns pixie.math
  (require pixie.ffi-infer :as i))

(i/with-config {:library "m"
                :cxx-flags ["-lm"]
                :includes ["math.h"]}
  (i/defcfn acos)
  (i/defcfn asin)
  (i/defcfn atan)
  (i/defcfn atan2)
  (i/defcfn cos)
  (i/defcfn cosh)
  (i/defcfn sin)
  (i/defcfn sinh)
  (i/defcfn tanh)
  (i/defcfn exp)
  (i/defcfn ldexp)
  (i/defcfn log)
  (i/defcfn log10)
  ;(i/defcfn modf) ;; Needs ffi support
  (i/defcfn pow)
  (i/defcfn sqrt)
  (i/defcfn ceil)
  (i/defcfn fabs)
  (i/defcfn floor)
  (i/defcfn fmod))
