(ns pixie.math
  (:require [pixie.ffi-infer :as i]))

(i/with-config {:library "m"
                :cxx-flags ["-lm"]
                :includes ["math.h"]}
  (i/defconst M_E)
  (i/defconst M_LOG2E)
  (i/defconst M_LOG10E)
  (i/defconst M_LN2)
  (i/defconst M_LN10)
  (i/defconst M_PI)
  (i/defconst M_PI_2)
  (i/defconst M_PI_4)
  (i/defconst M_1_PI)
  (i/defconst M_2_PI)
  (i/defconst M_2_SQRTPI)
  (i/defconst M_SQRT2)
  (i/defconst M_SQRT1_2)

  (i/defcfn nan)
  (i/defcfn ceil)
  (i/defcfn floor)
  (i/defcfn nearbyint)
  (i/defcfn rint)
  (i/defcfn lround)
  (i/defcfn llrint)
  (i/defcfn llround)
  (i/defcfn trunc)

  (i/defcfn fmod)
  (i/defcfn remainder)
  (i/defcfn remquo)

  (i/defcfn fdim)
  (i/defcfn fmax)
  (i/defcfn fmin)

  (i/defcfn fma)

  (i/defcfn fabs)
  (i/defcfn sqrt)
  (i/defcfn cbrt)
  (i/defcfn hypot)

  (i/defcfn exp)
  (i/defcfn exp2)
  (i/defcfn exp10)
  (i/defcfn expm1)

  (i/defcfn log)
  (i/defcfn log2)
  (i/defcfn log10)
  (i/defcfn log1p)

  (i/defcfn logb)
  (i/defcfn ilogb)

  (i/defcfn modf)
  (i/defcfn frexp)

  (i/defcfn ldexp)
  (i/defcfn scalbn)
  (i/defcfn scalbln)

  (i/defcfn pow)

  (i/defcfn cos)
  (i/defcfn sin)
  (i/defcfn tan)

  (i/defcfn cosh)
  (i/defcfn sinh)
  (i/defcfn tanh)

  (i/defcfn acos)
  (i/defcfn asin)
  (i/defcfn atan)
  (i/defcfn atan2)

  (i/defcfn acosh)
  (i/defcfn asinh)
  (i/defcfn atanh)

  (i/defcfn tgamma)
  (i/defcfn lgamma)

  (i/defcfn j0)
  (i/defcfn j1)
  (i/defcfn jn)
  (i/defcfn y0)
  (i/defcfn y1)
  (i/defcfn yn)

  (i/defcfn erf)
  (i/defcfn erfc))
