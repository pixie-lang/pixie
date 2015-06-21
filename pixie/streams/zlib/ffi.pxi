(ns pixie.streams.zlib.ffi
  (:require [pixie.ffi-infer :as f]
            [pixie.ffi :as ffi]))

(f/with-config  {:library "z"
                :includes ["zlib.h"]}
  (f/defcstruct z_stream [:next_in 
                          :avail_in 
                          :total_in
                          :next_out 
                          :avail_out
                          :total_out

                          :msg
                          :state

                          :zalloc 
                          :zfree 
                          :opaque 

                          :data_type
                          :adler

                          :reserved])

  (f/defcfn zError)
  (f/defcfn zlibVersion)

  ;; Inflating (decompressing)
  (f/defcfn inflate)
  (f/defcfn inflateEnd)
  (f/defcfn inflateInit2_)

  ;; Defalting (compressing)
  (f/defcfn deflate)
  (f/defcfn deflateInit_)
  (f/defcfn deflateInit2_)
  (f/defcfn deflateEnd))

(def Z_OK 0)
(def Z_NO_FLUSH 0)
(def Z_PARTIAL_FLUSH 1)
(def Z_SYNC_FLUSH 2)
(def Z_FULL_FLUSH 3)
(def Z_FINISH 4)
(def Z_BLOCK 5)

(def Z_ERRNO -1)
(def Z_STREAM_ERROR -2)
(def Z_DATA_ERROR -3)

(def Z_NO_COMPRESSION 0)
(def Z_BEST_SPEED 1)
(def Z_BEST_COMPRESSION 9)
(def Z_DEFAULT_COMPRESSION -1)

(def Z_DEFLATED 8)

(def Z_DEFAULT_STRATEGY 0)
