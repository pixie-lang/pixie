(ns pixie.pxic-writer
  (:require [pixie.streams :refer [write-byte]]
            [pixie.streams.utf8 :refer [utf8-output-stream-rf]]
            [pixie.io :refer [spit]]))

(def MAX_INT32 (bit-shift-left 1 31))

(defmacro defenum [nms])




(defmacro defbytecodes [bytecodes]
  `(do ~@(map
        (fn [idx k]
          `(def ~(symbol (name k)) ~idx))
        (range)
        bytecodes)))

(defbytecodes
  [:CACHED-OBJECT
   :INT
   :FLOAT
   :INT-STRING
   :STRING
   :TRUE
   :FALSE
   :NIL
   :VAR
   :KEYWORD
   :SYMBOL
   :NEW-CACHED-OBJECT
   :DO
   :INVOKE
   :VAR
   :CONST
   :FN
   :LOOKUP
   :IF
   :LET
   :META
   :LINE-META
   :VAR-CONST])

(def *cache* nil)
(set-dynamic! (var *cache*))


(defprotocol IWriterCache
  (write-cached-obj [this val wfn]))

(deftype NullWriterCache []
  IWriterCache
  (write-cached-obj [this val wfn]
    (apply wfn val)))

(deftype WriterCache [os cache]
  IWriterCache
  (write-cached-obj [this val wfn]
    (if-let [idx (cache val)]
      (do (write-tag os CACHED-OBJECT)
          (write-int-raw os idx))
      (let [idx (count cache)]
        (set-field! this :cache (assoc cache val idx))
        (write-tag os NEW-CACHED-OBJECT)
        (apply wfn val)))))


(defn writer-cache [os]
  (->WriterCache os {}))

(defn write-raw-string [os str]
  (write-int-raw os (count str))
  (spit os str false))

(defn write-int-raw [os i]
  (if (<= 0 i MAX_INT32)
    (do (write-byte os (bit-and i 0xFF))
        (write-byte os (bit-and (bit-shift-right i 8) 0xFF))
        (write-byte os (bit-and (bit-shift-right i 16) 0xFF))
        (write-byte os (bit-and (bit-shift-right i 24) 0xFF)))
    (throw [:pixie.pxic-writer/OversizedInt
            "Collection sizes are limited to 32 bits in pxic files"])))

(defn write-int [os i]
  (if (<= 0 i MAX_INT32)
    (do (write-byte os INT)
        (write-int-raw os i))
    (do (write-byte os INT-STRING)
        (write-raw-string os (str i)))))

(defn write-meta [os ast]
  (let [m (meta (:form ast))]
    (if m
      (write-object os {:op :meta
                        :line {:op :line-meta
                               :line (str (:line m))
                               :file (:file m)
                               :line-number (:line-number m)}
                        :column-number (:column-number m)})
      (write-object os nil))))

(defn write-tag [os tag]
  (write-byte os tag))

(defprotocol IPxicObject
  (-write-object [this os]))

(defmulti write-ast (fn [os ast]
                      (:op ast)))

(defmethod write-ast :do
  [os {:keys [statements ret] :as ast}]
  (write-tag os DO)
  (write-int-raw os (inc (count statements)))
  (doseq [statement statements]
    (write-object os statement))
  (write-object os ret)
  (write-meta os ast))

(defmethod write-ast :invoke
  [os {:keys [fn args] :as ast}]
  (write-tag os INVOKE)
  (write-int-raw os (inc (count args)))
  (write-object os fn)
  (doseq [arg args]
    (write-object os arg))
  (write-meta os ast))

(defmethod write-ast :var
  [os {:keys [ns name]}]
  (write-cached-obj *cache*
                    [:deref ns name]
                    (fn [_ ns name]
                      (write-tag os VAR)
                      (write-raw-string os (str ns))
                      (write-raw-string os (str name)))))

(defmethod write-ast :var-const
  [os {:keys [ns name]}]
  (write-cached-obj *cache*
                    [:const ns name]
                    (fn [_ ns name]
                      (write-tag os VAR-CONST)
                      (write-raw-string os (str ns))
                      (write-raw-string os (str name)))))

(defmethod write-ast :const
  [os {:keys [form]}]
  (write-tag os CONST)
  (write-object os form))

(defmethod write-ast :fn-body
  [os {:keys [name args closed-overs body] :as ast}]
  (write-tag os FN)
  (write-raw-string os (str name))
  (write-int-raw os (count args))
  (doseq [arg args]
    (write-object os (keyword (str arg))))
  (write-int-raw os (count closed-overs))
  (doseq [co closed-overs]
    (write-object os (keyword (str co))))
  (write-object os body)
  (write-meta os ast))

(defmethod write-ast :binding
  [os {:keys [name] :as ast}]
  (write-tag os LOOKUP)
  (write-object os (keyword (pixie.stdlib/name name)))
  (write-meta os ast))

(defmethod write-ast :if
  [os {:keys [test then else] :as ast}]
  (write-tag os IF)
  (write-object os test)
  (write-object os then)
  (write-object os else)
  (write-meta os ast))

(defmethod write-ast :let
  [os {:keys [bindings body] :as ast}]
  (write-tag os LET)
  (write-int-raw os (count bindings))
  (doseq [{:keys [name value]} bindings]
    (write-object os name)
    (write-object os value))
  (write-object os body)
  (write-meta os ast))

(defmethod write-ast :meta
  [os {:keys [line column-number]}]
  (write-tag os META)
  (write-object os line)
  (write-int-raw os column-number))

(defmethod write-ast :line-meta
  [os ast]
  (write-cached-obj *cache*
                    [:line-meta ast]
                    (fn [_ {:keys [line file line-number]}]
                      (write-tag os LINE-META)
                      (write-raw-string os file)
                      (write-raw-string os line)
                      (write-int-raw os line-number))))

(extend-protocol IPxicObject
  IMap
  (-write-object [this os]
    (write-ast os this))

  String
  (-write-object [this os]
    (write-cached-obj *cache*
                      [:string this]
                      (fn [_ this]
                        (write-tag os STRING)
                        (write-raw-string os this))))

  Keyword
  (-write-object [this os]
    (write-cached-obj *cache*
                      [:keyword this]
                      (fn [_ this]
                        (write-tag os KEYWORD)
                        (if (namespace this)
                          (write-raw-string os (str (namespace this) "/" (name this)))
                          (write-raw-string os (str this))))))

  Symbol
  (-write-object [this os]
    (write-cached-obj *cache*
                      [:symbol this]
                      (fn [_ this]
                        (write-tag os SYMBOL)
                        (if (namespace this)
                          (write-raw-string os (str (namespace this) "/" (name this)))
                          (write-raw-string os (str this))))))

  Integer
  (-write-object [this os]
    (write-int os this))

  Bool
  (-write-object [this os]
    (if this
      (write-tag os TRUE)
      (write-tag os FALSE)))

  Nil
  (-write-object [this os]
    (write-tag os NIL)))


(defn write-object [os ast]
  (-write-object ast os))
