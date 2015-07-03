(ns pixie.ast-output
  (:require [pixie.ast.internal :as iast]
            [pixie.ast :as ast]))

(defprotocol ToNativeAST
  (-to-ast [this]))

(defn meta-ast [ast]
  nil)

(defn to-ast [this]
  (-to-ast this))

(extend-protocol ToNativeAST
  
  ast/If
  (-to-ast [{:keys [test then else] :as ast}]
    (ast/->If (to-ast test)
              (to-ast then)
              (to-ast else)
              (meta-ast ast)))

  ast/Let
  (-to-ast [{:keys [bindings body] :as ast}]
    (ast/->Let (apply array (map #(keyword (name (:name %)))
                                 bindings))
               (apply array (map #(to-ast :value %)
                                 bindings))
               (to-ast body)
               (meta-ast ast)))


  ast/LetBinding
  (-to-ast
    [{:keys [name] :as ast}]
    (iast/->Lookup name
                   (meta-ast ast)))
  
  
  ast/Const
  (-to-ast [{:keys [form] :as ast}]
    (iast/->Const form (meta-ast ast)))

  ast/Invoke
  (-to-ast [{:keys [args] :as ast}]
    (let [args-array (make-array (inc (count args)))]
      (aset args-array 0 (to-ast (:fn ast)))
      (loop [idx 0]
        (when (< idx (count args))
          (aset args-array
                (inc idx)
                (to-ast (nth args idx)))
          (recur (inc idx))))
      (iast/->Invoke args-array
                     (meta-ast ast))))

  
  Object
  (-to-ast [this]
    (println this)
    (throw [:pixie.stdlib/IllegalArgumentException
            (str "Can't encode " this)])))

(defn simplify [ast]
  (let [simplified (ast/simplify-ast ast)]
    (if (identical? simplified ast)
      ast
      (recur simplified))))


