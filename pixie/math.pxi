(ns pixie.math
  (:require [pixie.ffi-infer :as i]))

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
  (i/defcfn tan)
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
  (i/defcfn fmod)

  (i/defconst M_E)             ; base of natural logarithm, e
  (i/defconst M_LOG2E)         ; log2(e)
  (i/defconst M_LOG10E)        ; log10(e)
  (i/defconst M_LN2)           ; ln(2)
  (i/defconst M_LN10)          ; ln(10)
  (i/defconst M_PI)            ; pi
  (i/defconst M_PI_2)          ; pi / 2
  (i/defconst M_PI_4)          ; pi / 4
  (i/defconst M_1_PI)          ; 1 / pi
  (i/defconst M_2_PI)          ; 2 / pi
  (i/defconst M_2_SQRTPI)      ; 2 / sqrt(pi)
  (i/defconst M_SQRT2)         ; sqrt(2)
  (i/defconst M_SQRT1_2))      ; sqrt(1/2)

