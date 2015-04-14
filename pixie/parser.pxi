(ns pixie.parser
  (:require [pixie.stdlib :as s]))


;; This file contans a small framework for writing generic parsers in Pixie. Although the generated
;; code is probably not the fastest, it is fairly simple, and that simplicity should open the road for
;; future optimizations. The parsers allowed support multiple inheritance and multiple input data types.
;; Backtracking is supported by snapshots taken at key parts of the parsing process. For a string parser
;; these snapshots are simply a integer index into the string being parsed.

;; Cursors

(defprotocol ICursor
  (next! [this] "Advance to the next element")
  (current [this] "Return the current element")
  (snapshot [this] "Return a snapshot of the cursor's mutable state")
  (rewind! [this snapshot] "Rewind the cursor to a previous snapshot")
  (at-end? [this] "Is there more to parse?"))

(deftype StringCursor [idx s]
  ICursor
  (next! [this]
    (set-field! this :idx (inc idx)))
  (current [this]
    (when (< idx (count s))
      (nth s idx)))
  (snapshot [this]
    idx)
  (rewind! [this val]
    (set-field! this :idx val))
  (at-end? [this]
    (= idx (count s))))

;; Create a cursor from the given string
(defn string-cursor [s]
  (->StringCursor 0 s))

;; Mechanics

(deftype ParseFailure [])

;; If a parser returns this value, parsing has failed
(def fail (->ParseFailure))

(defn failure?
  "Returns true if return value from a parser is a parse failure"
  [v]
  (identical? v fail))

(defn parse-if
  "Parse and return the current value of the cursor if this predicate succeeds against the cursor. Advances
  the cursor to the next element."
  [pred]
  (fn [cursor]
    (if (pred (current cursor))
      (let [value (current cursor)]
        (next! cursor)
        value)
      fail)))


(defprotocol IParserGenerator
  (to-parser [this] "Convert the current object to a parser"))

