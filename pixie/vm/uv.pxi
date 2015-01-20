(ns pixie.uv
  (require pixie.ffi-infer :as f))

(f/with-config {:library "uv"
                :includes ["uv.h"]}
  (f/defconst UV_RUN_DEFAULT)
  (f/defconst UV_RUN_ONCE)
  (f/defconst UV_RUN_NOWAIT)

  (f/defcstruct uv_loop_t [])
  )