(ns pixie.ast)

(defprotocol IAst
  (children-keys [this]))

(extend-type Object
  IAst
  (children-keys [this]
    (throw [:pixie.stdlib/IllegalArgumentException
            (str "Can't get AST keys of " this)])))

(defrecord Meta [line column-number])
(defrecord LineMeta [line file line-number])

(defrecord Do [statements ret form env]
  IAst
  (children-keys [this]
    `[:statements :ret]))

(defrecord If [test then else form env]
  IAst
  (children-keys [this]
    `[:test :then :else]))

(defrecord Fn [name arities form env]
  IAst
  (children-keys [this]
    `[:arities]))

(defrecord Binding [type name form env]
  IAst
  (children-keys [this]
    `[]))

(defrecord FnBody [name arity args closed-overs variadic? body form env]
  IAst
  (children-keys [this]
    `[:body]))

(defrecord Let [bindings body form env]
  IAst
  (children-keys [this]
    `[:bindings :body]))

(defrecord LetBinding [name value form env]
  IAst
  (children-keys [this]
    `[:value]))

(defrecord Def [name value form env]
  IAst
  (children-keys [this]
    `[:value]))


(defrecord LocalMacro [name respace form env])

(defrecord Invoke [args tail-call? form env]
  IAst
  (children-keys  [this]
    `[:args]))

(defrecord Var [ns var-name form env]
  IAst
  (children-keys [this]
    `[]))

(defrecord VarConst [ns name form env]
  IAst
  (children-keys [this]
    `[]))

(defrecord Const [form env]
  IAst
  (children-keys [this]
    `[]))

(defrecord Vector [items form env]
  IAst
  (children-keys [this]
    `[:items]))

(defrecord Env [ns vars locals tail? meta bootstrap?])

;; Ctors


(defn make-invoke-ast [f args form env]
  (->Invoke (cons f args) false form env))

(defn make-var-ast [ns name env]
  (->Var ns name (symbol (pixie.stdlib/name name)) env))


(defn make-var-const-ast [ns name env]
  (->VarConst ns (symbol (pixie.stdlib/name name)) name env))    

(defn make-invoke-var-ast [ns name args form env]
  (make-invoke-ast
   (make-var-ast ns name env)
   args
   form
   env))

;;

(defn convert-fn-body [name {:keys [variadic? args body form env] :as ast}]
  (if variadic?
    (make-invoke-var-ast
     "pixie.stdlib"
     (symbol "variadic-fn")
     [(->Const (dec (count args)) env) 
      (convert-fn-body name (assoc ast :variadic? false))]
     form
     env)
    ast))

(defprotocol ISimplfy
  (simplify-ast [ast]))

(extend-protocol ISimplfy
  Do
  (simplify-ast [{:keys [statements ret] :as ast}]
    (if (= (count statements) 0)
      ret
      ast))

  Let
  (simplify-ast [{:keys [bindings body] :as ast}]
    (if (= (count bindings) 0)
      body
      ast))

  Fn
  (simplify-ast [{:keys [name arities form env]}]
    (if (= (count arities) 1)
      (convert-fn-body name (first arities))
      (make-invoke-var-ast
       "pixie.stdlib"
       (symbol "multi-arity-fn")
       (persistent! (reduce
                     (fn [acc {:keys [args variadic?] :as body}]
                       (-> acc
                           (conj! (->Const (if variadic?
                                             -1
                                             (count args))
                                           env))
                           (conj! (convert-fn-body name body))))
                     (transient [(->Const (pixie.stdlib/name name)
                                          env)])
                     arities))
       form
       env)))

  Vector
  (simplify-ast [{:keys [items form env]}]
    (make-invoke-var-ast
     "pixie.stdlib"
     (if (:bootstrap? env)
       (symbol "array")
       (symbol "vector"))
     items
     form
     env))


  Def
  (simplify-ast [{:keys [name env value form]}]
    (make-invoke-var-ast
       "pixie.stdlib"
       (symbol "set-var-root!")
       [(make-var-const-ast @(:ns env) name env)
        value]
       form
       env))

  Object
  (simplify-ast [this]
    this))
