#include "uv.h"
#include "ffi.h"

#define EXPORT __attribute__((visibility("default")))

typedef struct cif_desc_t {
  ffi_cif *cif;
  int abi;
  int nargs;
  ffi_type* rtype;
  ffi_type** atypes;
  int exchange_size;
  int exchange_result;
  int exchange_result_libffi;
  int exchange_args[0];
} cif_desc_t;

void (*ffi_cb)(ffi_cif *cif);

typedef struct work_baton_t
{
  uv_work_t work;
  cif_desc_t *cif;
  void *fn_addr;
  void *exb;
  void *result;
} work_baton_t;


void do_work(work_baton_t *req)
{
  puts("doing work\n");
  ffi_call(req->cif, req->fn_addr, req->result, req->exb);
  puts("work done\n");
}

EXPORT void* uv_ffi_make_baton()
{
  return malloc(sizeof(work_baton_t));
}

EXPORT int uv_ffi_run(work_baton_t *w, uv_loop_t *loop, ffi_cif *cif, void* fn_addr, void *exb, void *result, uv_after_work_cb *after_work)
{
  w->cif = cif;
  w->fn_addr = fn_addr;
  w->exb = exb;
  w->result = result;
  puts("queuing work\n");
  uv_queue_work(loop, w, do_work, after_work);
}