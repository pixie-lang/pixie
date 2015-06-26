(ns pixie.compiler
  (:require [pixie.string :as string]
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
           type-nm (str @(:ns *env*) "." (name nm))
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
                                                 ~(symbol (str @(:ns *env*) "/" nm))
                                                 ~(mk-body body))
                                  :else (assert false "Unknown body element in deftype, expected symbol or seq"))))
                         conj
                         proto-bodies)]
       (println type-nm all-fields field-syms ctor)
       `(do ~type-decl
            ~ctor
            ~@proto-bodies)))

   (resolve 'ns)
   (fn ns [nm & body]
     (let [bmap (reduce (fn [m b]
                          (update-in m [(first b)] (fnil conj []) (rest b)))
                        {}
                        body)
           requires
           (do
             (assert (>= 1 (count (:require bmap)))
                     "Only one :require block can be defined per namespace")
             (mapv (fn [r] `(require ~(keyword (name nm)) ~@r)) (first (:require bmap))))]
       `(do (in-ns ~(keyword (name nm)))
            (println "in-ns " ~(keyword (name nm)))
            ~@requires)))

   (resolve 'require)
   (fn [ins ns & args]
  `(do (load-ns (quote ~ns))
       (assert (the-ns (quote ~ns))
               (str "Couldn't find the namespace " (quote ~ns) " after loading the file"))

       (apply refer ~ins (quote [~ns ~@args]))))



   })


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
                           (keyword? x) :keyword
                           (map? x) :map)))

(defmulti analyze-seq (fn [x]
                         (let [f (first x)]
                           (if (symbol? f)
                             (let [sname (symbol (name f))]
                               (if (get @(get-field analyze-seq :methods) sname)
                                 sname
                                 f))
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

(defmethod analyze-seq 'this-ns-name
  [[_]]
  (analyze-form (name @(:ns *env*))))

(defmethod analyze-seq 'with-handler
  [[_ [h handler] & body]]
  (analyze-form `(let [~h ~handler]
                   (~'pixie.stdlib/-effect-return
                    ~h
                    (~'pixie.stdlib/-with-handler
                     ~h
                     (fn []
                       (~'pixie.stdlib/-effect-val
                        ~h
                        (do ~@body))))))))

(defmethod analyze-seq 'defeffect
  [[_ nm & sigs]]
  (analyze-form `(do (def ~nm (~'pixie.stdlib/protocol ~(str nm)))
                    ~@(map (fn [[x]]
                             `(def ~x (~'pixie.stdlib/-effect-fn
                                       (~'pixie.stdlib/polymorphic-fn ~(str x) ~nm))))
                           sigs))))


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

(defmethod analyze-seq 'var
  [[_ nm]]
  (->VarConst @(:ns *env*) nm nm env))

(defmethod analyze-seq 'def
  [[_ nm val :as form]]
  (->Def
   nm
   (analyze-form val)
   form
   *env*))

(defmethod analyze-seq 'quote
  [[_ val]]
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
    (->Const val *env*)))

(defmethod analyze-seq 'in-ns
  [[_ nsp]]
  (reset! (:ns *env*) (symbol (name nsp)))
  (in-ns nsp)
  (in-ns :pixie.compiler)
  (analyze-form (list 'pixie.stdlib/-in-ns (keyword (name nsp)))))

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
                           (resolve-in (the-ns @(:ns *env*)) sym))
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

(defmethod analyze-form :map
  [x]
  (analyze-seq (with-meta
                 `(pixie.stdlib/hashmap ~@(reduce
                                           (fn [acc [k v]]
                                             (-> acc
                                                 (conj k)
                                                 (conj v)))
                                           []
                                           x))
                 (meta x))))

(defn maybe-var [x]
  (->Var @(:ns *env*) x x *env*))


;; ENV Functions

(defn new-env
  "Creates a new (empty) environment"
  []
  (->Env
   (atom 'pixie.stdlib)
   nil
   {}
   true
   nil))


(defn analyze
  ([form]
   (analyze form (new-env)))
  ([form env]
   (if *env*
     (analyze-form form)
     (binding [*env* env]
       (analyze-form form)))))


