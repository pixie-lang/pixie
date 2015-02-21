(ns pixie.uv
  (require pixie.ffi-infer :as f))

(f/with-config {:library "uv"
                :includes ["uv.h"]}
  (f/defconst UV_RUN_DEFAULT)
  (f/defconst UV_RUN_ONCE)
  (f/defconst UV_RUN_NOWAIT)

  (f/defcstruct uv_loop_t [])

  (f/defcfn uv_loop_init)
  (f/defcfn uv_loop_close)
  (f/defcfn uv_default_loop)

  (f/defcfn uv_run)
  (f/defcfn uv_loop_alive)
  (f/defcfn uv_stop)
  (f/defcfn uv_loop_size)
  (f/defcfn uv_backend_fd)
  (f/defcfn uv_backend_timeout)
  (f/defcfn uv_now)
  (f/defcfn uv_update_time)
  (f/defcfn uv_walk)

  (f/defccallback uv_read_cb)


  ;; Timer

  (f/defcstruct uv_timer_t [])
  (f/defccallback uv_timer_cb)
  (f/defcfn uv_timer_init)
  (f/defcfn uv_timer_start)
  (f/defcfn uv_timer_stop)
  (f/defcfn uv_timer_again)
  (f/defcfn uv_timer_set_repeat)
  (f/defcfn uv_timer_get_repeat))
