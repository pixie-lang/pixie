(ns pixie.tests.utils)

;; Here we create a new type which hashes poorly, in fact it's so bad we have a
;; hash space of only 1.
;; All members of WorstHasher return (hash "worst hasher")
;; when hash is called on them.
;;
;; This makes debugging, testing and benchmarking anything based off
;; PersistentHashMap trivial.

;; X can be any thing you like.
(defrecord WorstHasher [x])
(extend -hash WorstHasher (fn [self] (hash "worst hasher")))
