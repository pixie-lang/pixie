import py

from rpython.rtyper.lltypesystem import lltype, rffi
from rpython.rtyper.lltypesystem.lloperation import llop
from rpython.translator import cdir
from rpython.translator.tool.cbuild import ExternalCompilationInfo

# ____________________________________________________________

srcdir = py.path.local(cdir) / 'src'
compilation_info = ExternalCompilationInfo(
        includes=['readline/readline.h'],
        libraries=["readline"])

def llexternal(*args, **kwargs):
    return rffi.llexternal(*args, compilation_info=compilation_info, **kwargs)

__readline = llexternal('readline', [rffi.CCHARP], rffi.CCHARP)

def _readline(prompt):
    result = __readline(rffi.str2charp(prompt))
    if result is None:
        return u""
    else:
        return unicode(rffi.charp2str(result))
