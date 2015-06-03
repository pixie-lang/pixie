(ns pixie.compiler
  (:require [pixie.io :as io]
            [pixie.string :as string]
            [pixie.time :refer [time]]
            [pixie.pxic-writer :as pxic-writer]))

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
                           (keyword? x) :keyword)))

(defmulti analyze-seq (fn [x]
                         (let [f (first x)]
                           (if (symbol? f)
                             f
                             :invoke))))


;; Special Forms

(defmethod analyze-seq 'do
  [x]
  {:op :do
   :children '[:statements :ret]
   :env *env*
   :form x
   :statements (binding [*env* (assoc *env* :tail? false)]
                 (mapv analyze-form (butlast (next x))))
   :ret (analyze-form (last x))})

(defmethod analyze-seq 'comment
  [x]
  {:op :const
   :type (keyword "nil")
   :form x
   :env *env*})

(defmethod analyze-seq 'if
  [[_ test then else :as form]]
  {:op :if
   :children '[:test :then :else]
   :env *env*
   :form form
   :test (binding [*env* (assoc *env* :tail? false)]
           (analyze-form test))
   :then (analyze-form then)
   :else (analyze-form else)})


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
    {:op :fn
     :env *env*
     :form form
     :name name
     :children '[:arities]
     :arities (vals analyzed-bodies)}
    ))

