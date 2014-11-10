#include "uv.h"
#include "ffi.h"

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
  ffi_cif *cif;
  void *fn_addr;
  void *exb;
  void *result;
} work_baton_t;