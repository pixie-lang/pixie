;; Mandelbrot demo from Timothy Baldridge's 2015 Strange Loop talk
;; https://www.youtube.com/watch?v=1AjhFZVfB9c


(ns mandelbrot
  (:require [pixie.ffi-infer :refer :all]
            [pixie.ffi :as ffi]
            [pixie.time :refer [time]]))

(with-config {:library "SDL2"
              :cxx-flags ["`sdl2-config --cflags`"]
              :includes ["SDL.h"]}

  (defcfn SDL_Init)

  (defconst SDL_INIT_VIDEO)
  (defconst SDL_WINDOWPOS_UNDEFINED)
  (defcfn SDL_CreateWindow)
  (defcfn SDL_CreateRenderer)
  (defcfn SDL_CreateTexture)
  (defconst SDL_PIXELFORMAT_RGBA8888)
  (defconst SDL_TEXTUREACCESS_STREAMING)
  (defcfn SDL_UpdateTexture)
  (defcfn SDL_RenderClear)
  (defcfn SDL_RenderCopy)

  (defconst SDL_WINDOW_SHOWN)
  (defcfn SDL_RenderPresent)
  (defcfn SDL_LockSurface))

(println "starting")
(def WIDTH 1024)
(def HEIGHT 512)

(assert (>= (SDL_Init SDL_INIT_VIDEO) 0))

(def WINDOW (SDL_CreateWindow "Pixie MandelBrot"
                              SDL_WINDOWPOS_UNDEFINED
                              SDL_WINDOWPOS_UNDEFINED
                              WIDTH
                              HEIGHT
                              SDL_WINDOW_SHOWN))

(assert WINDOW "Could not create window")

(def RENDERER (SDL_CreateRenderer WINDOW -1 0))

(def DRAW_SURFACE (SDL_CreateTexture RENDERER
                                     SDL_PIXELFORMAT_RGBA8888
                                     SDL_TEXTUREACCESS_STREAMING
                                     WIDTH
                                     HEIGHT))

(defn bit-or [& args]
  (reduce pixie.stdlib/bit-or 0 args))

(defn put-pixel [ptr x y r g b]
  (let [loc (* 4 (+(* y WIDTH) x))]
    (ffi/pack! ptr loc CUInt32 (bit-or (bit-shift-left r 24)
                                       (bit-shift-left g 16)
                                       (bit-shift-left b 8)
                                       255))))

(def BUFFER (buffer (* 4 WIDTH HEIGHT)))

(defn mandel-point [x y width height max_iterations]
  (let [x0 (float (- (* (/ x width) 3.5) 2.5))
        y0 (float (- (* (/ y height) 2) 1))]
    (loop [x 0.0
           y 0.0
           iteration 0]
      (let [xsq (* x x)
            ysq (* y y)]
        (if (and (< (+ xsq
                       ysq)
                    (* 2 2))
                 (< iteration max_iterations))
          (let [xtemp (+ (- xsq
                            ysq)
                         x0)
                y (+ (* 2 x y) y0)]
            (recur xtemp y (inc iteration)))
          (- 1 (/ iteration max_iterations)))))))

(dotimes [x 3]
  (time
   (let [max (* WIDTH HEIGHT)]
     (dotimes [y HEIGHT]
       (dotimes [x WIDTH]
         (let [result (mandel-point (float x) (float y) (float WIDTH) (float HEIGHT) 1000)
               color (int (* 16777216 result))]
           (put-pixel BUFFER x y
                      (bit-shift-right color 16)
                      (bit-and (bit-shift-right color 8) 0xff)
                      (bit-and color 0xff))))))))

(SDL_UpdateTexture DRAW_SURFACE nil BUFFER (* 4 WIDTH))
(SDL_RenderCopy RENDERER DRAW_SURFACE nil nil)
(SDL_RenderPresent RENDERER)

(pixie.stacklets/sleep 10000)