(defn analyze-fn-body [fn-name acc [args & body]]
  ; TODO: Add support for variadic fns
  (let [[args variadic?] (let [not& (vec (filter (complement (partial = '&)) args))]
                           [not& (= '& (last (butlast args)))])
        arity (count args)
        arity-idx (if variadic? -1 arity)
        new-env (update-in *env* [:locals] (fn [locals]
                                             (reduce
                                              (fn [locals [k v]]
                                                (assoc locals k (assoc v :closed-overs #{k})))
                                              {}
                                              locals)))
        new-env (assoc-in new-env [:locals fn-name] {:op :binding
                                                   :type :fn-self
                                                   :name fn-name
                                                   :form fn-name
                                                   :env *env*})
        new-env (reduce
                 (fn [acc idx]
                   (let [arg-name (nth args idx)]
                     (assoc-in acc [:locals arg-name] {:op :binding
                                                       :type :arg
                                                       :idx idx
                                                       :name arg-name
                                                       :form arg-name
                                                       :env *env*})))
                 new-env
                 (range (count args)))]
    (assert (not (acc arity-idx)) (str "Duplicate arity for " (cons args body)))
    (assoc acc arity-idx {:op :fn-body
                      :env *env*
                      :arity arity
                      :args args
                      :variadic? variadic?
                      :children '[:body]
                      :body (binding [*env* (assoc new-env :tail? true)]
                              (analyze-form (cons 'do body)))})))

(defn analyze-let-body
  [acc [name binding & rest :as form]]
  {:op :let
   :form form
   :children '[:binding :body]
   :env *env*
   :name name
   :body acc})

(defmethod analyze-seq 'let*
  [[_ bindings & body :as form]]
  (assert (even? (count bindings)) "Let requires an even number of bindings")
  (let [parted (partition 2 bindings)
        [new-env bindings] (reduce
                            (fn [[new-env bindings] [name binding-form]]
                              (let [binding-ast (binding [*env* new-env]
                                                  {:op :binding
                                                   :type :let
                                                   :children '[:value]
                                                   :form binding-form
                                                   :env *env*
                                                   :name name
                                                   :value (binding [*env* (assoc *env* :tail? false)]
                                                            (analyze-form binding-form))})]
                                [(assoc-in new-env [:locals name] binding-ast)
                                 (conj bindings binding-ast)]))
                            [*env* []]
                            parted)]
    {:op :let
     :form form
     :children '[:bindings :body]
     :bindings bindings
     :env *env*
     :body (binding [*env* new-env]
             (analyze-form `(do ~@body)))}))

(defmethod analyze-seq 'loop*
  [[_ bindings & body]]
  (let [parted (partition 2 bindings)]
    (analyze-form `((fn ~'__loop__fn__ ~(mapv first parted)
                      ~@body)
                    ~@(mapv second parted)))))

(defmethod analyze-seq 'recur
  [[_ & args]]
  (analyze-form `(~'__loop__fn__ ~@args)))

(defmethod analyze-seq 'def
  [[_ nm val :as form]]
  (swap! (:vars *env*) update-in [(:ns *env*) nm] (fn [x]
                                          (or x :def)))
  {:op :def
   :name nm
   :form form
   :env *env*
   :children '[:val]
   :val (analyze-form val)})

(defmethod analyze-seq 'quote
  [[_ val]]
  {:op :const
   :type (cond
           (symbol? val) :symbol
           (string? val) :string
           :else :unknown)
   :form val})

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
  {:op :const
   :type (keyword "nil")
   :env *env*
   :form nil})

(defmethod analyze-form :bool
  [form]
  {:op :const
   :type :bool
   :env *env*
   :form form})

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
      {:op :invoke
       :tail-call (:tail? *env*)
       :children '[:fn :args]
       :form form
       :env *env*
       :fn (binding [*env* (assoc *env* :tail? false)]
             (analyze-form sym))
       :args (binding [*env* (assoc *env* :tail? false)]
               (mapv analyze-form args))})))


(defmethod analyze-form :number
  [x]
  {:op :const
   :type :number
   :form x
   :env *env*})

(defmethod analyze-form :keyword
  [x]
  {:op :const
   :type :keyword
   :form x
   :env *env*})

(defmethod analyze-form :string
  [x]
  {:op :const
   :type :string
   :form x
   :env *env*})

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
  {:op :vector
   :children [:items]
   :items (mapv analyze-form x)
   :form x
   :env *env*})

(defn maybe-var [x]
  (let [namesp (the-ns (:ns *env*))
        resolved (try
                   (resolve-in namesp x)
                   (catch :pixie.stdlib/AssertionException ex
                     nil))
        result (cond
                 (namespace x)
                 {:op :var
                  :env *env*
                  :ns (symbol (namespace x))
                  :name (symbol (name x))
                  :form x}
                 
                 (get-in @(:vars *env*) [(:ns *env*) x])
                 {:op :var
                  :env *env*
                  :ns (:ns *env*)
                  :name x
                  :form x}

                 ;; Hack until we get proper refers
                 (get-in @(:vars *env*) ['pixie.stdlib x])
                 {:op :var
                  :env *env*
                  :ns 'pixie.stdlib
                  :name x
                  :form x}

                 resolved
                 {:op :var
                  :env *env*
                  :ns (namespace resolved)
                  :name (name resolved)
                  :form x}

                 :else
                 {:op :var
                  :env *env*
                  :ns (name (:ns *env*))
                  :name (name x)
                  :form x})]
    result))


;; ENV Functions

(defn new-env
  "Creates a new (empty) environment"
  []
  {:ns 'pixie.stdlib
   :vars (atom {'pixie.stdlib {'array true}})
   :tail? true})


(defn analyze
  ([form]
   (analyze form (new-env)))
  ([form env]
    (binding [*env* env]
      (analyze-form form))))





(defn walk [pre post selector node]
  (-> (reduce
       (fn [node k]
         (let [v (get node k)
               result (if (or (vector? v)
                              (seq? v))
                        (mapv (partial walk pre post selector) v)
                        (walk pre post selector v))]
           (assoc node k result)))
       (pre node)
       (selector node))
      post))

(defn post-walk [f ast]
  (walk identity f :children ast))

(defn clean-do [ast]
  (post-walk
   (fn [{:keys [op statements ret] :as ast}]
     (if (and (= op :do)
              (= (count statements) 0))
       ret
       ast))
   ast))

(defn child-seq [ast]
  (mapcat
   (fn [k]
     (let [child (get ast k)]
       (if (or (vector? child)
               (seq? child))
         child
         [child])))
   (:children ast)))

(def collect-closed-overs
  (fn [{:keys [op args env closed-overs] :as ast}]
    (let [{:keys [locals]} env
          closed-overs (set (or closed-overs
                                (mapcat :closed-overs (child-seq ast))))
          closed-overs (if (= op :fn-body)
                         (reduce disj closed-overs args)
                         closed-overs)]
      (assoc ast :closed-overs closed-overs)))
  ast)

(defn remove-env [ast]
  (walk #(dissoc % :env)
        identity
        :children
        ast))

(defn make-invoke-ast [fn args form env]
  {:op :invoke
   :children '[:fn :args]
   :form form
   :env env
   :fn fn
   :args args})

(defn make-var-ast [ns name env]
  {:op :var
   :ns ns
   :name name
   :env env
   :form (symbol (pixie.stdlib/name name))})

(defn make-var-const-ast [ns name env]
  {:op :var-const
   :ns ns
   :name name
   :env env
   :form (symbol (pixie.stdlib/name name))})

(defn make-invoke-var-ast [ns name args form env]
  (make-invoke-ast
   (make-var-ast ns name env)
   args
   form
   env))

(def convert-defs
  (fn [{:keys [op name env val form] :as ast}]
    (if (= op :def)
      (make-invoke-var-ast
       "pixie.stdlib"
       "set-var-root!"
       [(make-var-const-ast (:ns env) name env)
        val]
       form
       env)
      ast))
  identity
  :children
  ast)

(defn pass-for [op-for f]
  (fn [{:keys [op] :as ast}]
    (if (= op op-for)
      (f ast)
      ast)))

(def convert-fns
  (pass-for :fn
            (fn [{:keys [name arities form env]}]
              (if (= (count arities) 1)
                (convert-fn-body name (first arities))
                (make-invoke-var-ast
                 "pixie.stdlib"
                 "multi-arity-fn"
                 (vec (concat [{:op :const
                                :form (pixie.stdlib/name name)
                                :env env}]
                              (mapcat
                               (fn [{:keys [args variadic?] :as body}]
                                 [{:op :const
                                   :form (if variadic?
                                           -1
                                           (count args))
                                   :env env}
                                  (convert-fn-body name body)])
                               arities)))
                 form
                 env)))))


(defn convert-fn-body [name {:keys [variadic? args body form env] :as ast}]
  (if variadic?
    (make-invoke-var-ast
     "pixie.stdlib"
     "variadic-fn"
     [{:op :const
       :form (dec (count args))
       :env env}
      (convert-fn-body name (dissoc ast :variadic?))]
     form
     env)
    (assoc ast
           :op :fn-body
           :name name)))

(def convert-vectors
  (pass-for :vector
            (fn [{:keys [items form env]}]
              (make-invoke-var-ast
               "pixie.stdlib"
               "array"
               items
               form
               env))))

(defn run-passes [ast]
  (walk identity
        (comp
         convert-vectors
         convert-fns
         (comp convert-defs
               collect-closed-overs
               clean-do))
        :children
        ast))


(println "Reading")
(let [form (time (read-string (str "(do " (pixie.io/slurp "pixie/bootstrap.pxi") ")")))
      _ (println "Compiling")
      ast (time (analyze form))
      _ (println "Passes")
      ast (time (run-passes ast))
      _ (println "To String")
      os (-> "/tmp/bootstrap.pxic"
             io/open-write
             io/buffered-output-stream)]
  (binding [pxic-writer/*cache* (pxic-writer/writer-cache os)]
    (time (pxic-writer/write-object os ast)))
  #_(print str)
  (dispose! os)
  (println "done"))
