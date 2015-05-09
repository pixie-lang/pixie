(ns pixie.compiler
  (:require [pixie.io :as io]))

(def macro-overrides
  {
   (resolve 'defprotocol)
   (fn
     [nm & sigs]
     `(do (def ~nm (protocol ~(str nm)))
          ~@(map (fn [[x]]
                   `(def ~x (polymorphic-fn ~(str x) ~nm)))
                 sigs)))})


(def *env* nil)
(set-dynamic! (var *env*))

(defmulti analyze-form (fn [x]
                         (println "Meta --> " (meta x))
                         (cond
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
        new-env (assoc-in *env* [:locals fn-name] {:op :binding
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
    (assert (not (acc arity)) (str "Duplicate arity for " (cons args body)))
    (assoc acc arity {:op :fn-body
                      :env *env*
                      :arity arity
                      :args args
                      :variadic? variadic?
                      :children '[:body]
                      :body (binding [*env* (assoc new-env :tail? true)]
                              (analyze-form (cons 'do body)))})))


(defmethod analyze-seq 'let*
  [[_ bindings & body :as form]]
  (assert (even? (count bindings)) "Let requires an even number of bindings")
  (let [parted (partition 2 bindings)
        [new-env bindings] (reduce
                            (fn [[new-env bindings] [name binding-form]]
                              (let [binding-ast (binding [*env* new-env]
                                                  {:op :binding
                                                   :type :let
                                                   :children [:value]
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
     :children [:bindings :body]
     :bindings bindings
     :env *env*
     :body (binding [*env* new-env]
             (analyze-form `(do ~@body)))}))

(defmethod analyze-seq 'def
  [[_ nm val :as form]]
  (swap! (:vars *env*) update-in [(:ns *env*) nm] (fn [x]
                                          (or x :def)))
  {:op :def
   :name nm
   :form form
   :env *env*
   :children [:val]
   :val (analyze-form val)})

(defmethod analyze-seq 'quote
  [[_ val]]
  {:op :const
   :type (cond
           (symbol? val) :symbol
           (string? val) :string
           :else :unknown)
   :form val})

(defmethod analyze-seq 'local-macro
  [[_ [nm replace] body :as form]]
  (binding [*env* (assoc-in *env* [:locals nm] {:op :local-macro
                                                :name nm
                                                :replace-with replace
                                                :form form})]
    (analyze-form body)))

(defmethod analyze-form nil
  [_]
  {:op :const
   :type (keyword "nil")
   :env *env*
   :form nil})

(defmethod analyze-seq :default
  [[sym & args :as form]]
  (println form)
  (let [resolved (and (symbol? sym)
                      (resolve-in (the-ns (:ns *env*)) sym))]
    (println "fff" (contains? macro-overrides resolved))
    (cond
      (and resolved
           (contains? macro-overrides resolved))
      (analyze-form (apply (macro-overrides resolved) args))
      
      (and resolved
           (macro? @resolved))
      (analyze-form (apply @resolved args))

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
      local)
    (maybe-var x)))

(defmethod analyze-form :vector
  [x]
  (println "analyze " x)
  {:op :vector
   :children [:items]
   :items (mapv analyze-form x)
   :form x
   :env *env*})

(defn maybe-var [x]
  (let [resolved (resolve-in (the-ns (:ns *env*)) x)]
    (cond
      (get-in @(:vars *env*) [(:ns *env*) x])
      {:op :var
       :env *env*
       :ns (:ns *env*)
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
       :form x})))


;; ENV Functions

(defn new-env
  "Creates a new (empty) environment"
  []
  {:ns 'pixie.stdlib
   :vars (atom nil)
   :tail? true})


(defn analyze [form]
  (binding [*env* (new-env)]
    (analyze-form form)))





(defn walk [post pre selector node]
  (-> (reduce
       (fn [node k]
         (let [v (get node k)
               result (if (or (vector? v)
                              (seq? v))
                        (mapv (partial walk post pre selector) v)
                        (walk post pre selector v))]
           (assoc node k result)))
       (pre node)
       (selector node))
      post))

(defn post-walk [f ast]
  (walk f identity :children ast))

(defn clean-do [ast]
  (post-walk
   (fn [{:keys [op statements ret] :as do}]
     (println ">-- " op (count statements))
     (if (and (= op :do)
              (= (count statements) 0))
       (do (println "reducing ") ret)
       ast))
   ast))

(defn remove-env [ast]
  (walk #(dissoc % :env)
        identity
        :children
        ast))

(defn write! [{:keys [code] :as state} val]
  (swap! code conj! val)
  state)

(defn add-meta [{:keys [meta-state meta-lines] :as state} ast]
  (let [m (meta (:form ast))]
    (if m
      (let [k [(:line m) (:file m)]
            id (get @meta-state k)]
        (if id
          id
          (let [id (str "mid" (count @meta-state))]
            (swap! meta-state assoc k id)
            (swap! meta-lines conj! (str id " = (u\"" (:line m) "\", \"" (:file m) "\")\n"))
            id)))
      "nil")))

(defn meta-str [state ast]
  (println (:form ast) (meta (:form ast)))
  (let [m (meta (:form ast))]
    (if m
      (str "Meta(" (add-meta state ast) ", " (:line-number m) ", " (:column-number m) ")")
      "nil")))

(defn offset-spaces [sb off]
  (dotimes [x off]
    (write! sb "  ")))

(defmulti to-rpython (fn [sb offset node]
                       (println (:op node))
                         (:op node)))

(defmethod to-rpython :if
  [sb offset {:keys [test then else] :as ast}]
  #_(offset-spaces sb offset)
  (write! sb "i.If(\n")
  (let [offset (inc offset)]
    (doseq [[nm form] [[:test test]
                       [:then then]
                       [:els else]]]
      (offset-spaces sb offset)
      (write! sb (name nm))
      (write! sb "=")
      (to-rpython sb offset form)
      (write! sb ",\n"))
  (offset-spaces sb offset)
  (write! sb "meta=")
  (write! sb (meta-str sb ast))

  (write! sb ")")))

(defmulti write-const (fn [sb offset const]
                        (println "const " const)
                         (:type const)))

(defmethod write-const :keyword
  [sb offset {:keys [form]}]
  (write! sb "kw(u\"")
  (when (namespace form)
    (write! sb (namespace form))
    (write! sb "/"))
  (write! sb (name form))
  (write! sb "\")"))

(defmethod write-const (keyword "nil")
  [sb offset _]
  (write! sb "nil"))

(defmethod write-const :symbol
  [sb offset {:keys [form]}]
  (write! sb "sym(u\"")
  (when (namespace form)
    (write! sb (namespace form))
    (write! sb "/"))
  (write! sb (name form))
  (write! sb "\")"))

(defmethod write-const :string
  [sb offset {:keys [form]}]
  (write! sb "rt.wrap(u\"")
  (write! sb form)
  (write! sb "\")"))

(defmethod write-const :number
  [sb offset {:keys [form]}]
  (write! sb "rt.wrap(")
  (write! sb (str form))
  (write! sb ")"))

(defmethod to-rpython :const
  [sb offset ast]
  (write! sb "i.Const(")
  (write-const sb offset ast)
  (write! sb ")"))

(defmethod to-rpython :invoke
  [sb offset ast]
  (if (:tail-call ast)
    (write! sb "i.TailCall(\n")
    (write! sb "i.Invoke(\n"))
  (let [offset (inc offset)]
    (offset-spaces sb offset)
    (write! sb "args=[\n")
    (let [offset (inc offset)]
      (doseq [x `(~(:fn ast) ~@(:args ast))]
        (offset-spaces sb offset)
        (to-rpython sb offset x)
        (write! sb ",\n")))
    (offset-spaces sb offset)
    (write! sb "],\n"))
  (offset-spaces sb offset)
  (write! sb ")"))


(defmethod to-rpython :do
  [sb offset {:keys [ret statements] :as ast}]
  (write! sb "i.Do(\n")
  (let [offset (inc offset)]
    (offset-spaces sb offset)
    (write! sb "args=[\n")
    (let [offset (inc offset)]
      (doseq [x `(~@statements ~ret)]
        (offset-spaces sb offset)
        (to-rpython sb offset x)
        (write! sb ",\n")))
    (offset-spaces sb offset)
    (write! sb "],\n"))
  (offset-spaces sb offset)
  (write! sb "meta=")
  (write! sb (meta-str sb ast))
  (write! sb ")"))


(defmethod to-rpython :fn
  [sb offset {:keys [name arities]}]
  (if (= (count arities) 1)
    (to-rpython-fn-body sb offset name (nth arities 0))
    (do (write! sb (str "i.Invoke([i.Const(code.intern_var(u\"pixie.stdlib\", u\"multi-arity-fn\")), i.Const(rt.wrap(u\"" name "\")),\n"))
        (offset-spaces sb offset)
        (let [offset (inc offset)]
          (doseq [f arities]
            (when (not (:variadic? f))
              (offset-spaces sb offset)
              (write! sb (str "i.Const(rt.wrap(" (count (:args f)) ")), "))
              (to-rpython-fn-body sb offset name f)
              (write! sb ",\n")))
          (offset-spaces sb offset)
          (let [vfn (first (filter :variadic? arities))]
            (offset-spaces sb offset)
            (write! sb (str "i.Const(rt.wrap(-1)), \n"))
            (offset-spaces sb offset)
            (to-rpython-fn-body sb offset name vfn)
            (write! sb "\n")))
        (offset-spaces sb offset)
        (write! sb "])"))))

(defn to-rpython-fn-body
  [sb offset name {:keys [args body variadic?]}]
  (when variadic?
    (write! sb (str "i.Invoke([i.Const(code.intern_var(u\"pixie.stdlib\", u\"variadic-fn\")), i.Const(rt.wrap(" (dec (count args)) ")), \n"))
    (offset-spaces sb offset))
  (write! sb "i.Fn(args=[")
  (write! sb (->> args
                  (map (fn [name]
                              (str "kw(u\"" name "\")")))
                  (interpose ",")
                  (apply str)))
  (write! sb "],name=kw(u\"")
  (write! sb (str name))
  (write! sb "\"),\n")
  (let [offset (inc offset)]
    (offset-spaces sb offset)
    (write! sb "body=")
    (to-rpython sb offset body)
    (write! sb ",\n"))
  (offset-spaces sb offset)
  (write! sb ")")
  (if variadic?
    (write! sb "])")))

(defmethod to-rpython :var
  [sb offset {:keys [ns name]}]
  (write! sb "i.VDeref(code.intern_var(")
  (write! sb "u\"")
  (write! sb ns)
  (write! sb "\", u\"")
  (write! sb name)
  (write! sb "\"))"))

(defmethod to-rpython :binding
  [sb offset {:keys [name]}]
  (write! sb "i.Lookup(kw(u\"")
  (write! sb name)
  (write! sb "\"))"))

(defmethod to-rpython :def
  [sb offset {:keys [name env val]}]
  (write! sb "i.Invoke(args=[\n")
  (write! sb (str "# (def " (:ns env) "/" name ")\n"))
  (let [offset (inc offset)]
    (offset-spaces sb offset)
    (write! sb "i.Const(code.intern_var(u\"pixie.stdlib\", u\"set-var-root!\")),\n")
    (offset-spaces sb offset)
    (write! sb "i.Const(code.intern_var(u\"")
    (write! sb (:ns env))
    (write! sb "\",u\"")
    (write! sb name)
    (write! sb "\")),\n")
    (offset-spaces sb offset)
    (to-rpython sb offset val)
    (write! sb "])")
    ))

(defmethod to-rpython :vector
  [sb offset {:keys [items]}]
  (write! sb "i.Invoke(args=[\n")
  (let [offset (inc offset)]
    (offset-spaces sb offset)
    (write! sb "i.Const(code.intern_var(u\"pixie.stdlib\", u\"array\")),")
    (doseq [item items]
      (offset-spaces sb offset)
      (to-rpython sb offset item)
      (write! sb ",\n"))
    (offset-spaces sb offset)
    (write! sb "])")))


(defn writer-context []
  {:meta-lines (atom (string-builder))
   :meta-state (atom {})
   :code (atom (string-builder))})

(defn finish-context [{:keys [meta-lines code]}]
  (str (string-builder @meta-lines)
       "\n \n"
       (string-builder @code)))

(let [form 
      '(do (defn +
             ([] 0)
             ([x] x)
             ([x y] (-add x y))
             ([x y & more]
              (-apply + (+ x y) more)))

           ((fn c [i max]
              (if (-lt i max)
                (c (+ i 1 1) max)
                max))
            0 10000))
      str (finish-context (to-rpython (writer-context) 0 (clean-do (analyze form))))]
  (print str)
  (io/spit "/tmp/pxi.py" str))

#_'(do
              (defprotocol ISeq
                (-first [this])
                (-next [this]))
              (defprotocol IMeta
                (-meta [this]))
              (deftype Cons [head tail meta]
                  ISeq
                  (-first [this]
                    head)
                  (-next [this]
                    tail)
                  IMeta
                  (-meta [this]
                    meta))
                )
