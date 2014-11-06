#include "uv.h"
#include "ffi.h"

typedef struct cif_desc_t {
  ffi_cif cif;
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
  ffi_cif *cif;
  void *fn_addr;
  void *exb;
} work_baton_t;

void ffi_call_impl_any_c(cif_desc_t *cif, void* func_addr, void* exchange_buffer)
{
    void **buffer_array = (void **)exchange_buffer;
    for (int i = 0; i < cif->nargs; i += 1)
    {
        void **data = exchange_buffer + cif->exchange_args[i];
        buffer_array[i] = data;
    }
    void **result_data = exchange_buffer + cif->exchange_result_libffi;
    ffi_call(&cif->cif, func_addr, (void*)result_data, buffer_array);
}



void do_work(work_baton_t *req)
{
  ffi_call_impl_any_c(req->cif, req->fn_addr, req->exb);
}

void* uv_ffi_make_baton()
{
  return malloc(sizeof(work_baton_t));
}

int uv_ffi_run(work_baton_t *w, uv_loop_t *loop, ffi_cif *cif, void* fn_addr, void *exb, uv_after_work_cb *after_work)
{
  w->cif = cif;
  w->fn_addr = fn_addr;
  w->exb = exb;
  uv_queue_work(loop, w, do_work, after_work);
}