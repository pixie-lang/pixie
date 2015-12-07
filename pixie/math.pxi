(ns pixie.math
  (:require [pixie.ffi-infer :as i]))

(i/with-config {:library "m"
                :cxx-flags ["-lm"]
                :includes ["math.h"]}
  (i/defcfn sin)
  (i/defcfn cos)
  (i/defcfn tan)

  (i/defcfn asin)
  (i/defcfn acos)
  (i/defcfn atan)
  (i/defcfn atan2) ; Arc tangent function of two variables.

  (i/defcfn sinh)
  (i/defcfn cosh)
  (i/defcfn tanh)

  (i/defcfn asinh)
  (i/defcfn acosh)
  (i/defcfn atanh)

  (i/defcfn exp)
  (i/defcfn ldexp)

  (i/defcfn log)
  (i/defcfn log2)
  (i/defcfn log10)
  (i/defcfn log1p)
  (i/defcfn logb)
  (i/defcfn ilogb)

  ;; (i/defcfn modf) ;; Needs ffi support
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

