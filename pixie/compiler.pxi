(ns pixie.compiler
  (:require [pixie.io :as io]
            [pixie.string :as string]
            [pixie.time :refer [time]]
            [pixie.pxic-writer :as pxic-writer]
            [pixie.ast :refer :all]))


(def macro-overrides
  {
   (resolve 'defprotocol)
   (fn
     [nm & sigs]
     `(do (def ~nm (~'pixie.stdlib/protocol ~(str nm)))
          ~@(map (fn [[x]]
                   `(def ~x (~'pixie.stdlib/polymorphic-fn ~(str x) ~nm)))
                 sigs)))

   (resolve 'deftype)
   (fn deftype
     [nm fields & body]
     (let [ctor-name (symbol (str "->" (name nm)))
           fields (transduce (map (comp keyword name)) conj fields)
           field-syms (transduce (map (comp symbol name)) conj fields)
           mk-body (fn [body]
                     (let [fn-name (first body)
                           _ (assert (symbol? fn-name) "protocol override must have a name")
                           args (second body)
                           _ (assert (or (vector? args)
                                         (seq? args)) "protocol override must have arguments")
                           self-arg (first args)
                           _ (assert (symbol? self-arg) "protocol override must have at least one `self' argument")

                           rest (next (next body))
                           body (reduce
                                 (fn [body f]
                                   `[(local-macro [~(symbol (name f))
                                                   (get-field ~self-arg ~(keyword (name f)))]
                                                  ~@body)])
                                 rest
                                 fields)]
                       `(fn ~(symbol (str fn-name "_" nm)) ~args ~@body)))
           bodies (reduce
                   (fn [res body]
                     (cond
                       (symbol? body) (cond
                                        (= body 'Object) [body (second res) (third res)]
                                        :else [body
                                               (second res)
                                               (conj (third res) body)])
                       (seq? body) (let [proto (first res) tbs (second res) pbs (third res)]
                                     (if (protocol? proto)
                                       [proto tbs (conj pbs body)]
                                       [proto (conj tbs body) pbs]))))
                   [nil [] []]
                   body)
           proto-bodies (second bodies)
           all-fields fields
           type-nm (str (:ns *env*) "." (name nm))
           type-decl `(def ~nm (create-type ~(keyword type-nm)
                                            ~all-fields))
           inst (gensym)
           ctor `(defn ~ctor-name ~field-syms
                   (new ~nm
                        ~@field-syms))
           proto-bodies (transduce
                         (map (fn [body]
                                (cond
                                  (symbol? body) `(satisfy ~body ~nm)
                                  (seq? body) `(extend ~(first body)
                                                 ~(symbol (str (:ns *env*) "/" nm))
                                                 ~(mk-body body))
                                  :else (assert false "Unknown body element in deftype, expected symbol or seq"))))
                         conj
                         proto-bodies)]
       `(do ~type-decl
            ~ctor
            ~@proto-bodies)))})


(def *env* nil)
(set-dynamic! (var *env*))

(defmulti analyze-form (fn [x]
                         (cond
                           (identical? x true) :bool
                           (identical? x false) :bool
                           (nil? x) nil
                           (seq? x) :seq
                           (vector? x) :vector
                           (symbol? x) :symbol
                           (number? x) :number
                           (string? x) :string
                           (char? x) :char
                           (keyword? x) :keyword)))

(defmulti analyze-seq (fn [x]
                         (let [f (first x)]
                           (if (symbol? f)
                             f
                             :invoke))))


;; Special Forms

(defmethod analyze-seq 'do
  [x]
  (let [statement-asts (binding [*env* (assoc *env* :tail? false)]
                         (mapv analyze-form (butlast (next x))))]
    (->Do statement-asts
          (analyze-form (last x))
          x
          *env*)))

(defmethod analyze-seq 'comment
  [x]
  (->Const x *env*))

(defmethod analyze-seq 'if
  [[_ test then else :as form]]
  (->If (binding [*env* (assoc *env* :tail? false)]
           (analyze-form test))
        (analyze-form then)
        (analyze-form else)
        form
        *env*))


(defmethod analyze-seq 'fn*
  [[_ & body :as form]]
  (let [[name body] (if (symbol? (first body))
                      [(first body)
                       (next body)]
                      [(gensym "fn_")
                       body])
        arities (if (vector? (first body))
                  [body]
                  body)
        analyzed-bodies (reduce
                         (partial analyze-fn-body name)
                         {}
                         arities)]
    (->Fn name
          (vals analyzed-bodies)
          form
          *env*)))

(defn add-local [env type bind-name]
  (assoc-in env [:locals bind-name] (->Binding type bind-name bind-name *env*)))

(defn analyze-fn-body [fn-name acc [args & body :as form]]
  (let [[args variadic?] (let [not& (vec (filter (complement (partial = '&)) args))]
                           [not& (= '& (last (butlast args)))])
        arity (count args)
        arity-idx (if variadic? -1 arity)
        new-env (add-local *env* :fn-self fn-name)
        new-env (reduce
                 (fn [acc arg-name]
                   (add-local acc :arg arg-name))
                 new-env
                 args)]
    (assert (not (acc arity-idx)) (str "Duplicate arity for " (cons args body)))
    (assoc acc arity-idx (->FnBody fn-name
                                   arity
                                   args
                                   nil
                                   variadic?
                                   (binding [*env* (assoc new-env :tail? true)]
                                     (analyze-form (cons 'do body)))
                                   form
                                   *env*))))

(defmethod analyze-seq 'let*
  [[_ bindings & body :as form]]
  (assert (even? (count bindings)) "Let requires an even number of bindings")
  (let [parted (partition 2 bindings)
        [new-env bindings] (reduce
                            (fn [[new-env bindings] [name binding-form]]
                              (let [binding-ast (binding [*env* new-env]
                                                  (->LetBinding name
                                                                (binding [*env* (assoc *env* :tail? false)]
                                                                  (analyze-form binding-form))
                                                                binding-form
                                                                *env*))]
                                [(assoc-in new-env [:locals name] binding-ast)
                                 (conj bindings binding-ast)]))
                            [*env* []]
                            parted)]
    (->Let bindings
           (binding [*env* new-env]
             (analyze-form `(do ~@body)))
           form
           *env*)))

(defmethod analyze-seq 'loop*
  [[_ bindings & body]]
  (let [parted (partition 2 bindings)]
    (analyze-form `((fn ~'__loop__fn__ ~(mapv first parted)
                      ~@body)
                    ~@(mapv second parted)))))

(defmethod analyze-seq 'recur
  [[_ & args]]
  (assert (:tail? *env*) "Can only recur at tail position")
  (analyze-form `(~'__loop__fn__ ~@args)))

(defmethod analyze-seq 'def
  [[_ nm val :as form]]
  (swap! (:vars *env*) update-in [(:ns *env*) nm] (fn [x]
                                          (or x :def)))
  (->Def
   nm
   (analyze-form val)
   form
   *env*))

(defmethod analyze-seq 'quote
  [[_ val]]
  (->Const val *env*))

(defmethod analyze-seq 'in-ns
  [[_ nsp]]
  (set! (var *env*) (assoc *env* :ns (symbol (name nsp))))
  (in-ns nsp)
  (in-ns :pixie.compiler)
  (analyze-form nil))

(defmethod analyze-seq 'local-macro
  [[_ [nm replace] & body :as form]]
  (binding [*env* (assoc-in *env* [:locals nm] {:op :local-macro
                                                :name nm
                                                :replace-with replace
                                                :form form})]
    (analyze-form (cons 'do body))))

(defmethod analyze-form nil
  [_]
  (->Const nil *env*))

(defmethod analyze-form :bool
  [form]
  (->Const form *env*))

(defn keep-meta [new old]
  (if-let [md (meta old)]
    (if (satisfies? IMeta new)
      (with-meta new md)
      new)
    new))

(defmethod analyze-seq :default
  [[sym & args :as form]]
  (let [resolved (try (and (symbol? sym)
                           (resolve-in (the-ns (:ns *env*)) sym))
                      (catch :pixie.stdlib/AssertionException ex
                        nil))]
    (cond
      (and (symbol? sym)
           (string/starts-with? (name sym) ".-"))
      (let [sym-kw (keyword (string/substring (name sym) 2))
            result (analyze-form (keep-meta `(~'pixie.stdlib/-get-field ~@args ~sym-kw)
                                            form))]
        result)
      
      (contains? macro-overrides resolved)
      (analyze-form (keep-meta (apply (macro-overrides resolved) args)
                               form))
      
      (and resolved
           (macro? @resolved))
      (analyze-form (keep-meta (apply @resolved args)
                               form))

      :else
      (->Invoke (binding [*env* (assoc *env* :tail? false)]
                  (analyze-form sym))
                (binding [*env* (assoc *env* :tail? false)]
                  (mapv analyze-form args))
                (:tail? *env*)
                form
                *env*))))


(defmethod analyze-form :number
  [x]
  (->Const x *env*))

(defmethod analyze-form :keyword
  [x]
  (->Const x *env*))

(defmethod analyze-form :string
  [x]
  (->Const x *env*))

(defmethod analyze-form :char
  [x]
  (->Const x *env*))

(defmethod analyze-form :seq
  [x]
  (analyze-seq x))

(defmethod analyze-form :symbol
  [x]
  (if-let [local (get-in *env* [:locals x])]
    (if (= (:op local) :local-macro)
      (analyze-form (:replace-with local))
      (assoc local :form x))
    (maybe-var x)))

(defmethod analyze-form :vector
  [x]
  (->Vector (mapv analyze-form x)
            x
            *env*))

(defn maybe-var [x]
  (let [namesp (the-ns (:ns *env*))
        resolved (try
                   (resolve-in namesp x)
                   (catch :pixie.stdlib/AssertionException ex
                     nil))
        result (cond
                 (namespace x)
                 (->Var (symbol (namespace x))
                        (symbol (name x))
                        x
                        *env*)
                 
                 (get-in @(:vars *env*) [(:ns *env*) x])
                 (->Var (:ns *env*)
                        x
                        x
                        *env*)

                 ;; Hack until we get proper refers
                 (get-in @(:vars *env*) ['pixie.stdlib x])
                 (->Var 'pixie.stdlib
                        x
                        x
                        *env*)
                 
                 resolved
                 (->Var (namespace resolved)
                        (name resolved)
                        x
                        *env*)
                 
                 :else
                 (->Var (name (:ns *env*))
                        (name x)
                        x
                        *env*))]
    result))


;; ENV Functions

(defn new-env
  "Creates a new (empty) environment"
  []
  (->Env
   'pixie.stdlib
   (atom {'pixie.stdlib {'array true
                         'size-t true
                         'bit-count32 true
                         'contains-table true
                         'switch-table true
                         '-add-to-string-builder true
                         '-parse-number true}})
   {}
   true))


(defn analyze
  ([form]
   (analyze form (new-env)))
  ([form env]
   (if *env*
     (analyze-form form)
     (binding [*env* env]
       (analyze-form form)))))




(defn walk [pre post selector node]
  (let [walk-fn (partial walk pre post selector)]
    (-> (reduce
         (fn [node k]
           (let [v (get node k)
                 result (if (or (vector? v)
                                (seq? v))
                          (mapv walk-fn v)
                          (walk-fn v))]
             (assoc node k result)))
         (pre node)
         (selector node))
        post)))

(defn post-walk [f ast]
  (walk identity f children-keys ast))


(defn child-seq [ast]
  (mapcat
   (fn [k]
     (let [child (get ast k)]
       (if (or (vector? child)
               (seq? child))
         child
         [child])))
   (children-keys ast)))

;; Collect Closed Overs


(defn collect-closed-overs [ast]
  (let [closed-overs (set (or (get-closed-overs ast)
                              (mapcat get-closed-overs (child-seq ast))))
        closed-overs (if (instance? FnBody ast)
                       (reduce disj closed-overs (:args ast))
                       closed-overs)]
    (assoc-closed-overs ast closed-overs)))


;; End Collect Closed Overs

(defn remove-env [ast]
  (walk #(dissoc % :env)
        identity
        :children
        ast))


(defn run-passes [ast]
  (walk identity
        identity #_simplify-ast
        children-keys
        ast))

(defn read-and-compile [form env]
  (let [ast (analyze form env)]
    ast))

#_(defn compile-file [from to]
  (println "Reading")
  (let [form (time (read-string (str "(do " (pixie.io/slurp from) ")")))
        _ (println "Compiling")
        ast (time (analyze form))
        _ (println "Passes")
        ast (time (run-passes ast))
        _ (println "To String")
        os (-> to
               io/open-write
               io/buffered-output-stream)]
    (binding [pxic-writer/*cache* (pxic-writer/writer-cache os)]
      (time (pxic-writer/write-object os ast)))
    #_(print str)
    (dispose! os)
    (println "done")))

(defn compile-file [from os]
  (let [forms (read-string (str "[" (io/slurp from) "]"))
        form-count (atom 0)
        total-count (atom 0)]
    (doseq [form forms]
          (swap! form-count inc)
          (swap! total-count inc)
          (when (= @form-count 10)
            (println from (int (* 100 (/ @total-count (count forms)))) "% in" (:ns *env*))
            (reset! form-count 0))
          
          (let [ast (read-and-compile form env)]
            (pxic-writer/write-object os ast)))))

(defn compile-files [files to]
  (let [os (-> to
               io/open-write
               io/buffered-output-stream)
                env (new-env)
]
    (binding [*env* env]
      (binding [pxic-writer/*cache* (pxic-writer/writer-cache os)]
        (doseq [file files]
          (compile-file file os))))
    (dispose! os)))

(time (compile-files ["pixie/bootstrap.pxi"
                      "pixie/streams.pxi"
                      "pixie/io-blocking.pxi"
                      "pixie/reader.pxi"]
                     "./bootstrap.pxic"))
