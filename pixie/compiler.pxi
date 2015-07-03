(ns pixie.compiler
  (:require [pixie.string :as string]
            [pixie.ast :refer :all]))


(defmulti analyze-form (fn [_ x]
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
                           (keyword? x) :keyword
                           (map? x) :map
                           (set? x) :set
                           :else (type x))))

(defmulti analyze-seq (fn [_ x]
                         (let [f (first x)]
                           (if (symbol? f)
                             (let [sname (symbol (name f))]
                               (if (get @(get-field analyze-seq :methods) sname)
                                 sname
                                 f))
                             :invoke))))


;; Special Forms

(defmethod analyze-seq 'do
  [env x]
  (let [statement-asts (mapv (partial analyze-form (assoc env :tail? false))
                             (butlast (next x)))]
    (->Do statement-asts
          (analyze-form env (last x))
          x
          env)))

(defmethod analyze-seq 'comment
  [env x]
  (->Const x env))

(defmethod analyze-seq 'if
  [env [_ test then else :as form]]
  (->If (analyze-form (assoc env :tail? false) test)
        (analyze-form env then)
        (analyze-form env else)
        form
        env))

(defmethod analyze-seq 'this-ns-name
  [env [_]]
  (analyze-form env (name @(:ns env))))

(defmethod analyze-seq 'with-handler
  [env [_ [h handler] & body]]
  (analyze-form env
                `(let [~h ~handler]
                   (~'pixie.stdlib/-effect-finally
                    ~h
                    (~'pixie.stdlib/-with-handler
                     ~h
                     (fn []
                       (~'pixie.stdlib/-effect-val
                        ~h
                        (do ~@body))))))))

(defmethod analyze-seq 'defeffect
  [env [_ nm & sigs]]
  (analyze-form env
                `(do (def ~nm (~'pixie.stdlib/protocol ~(str nm)))
                     ~@(map (fn [[x]]
                              `(def ~x (~'pixie.stdlib/-effect-fn
                                        (~'pixie.stdlib/polymorphic-fn ~(str x) ~nm))))
                            sigs))))


(defmethod analyze-seq 'fn*
  [env [_ & body :as form]]
  (let [[name body] (if (symbol? (first body))
                      [(first body)
                       (next body)]
                      [(gensym "fn_")
                       body])
        arities (if (vector? (first body))
                  [body]
                  body)
        analyzed-bodies (reduce
                         (partial analyze-fn-body env name)
                         {}
                         arities)]
    (->Fn name
          (vals analyzed-bodies)
          form
          env)))

(defmethod analyze-seq 'try
  [env [_ & body :as form]]
  (let [analyzed (reduce
                  (fn [acc f]
                    (cond
                      (and (seq? f)
                           (= (first f) 'catch))
                      (let [[_ k ex-nm & body] f]
                        (assert (keyword? k) "First argument to catch must be a keyword")
                        (assoc-in acc [:catches k] `(fn [~ex-nm]
                                                      ~body)))
                      (and (seq? f)
                           (= (first f) 'finally))
                      (let [[_ & body] f]
                        (assert (nil? (:finally acc)) "Can only have one finally block in a try")
                        (assoc acc :finally `(fn []
                                               ~@body)))

                      :else (update-in acc [:bodies] conj f)))
                  {}
                  body)]
    (analyze-form env `(~'pixie.stdlib/-try
                        (fn []
                          ~@(or (:bodies analyzed)
                                []))
                        ~(or (:catches analyzed)
                             {})
                        ~(or (:finally analyzed)
                             `(fn [] nil))))))

(defn add-local [env type bind-name]
  (assoc-in env [:locals bind-name] (->Binding type bind-name bind-name env)))

(defn analyze-fn-body [env fn-name acc [args & body :as form]]
  (let [[args variadic?] (let [not& (vec (filter (complement (partial = '&)) args))]
                           [not& (= '& (last (butlast args)))])
        arity (count args)
        arity-idx (if variadic? -1 arity)
        new-env (add-local env :fn-self fn-name)
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
                                   (analyze-form
                                    (assoc new-env :tail? true)
                                    (cons 'do body))
                                   form
                                   env))))

(defmethod analyze-seq 'let*
  [env [_ bindings & body :as form]]
  (assert (even? (count bindings)) "Let requires an even number of bindings")
  (let [parted (partition 2 bindings)
        [new-env bindings] (reduce
                            (fn [[new-env bindings] [name binding-form]]
                              (let [binding-ast (->LetBinding name
                                                              (analyze-form
                                                               (assoc new-env :tail? false)
                                                               binding-form)
                                                              binding-form
                                                              env)]
                                [(assoc-in new-env [:locals name] binding-ast)
                                 (conj bindings binding-ast)]))
                            [env []]
                            parted)]
    (->Let bindings
           (analyze-form new-env `(do ~@body))
           form
           env)))

(defmethod analyze-seq 'loop*
  [env [_ bindings & body]]
  (let [parted (partition 2 bindings)]
    (analyze-form env
                  `((fn ~'__loop__fn__ ~(mapv first parted)
                      ~@body)
                    ~@(mapv second parted)))))

(defmethod analyze-seq 'recur
  [env [_ & args]]
  (assert (:tail? env) "Can only recur at tail position")
  (analyze-form env `(~'__loop__fn__ ~@args)))

(defmethod analyze-seq 'var
  [env [_ nm]]
  (->VarConst @(:ns env) nm nm env))

(defmethod analyze-seq 'def
  [env [_ nm val :as form]]
  (->Def
   nm
   (analyze-form env val)
   form
   env))

(defmethod analyze-seq 'quote
  [env [_ val]]
  (if (map? val)
    (analyze-seq (with-meta
                   `(pixie.stdlib/hashmap ~@(reduce
                                             (fn [acc [k v]]
                                               (-> acc
                                                   (conj `(~'quote k))
                                                   (conj `(~'quote v))))
                                             []
                                             val))
                   (meta val)))
    (->Const val env)))

(defmethod analyze-seq 'in-ns
  [env [_ nsp]]
  (reset! (:ns env) (symbol (name nsp)))
  (in-ns nsp)
  (in-ns :pixie.compiler)
  (analyze-form env (list 'pixie.stdlib/-in-ns (keyword (name nsp)))))

(defmethod analyze-seq 'local-macro
  [env [_ [nm replace] & body :as form]]
  (let [new-env (assoc-in env [:locals nm] {:op :local-macro
                                            :name nm
                                            :replace-with replace
                                            :form form})]
    (analyze-form new-env (cons 'do body))))

(defmethod analyze-form nil
  [env _]
  (->Const nil env))

(defmethod analyze-form :bool
  [env form]
  (->Const form env))

(defn keep-meta [new old]
  (if-let [md (meta old)]
    (if (satisfies? IMeta new)
      (with-meta new md)
      new)
    new))

(defmethod analyze-seq :default
  [env [sym & args :as form]]
  (let [sym (if (and (symbol? sym)
                     (= "pixie.bootstrap-macros" (namespace sym)))
              (symbol (str "pixie.stdlib/" (name sym)))
              sym)
        bootstrap-resolved (when (and (symbol? sym)
                                      (:bootstrap? env))
                             (try (and (symbol? sym)
                                       (resolve-in (the-ns :pixie.bootstrap-macros) (symbol (name sym))))
                                  (catch :pixie.stdlib/AssertionException ex
                                    nil)))
        resolved (try (and (symbol? sym)
                           (resolve-in (the-ns @(:ns env)) sym))
                      (catch :pixie.stdlib/AssertionException ex
                        nil))]
    (cond
      (and (symbol? sym)
           (string/starts-with? (name sym) ".-"))
      (let [sym-kw (keyword (string/substring (name sym) 2))
            result (analyze-form env (keep-meta `(~'pixie.stdlib/-get-field ~@args ~sym-kw)
                                                form))]
        result)

      (and bootstrap-resolved
           (macro? @bootstrap-resolved))
      (analyze-form env (keep-meta (apply @bootstrap-resolved args)
                                   form))
      
      (and resolved
           (macro? @resolved))
      (analyze-form env (keep-meta (apply @resolved args)
                                   form))

      :else
      (->Invoke (let [new-env (assoc env :tail? false)]
                  (analyze-form new-env sym))
                (let [new-env (assoc env :tail? false)]
                  (mapv (partial analyze-form new-env) args))
                (:tail? env)
                form
                env))))


(defmethod analyze-form :number
  [env x]
  (->Const x env))

(defmethod analyze-form :keyword
  [env x]
  (->Const x env))

(defmethod analyze-form :string
  [env x]
  (->Const x env))

(defmethod analyze-form :char
  [env x]
  (->Const x env))

(defmethod analyze-form :seq
  [env x]
  (analyze-seq env x))

(defmethod analyze-form :symbol
  [env x]
  (if-let [local (get-in env [:locals x])]
    (if (= (:op local) :local-macro)
      (analyze-form env (:replace-with local))
      (assoc local :form x))
    (maybe-var env x)))

(defmethod analyze-form :vector
  [env x]
  (->Vector (mapv (partial analyze-form env) x)
            x
            env))

(defmethod analyze-form :map
  [env x]
  (analyze-seq env
               (with-meta
                 `(pixie.stdlib/hashmap ~@(reduce
                                           (fn [acc [k v]]
                                             (-> acc
                                                 (conj k)
                                                 (conj v)))
                                           []
                                           x))
                 (meta x))))

(defmethod analyze-form :set
  [env x]
  (analyze-seq env
               (with-meta
                 `(pixie.stdlib/set ~(vec x))
                 (meta x))))

(defn maybe-var [env x]
  (->Var @(:ns env) x x env))


;; ENV Functions

(defn new-env
  "Creates a new (empty) environment"
  [bootstrap?]
  (->Env
   (atom 'pixie.stdlib)
   nil
   {}
   true
   nil
   bootstrap?))


(defn analyze
  ([form]
   (analyze form (new-env false)))
  ([form env]
   (analyze-form env form)))


