(ns pixie.compiler)

(def *env* nil)
(set-dynamic! (var *env*))

(defmulti analyze-form (fn [x]
                         (cond
                           (nil? x) nil
                           (seq? x) :seq
                           (vector? x) :vector
                           (symbol? x) :symbol
                           (number? x) :number)))

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
                         analyze-fn-body
                         {}
                         arities)]
    {:op :fn
     :env *env*
     :form form
     :name name
     :children '[:arities]
     :arities (vals analyzed-bodies)}
    ))

(defn analyze-fn-body [acc [args & body]]
  ; TODO: Add support for variadic fns
  (let [arity (count args)
        new-env (reduce
                 (fn [acc idx]
                   (let [arg-name (nth args idx)]
                     (assoc-in acc [:locals arg-name] {:op :binding
                                                       :type :arg
                                                       :idx idx
                                                       :name arg-name
                                                       :form arg-name
                                                       :env *env*})))
                 *env*
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
  (let [resolved (resolve-in (the-ns (:ns *env*)) sym)]
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
   :form x
   :env *env*})

(defmethod analyze-form :seq
  [x]
  (analyze-seq x))

(defmethod analyze-form :symbol
  [x]
  (if-let [local (get-in *env* [:locals x])]
    local
    {:op :global
     :env *env*
     :form x}))


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


(defn remove-env [ast]
  (walk #(dissoc % :env)
        identity
        :children
        ast))

(let [form '((fn this [i max]
                (if (-lt i max)
                  (this (-add i 1)
                        max)
                  i))
             1000)]
  (println (string-builder @(to-rpython (atom (string-builder)) 0 (remove-env (analyze form))))))

(defn write! [sb val]
  (swap! sb conj! val)
  sb)

(defn offset-spaces [sb off]
  (dotimes [x off]
    (write! sb "  ")))

(defmulti to-rpython (fn [sb offset node]
                         (:op node)))

(defmethod to-rpython :if
  [sb offset {:keys [test then else]}]
  #_(offset-spaces sb offset)
  (write! sb "i.If(\n")
  (let [offset (inc offset)]
    (doseq [[nm form] [[:test test]
                       [:then then]
                       [:else else]]]
      (offset-spaces sb offset)
      (write! sb (name nm))
      (write! sb "=")
      (to-rpython sb offset form)
      (write! sb ",\n"))
  (offset-spaces sb offset)
  (write! sb ")")))

(defmethod to-rpython :const
  [sb offset {:keys [form]}]
  (write! sb "i.Const(rt.wrap(")
  (write! sb (str form))
  (write! sb "))"))



(defmethod rpython-node)
