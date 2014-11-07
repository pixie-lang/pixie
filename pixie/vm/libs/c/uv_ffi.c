#include "uv_ffi.h"
#include "stdlib.h"
#include "stdio.h"

#define EXPORT __attribute__((visibility("default")))

void do_work(work_baton_t *req)
{
  ffi_call(req->cif, req->fn_addr, req->result, req->exb);
}

EXPORT int uv_ffi_run(work_baton_t *w, uv_loop_t *loop, ffi_cif *cif, void* fn_addr, void *exb, void *result, uv_after_work_cb after_work)
{
  w->fn_addr = fn_addr;
  w->cif = cif;
  w->exb = exb;
  w->result = result;
  return uv_queue_work(loop, (uv_work_t *)w, (uv_work_cb)do_work, after_work);
}