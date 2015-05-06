(ns pixie.compiler)

(def *env* nil)
(set-dynamic! (var *env*))

(defmulti analyze-form (fn [x]
                         (cond
                           (nil? x) nil
                           (seq? x) :seq
                           (vector? x) :vector
                           (symbol? x) :symbol
                           (number? x) :number
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
   :statements (mapv analyze-form (butlast (next x)))
   :ret (analyze-form (last x))})

(defmethod analyze-seq 'if
  [[_ test then else :as form]]
  {:op :if
   :children '[:test :then :else]
   :env *env*
   :form form
   :test (analyze-form test)
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
  (let [arity (count args)
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
                      :children '[:body]
                      :body (binding [*env* new-env]
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
                                                   :value (analyze-form binding-form)})]
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
  {:op :def
   :name nm
   :form form
   :env *env*
   :children [:val]
   :val (analyze-form val)})

(defmethod analyze-form nil
  [_]
  {:op :const
   :env *env*
   :form nil})

(defmethod analyze-seq :default
  [[sym & args :as form]]
  (println form)
  (let [resolved (and (symbol? sym)
                      (resolve-in (the-ns (:ns *env*)) sym))]
    (if (and resolved
             (macro? @resolved))
      (analyze-form (apply @resolved args))
      {:op :invoke
       :children '[:fn :args]
       :form form
       :env *env*
       :fn (analyze-form sym)
       :args (mapv analyze-form args)})))


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

(defmethod analyze-form :seq
  [x]
  (analyze-seq x))

(defmethod analyze-form :symbol
  [x]
  (if-let [local (get-in *env* [:locals x])]
    local
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
    (if resolved
      {:op :var
       :env *env*
       :ns (namespace resolved)
       :name (name resolved)
       :form x}
      {:op :var
       :env *env*
       :ns (name (:ns *env*))
       :name (name x)
       :form x})))


;; ENV Functions

(defn new-env
  "Creates a new (empty) environment"
  []
  {:ns 'user})


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

(defn write! [sb val]
  (swap! sb conj! val)
  sb)

(defn offset-spaces [sb off]
  (dotimes [x off]
    (write! sb "  ")))

(defmulti to-rpython (fn [sb offset node]
                       (println (:op node))
                         (:op node)))

(defmethod to-rpython :if
  [sb offset {:keys [test then else]}]
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
  (write! sb ")")))

(defmulti write-const (fn [sb offset const]
                         (:type const)))

(defmethod write-const :keyword
  [sb offset {:keys [form]}]
  (write! sb "kw(u\"")
  (when (namespace form)
    (write! sb (namespace form))
    (write! sb "/"))
  (write! sb (name form))
  (write! sb "\")"))

(defmethod to-rpython :const
  [sb offset ast]
  (write! sb "i.Const(")
  (write-const sb offset ast)
  (write! sb ")"))

(defmethod to-rpython :invoke
  [sb offset ast]
  (write! sb "i.Invoke(\n")
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
  [sb offset {:keys [ret statements]}]
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
  (write! sb ")"))


(defmethod to-rpython :fn
  [sb offset {:keys [name arities]}]
  (assert (= (count arities) 1))
  (to-rpython-fn-body sb offset name (nth arities 0)))

(defn to-rpython-fn-body
  [sb offset name {:keys [args body]}]
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
  (write! sb ")"))

(defmethod to-rpython :var
  [sb offset {:keys [ns name]}]
  (write! sb "i.Const(code.intern_var(")
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
    (write! sb "i.Const(code.intern_var(u\"pixie.stdlib\", u\"vector\")),\n")
    (doseq [item items]
      (offset-spaces sb offset)
      (to-rpython sb offset item)
      (write! sb ",\n"))
    (offset-spaces sb offset)
    (write! sb "])")))


(let [form '(do (deftype Cons [head tail meta]))]
  (println (string-builder @(to-rpython (atom (string-builder)) 0 (clean-do (analyze form))))))

