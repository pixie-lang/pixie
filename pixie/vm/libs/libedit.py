import py

from pixie.vm.util import unicode_from_utf8

from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.translator import cdir
from rpython.translator.tool.cbuild import ExternalCompilationInfo

# ____________________________________________________________

srcdir = py.path.local(cdir) / 'src'
compilation_info = ExternalCompilationInfo(
        includes=['editline/readline.h'],
        libraries=["edit"])

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)

__readline = llexternal('readline', [rffi.CCHARP], rffi.CCHARP)

def _readline(prompt):
    result = __readline(rffi.str2charp(prompt))
    if result == lltype.nullptr(rffi.CCHARP.TO):
        return u""
    else:
        return unicode_from_utf8(rffi.charp2str(result)) + u"\n"
