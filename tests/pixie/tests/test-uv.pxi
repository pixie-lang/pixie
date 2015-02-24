(ns pixie.test-uv
  (require pixie.uv :as uv)
  (require pixie.test :as t))


(t/deftest timer-tests
  (let [cb (atom nil)
        result (atom false)
        loop (uv/uv_loop_t)
        timer (uv/uv_timer_t)]
    (reset! cb (ffi-prep-callback uv/uv_timer_cb
                                  (fn [handle]
                                    (reset! result true)
                                    (uv/uv_timer_stop timer)
                                    (-dispose! @cb))))
    (uv/uv_loop_init loop)
    (uv/uv_timer_init loop timer)
    (uv/uv_timer_start timer @cb 10 0)
    (uv/uv_run loop uv/UV_RUN_ONCE)
    (t/assert @result)))
