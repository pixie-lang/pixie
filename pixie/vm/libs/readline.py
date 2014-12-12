import py

from rpython.rlib.runicode import str_decode_utf_8
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
    if result == lltype.nullptr(rffi.CCHARP.TO):
        return u""
    else:
        s = rffi.charp2str(result)
        try:
            return unicode(s) + u"\n"
        except UnicodeDecodeError:
            res, _ = str_decode_utf_8(s, len(s), 'strict')
            return res + u"\n"