(extend-protocol IParserGenerator
  IFn
  (to-parser [this]
    this)
  Character
  (to-parser [this]
    (parse-if #(= % this)))
  String
  (to-parser [this]
    (println "bad-parser " this)
    (assert false)))




(defn or
  "Defines a parser that succeeds if one of the provided parsers succeeds. Parsers are tried in-order."
  ([a] a)
  ([a b]
   (let [a (to-parser a)
         b (to-parser b)
         m (atom #{})]
     (fn [cursor]
       (let [key [cursor (snapshot cursor)]]
         (if-let [v (contains? @m key)]
           (b cursor)
           (let [_ (swap! m conj key)
                 state (snapshot cursor)
                 val (a cursor)]
             (swap! m disj key)
             (if (identical? val fail)
               (do (rewind! cursor state)
                   (b cursor))
               val)))))))
  ([a b & more]
   (apply or (or a b) more)))

(defn add-clauses [cursor-sym body [[sym goal] & more]]
  (if sym
    `(let [~sym (~sym ~cursor-sym)]
       (if (identical? ~sym fail)
         fail
         ~(add-clauses cursor-sym body more)))
    body))

(defn -parse-args
  [args]
  (loop [args args
         rules []
         return nil]
    (let [[arg & rest] args]
      (assert (not (= '-> arg)) "invalid position for ->")
      (if arg
        (if (= '<- arg)
          (let [return (first rest)]
            (recur (next rest)
                   rules
                   return))
          (if (= (first rest) '->)
            (let [binding (-> rest next first)
                  rest (-> rest next next)]
              (recur rest
                     (conj rules [binding arg])
                     return))
            (recur rest
                   (conj rules [(gensym "_") arg])
                   return)))
        [rules return]))))

(defmacro and
  "Defines a parser that succeeds only if all parsers succeed. Tried in order. Each parser clause can be followed
  by a -> to give the parser's output a name. There may also be a single <- followed by any Pixie code that can be used
  to post-process the parsed output."
  [& args]
  (let [[parsed body] (-parse-args args)
        cursor-sym (gensym "cursor")]
    `(let [~@(mapcat
               (fn [[sym parser]]
                 [sym `(to-parser ~parser)])
               parsed)]
       (fn [~cursor-sym]
         (let [prev-pos# (snapshot ~cursor-sym)
               result# ~(add-clauses cursor-sym body parsed)]
           (if (identical? result# fail)
             (do (rewind! ~cursor-sym prev-pos#)
                 fail)
             result#))))))


(defprotocol IDeliverable
  (-deliver [this val]))

(deftype PromiseFn [f name]
  IDeliverable
  (-deliver [this val]
    (set-field! this :f val))
  IFn
  (-invoke [this val]
    (assert f (str "PromiseFN " name " has not been delivered"))
    (f val)))

(defn promise-fn
  "Defines a promise that is callable."
  [name]
  (->PromiseFn nil name))

(defn -parse-parser-args [args]
  (loop [rules {}
         args args]
    (if args
      (let [name (first args)
            body (second args)
            args (-> args next next)]
        (assert (symbol? name) "Must name all rules")
        (if (= '<- (first args))
          (let [return (first (next args))
                full-rule `(let [p# (to-parser ~body)]
                              (fn [cursor#]
                                      (let [~'value (p# cursor#)]
                                        (if (failure? ~'value)
                                          ~'value
                                          ~return))))]
            (recur (assoc rules name full-rule)
                   (next (next args))))
          (recur (assoc rules name body)
                 args)))
      rules)))

(defmacro parser
  "(parser nm inherits & rules)
  Defines a new parser named `nm` that inherits from zero or more other parsers defined ion `inherits`. Rules are pairs
  of names and rules that will be assigned to those names. Names are inherited from parent parsers in the order they are
  defined."
  [inherits & rules]
  (let [parted (apply merge
                      (conj (mapv (fn [sym]
                                    (::forms (deref (resolve-in *ns* sym))))
                                  inherits)
                            (-parse-parser-args rules)))
        rules (apply concat parted)
        syms (keys parted)]
    `(let [~@(mapcat (fn [s]
                       `[~s (promise-fn (quote ~s))])
                     syms)]
       ~@(map (fn [[s goal]]
                `(-deliver ~s ~goal))
              parted)
       ~(assoc (zipmap (map (comp keyword name) syms)
                       syms)
          ::forms (list 'quote (apply hashmap rules))))))

(defmacro defparser
  "(defparser nm inherits rules)
  Same as parser but assigns the resulting parser to a var with the name nm"
  [nm inherits & rules]
  `(def ~nm (parser ~inherits ~@rules)))

;; Common parsers

(defn char-range
  "Defines a parser that parses a numerical range of characters"
  [from to]
  (parse-if (fn [v]
              (when (char? v)
                (<= (int from) (int v) (int to))))))

(defn one+
  "Defines a parser that succeeds if the given parser succeeds once or more. Will return a vector, but any
  reducing function can be provided via rf as well."
  ([g]
   (one+ g conj))
  ([g rf]
    (let [g (to-parser g)]
      (fn [cursor]
        (loop [acc (rf)
               cnt 0]
          (let [prev-pos (snapshot cursor)
                v (g cursor)]
            (if (identical? v fail)
              (if (= 0 cnt)
                (do (rewind! cursor prev-pos)
                    fail)
                (rf acc))
              (recur (rf acc v)
                     (inc cnt)))))))))

(def one+chars #(one+ % string-builder))

(defn zero+
  "Defines a parser that succeeds if a given parser succeeds zero or more times. Will return a vector, but
  any reducing function can be provided via rf as well."
  ([g]
   (zero+ g conj))
  ([g rf]
    (let [g (to-parser g)]
      (fn [cursor]
        (loop [acc (rf)]
          (let [v (g cursor)]
            (if (identical? v fail)
              (rf acc)
              (recur (rf acc v)))))))))

(def zero+chars #(zero+ % string-builder))

(defn eat
  "Eagerly parses as many values as possible until g fails. Discards the result, returns nil."
  [g]
  (fn [cursor]
    (loop []
      (let [prev-pos (snapshot cursor)
            v (g cursor)]
        (if (identical? v fail)
          (do (rewind! cursor prev-pos)
              nil)
          (recur))))))

(defn maybe
  "Always succeeds, returns nil when the input did not match the parser."
  ([g]
   (maybe g nil))
  ([g default]
   (let [g (to-parser g)]
     (fn [cursor]
       (let [v (g cursor)]
         (if (failure? v)
           default
           v))))))

(defmacro sequence
  [coll arrow body]
  (assert (= '<- arrow) "Middle argument to sequence must be a return arrow")
  `(and ~@coll ~'<- ~body))

(defn end
  "A parser that only succeeds if there is no more input left to process."
  [cursor]
  (if (at-end? cursor)
    nil
    fail))

(defn one-of
  "Deines a parser that succeeds if the value being parsed is found in v"
  [v]
  (parse-if (partial contains? v)))

(def digits (parse-if (set "1234567890")))

(def whitespace (parse-if #{\newline \return \space \tab}))
