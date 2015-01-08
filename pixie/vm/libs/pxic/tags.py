
tag_name = ["INT",
            "FLOAT",
            "INT_STRING",
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
            "EOF"]

tags = {}


SMALL_INT_START = 128
SMALL_INT_END = 255
SMALL_INT_MAX = SMALL_INT_END - SMALL_INT_END

for idx, nm in enumerate(tag_name):
    globals()[nm] = idx
    tags[nm] = idx

