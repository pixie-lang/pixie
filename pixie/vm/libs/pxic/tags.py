
tag_name = ["INT",
            "BIGINT",
            "FLOAT",
            "INT_STRING",
            "BIGINT_STRING",
            "STRING",
            "CODE",
            "TRUE",
            "FALSE",
            "NIL",
            "VAR",
            "MAP",
            "VECTOR",
            "SEQ",
            "KEYWORD",
            "SYMBOL",
            "CACHED_OBJ",
            "NEW_CACHED_OBJ",
            "LINE_PROMISE",
            "NAMESPACE",
            "TAGGED",
            "CODE_INFO",
            "EOF"]

tags = {}


SMALL_INT_START = 128
SMALL_INT_END = 255
SMALL_INT_MAX = SMALL_INT_END - SMALL_INT_END

MAX_STRING_SIZE = 1 << 30

for idx, nm in enumerate(tag_name):
    globals()[nm] = idx
    tags[nm] = idx

