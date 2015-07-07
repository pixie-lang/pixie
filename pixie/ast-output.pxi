(ns pixie.ast-output
  (:require [pixie.ast.internal :as iast]
            [pixie.ast :as ast]))

(defprotocol ToNativeAST
  (-to-ast [this]))

(defn meta-ast [ast]
  (let [{:keys [line file line-number column-number] :as m} (or (meta (:form ast))
                                                                (:meta (:env ast)))
        line (if (string? line)
               line
               (apply str @line))]
     
    (iast/->Meta (or line
                     "<unknown>")
                 (or file
                     "<unknown>")
                 (or line-number -1)
                 (or column-number 1))))

(defn to-ast [this]
  (-to-ast (simplify this)))

(extend-protocol ToNativeAST
  
  ast/If
  (-to-ast [{:keys [test then else] :as ast}]
    (iast/->If (to-ast test)
               (to-ast then)
               (to-ast else)
               (meta-ast ast)))

  ast/Let
  (-to-ast [{:keys [bindings body] :as ast}]
    (iast/->Let (apply array (map #(keyword (name (:name %)))
                                  bindings))
                (apply array (map #(to-ast :value %)
                                  bindings))
                (to-ast body)
                (meta-ast ast)))

  ast/Do
  (-to-ast [{:keys [statements ret] :as ast}]
    (println "DO " statements ret)
    (let [args-array (make-array (inc (count statements)))]
      (dotimes [idx (count statements)]
        (aset args-array idx
              (to-ast (nth statements idx))))

      (aset args-array (count statements)
            (to-ast ret))
      
      (iast/->Do args-array
                 (meta-ast ast))))

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
    (println "INVOKE > " (count args) args)
    (let [args-array (make-array (count args))]
      (dotimes [idx (count args)]
        (aset args-array idx
              (to-ast (nth args idx))))
      
      (iast/->Invoke args-array
                     (meta-ast ast))))

  ast/Var
  (-to-ast [{:keys [ns var-name] :as ast}]
    (iast/->VDeref (name ns)
                   var-name
                   (meta-ast ast)))

  
  Object
  (-to-ast [this]
    (println "Encoding" this "of type" (type this))
    (throw [:pixie.stdlib/IllegalArgumentException
            (str "Can't encode " this)])))

(defn simplify [ast]
  (let [simplified (ast/simplify-ast ast)]
    (if (identical? simplified ast)
      ast
      (simplify simplified))))


