mid0 = (u"""     `(do (def ~nm (~'pixie.stdlib/protocol ~(str nm)))""", "pixie/compiler.pxi", 10)
mid1 = (u"""                   `(def ~x (~'pixie.stdlib/polymorphic-fn ~(str x) ~nm)))""", "pixie/compiler.pxi", 12)
mid2 = (u"""(defprotocol ISeq""", "<unknown>", 4)
mid3 = (u"""(defprotocol ISeqable""", "<unknown>", 8)
mid4 = (u"""(defprotocol ICounted""", "<unknown>", 11)
mid5 = (u"""(defprotocol IIndexed""", "<unknown>", 14)
mid6 = (u"""(defprotocol IPersistentCollection""", "<unknown>", 19)
mid7 = (u"""(defprotocol IEmpty""", "<unknown>", 23)
mid8 = (u"""(defprotocol IObject""", "<unknown>", 26)
mid9 = (u"""(defprotocol IReduce""", "<unknown>", 32)
mid10 = (u"""(defprotocol IDeref""", "<unknown>", 35)
mid11 = (u"""(defprotocol IReset""", "<unknown>", 38)
mid12 = (u"""(defprotocol INamed""", "<unknown>", 41)
mid13 = (u"""(defprotocol IAssociative""", "<unknown>", 45)
mid14 = (u"""(defprotocol ILookup""", "<unknown>", 50)
mid15 = (u"""(defprotocol IMapEntry""", "<unknown>", 53)
mid16 = (u"""(defprotocol IStack""", "<unknown>", 57)
mid17 = (u"""(defprotocol IPop""", "<unknown>", 60)
mid18 = (u"""(defprotocol IFn""", "<unknown>", 63)
mid19 = (u"""(defprotocol IDoc""", "<unknown>", 66)
mid20 = (u"""(defprotocol IMeta""", "<unknown>", 73)
mid21 = (u"""(defprotocol ITransientCollection""", "<unknown>", 77)
mid22 = (u"""(defprotocol IToTransient""", "<unknown>", 80)
mid23 = (u"""(defprotocol ITransientStack""", "<unknown>", 83)
mid24 = (u"""(defprotocol IDisposable""", "<unknown>", 87)
mid25 = (u"""(defprotocol IMessageObject""", "<unknown>", 90)
mid26 = (u"""(extend -get-field Object -internal-get-field)""", "<unknown>", 96)
mid27 = (u"""  (-eq [this other]""", "<unknown>", 106)
mid28 = (u"""(extend-type Object""", "<unknown>", 99)
mid29 = (u"""  (-repr  [x sb]""", "<unknown>", 103)
mid30 = (u"""    (sb (-internal-to-repr x)))""", "<unknown>", 104)
mid31 = (u"""  (-str [x sb]""", "<unknown>", 100)
mid32 = (u"""    (sb (-internal-to-str x)))""", "<unknown>", 101)
mid33 = (u"""  (-str [this sb]""", "<unknown>", 111)
mid34 = (u"""(extend-type String""", "<unknown>", 109)
mid35 = (u"""    (sb this)))""", "<unknown>", 112)
mid36 = (u"""(extend -eq Number -num-eq)""", "<unknown>", 116)
mid37 = (u"""  ([x] x)""", "<unknown>", 123)
mid38 = (u"""  ([x y] (-add x y))""", "<unknown>", 124)
mid39 = (u"""   (-apply + (+ x y) more)))""", "<unknown>", 126)
mid40 = (u"""  ([x] x)""", "<unknown>", 130)
mid41 = (u"""  ([x y] (-sub x y))""", "<unknown>", 131)
mid42 = (u"""   (-apply - (- x y) more))) """, "<unknown>", 133)
mid43 = (u"""  ([x] (+ x 1)))""", "<unknown>", 136)
mid44 = (u"""  ([x] (- x 1)))""", "<unknown>", 139)
mid45 = (u"""  ([x y] (-lt x y))""", "<unknown>", 142)
mid46 = (u"""   (-apply < (< x y) more)))""", "<unknown>", 144)
mid47 = (u"""  ([x y] (-gt x y))""", "<unknown>", 147)
mid48 = (u"""   (-apply > (> x y) more)))""", "<unknown>", 149)
mid49 = (u"""  ([x y] (-lte x y))""", "<unknown>", 154)
mid50 = (u"""  ([x y & rest] (if (-lte x y)""", "<unknown>", 155)
mid51 = (u"""                  (apply <= y rest)""", "<unknown>", 156)
mid52 = (u"""  ([x y] (-gte x y))""", "<unknown>", 161)
mid53 = (u"""  ([x y & rest] (if (-gte x y)""", "<unknown>", 162)
mid54 = (u"""                  (apply >= y rest)""", "<unknown>", 163)
mid55 = (u"""  ([x y] (if (identical? x y)""", "<unknown>", 173)
mid56 = (u"""           (-eq x y)))""", "<unknown>", 175)
mid57 = (u"""  ([x y & rest] (if (eq x y)""", "<unknown>", 176)
mid58 = (u"""                  (apply = y rest)""", "<unknown>", 177)
mid59 = (u"""  ([coll] coll)""", "<unknown>", 182)
mid60 = (u"""  ([coll itm] (-conj coll itm))""", "<unknown>", 183)
mid61 = (u"""   (-apply conj (conj x y) more)))""", "<unknown>", 185)
mid62 = (u"""  ([coll idx not-found] (-nth-not-found coll idx not-found)))""", "<unknown>", 194)
mid63 = (u"""  ([coll idx] (-nth coll idx))""", "<unknown>", 193)
mid64 = (u"""  ([coll] (-count coll)))""", "<unknown>", 198)
mid65 = (u"""(deftype Cons [first next meta]""", "<unknown>", 201)
mid66 = (u"""  (-first [this] first)""", "<unknown>", 203)
mid67 = (u"""  (-next [this] next)""", "<unknown>", 204)
mid68 = (u"""  (-seq [this] this)""", "<unknown>", 206)
mid69 = (u"""  (-meta [this] meta)""", "<unknown>", 208)
mid70 = (u"""  (-with-meta [this new-meta]""", "<unknown>", 209)
mid71 = (u"""    (->Cons first next new-meta)))""", "<unknown>", 210)
mid72 = (u"""  (->Cons head (seq tail) nil))""", "<unknown>", 213)
mid73 = (u"""  ([] (-string-builder))""", "<unknown>", 218)
mid74 = (u"""  ([sb] (-str sb))""", "<unknown>", 219)
mid75 = (u"""   (if (instance? String x)""", "<unknown>", 221)
mid76 = (u"""     (-add-to-string-builder x)""", "<unknown>", 222)
mid77 = (u"""     (-add-to-string-bulder (-str x)))))""", "<unknown>", 223)
mid78 = (u"""  (transduce""", "<unknown>", 226)
mid79 = (u"""   (map str)""", "<unknown>", 227)
mid80 = (u"""   string-builder""", "<unknown>", 228)
mid81 = (u"""   args))""", "<unknown>", 229)
mid82 = (u"""  (let [sb (-string-builder)""", "<unknown>", 232)
mid83 = (u"""                 (-add-to-string-builder sb x))]""", "<unknown>", 234)
mid84 = (u"""           sb sb]""", "<unknown>", 236)
mid85 = (u"""    (loop [idx 0""", "<unknown>", 235)
mid86 = (u"""      (if (< idx (count args))""", "<unknown>", 237)
mid87 = (u"""        (recur (inc idx)""", "<unknown>", 238)
mid88 = (u"""               (do (-str (aget args idx) add-fn)""", "<unknown>", 239)
mid89 = (u"""                   (add-fn " ")""", "<unknown>", 240)
mid90 = (u"""                 sb))""", "<unknown>", 241)
mid91 = (u"""        (-blocking-println (-finish-string-builder sb))))""", "<unknown>", 242)
mid92 = (u"""  (if (-satisfies? ISeqable t)""", "<unknown>", 256)
mid93 = (u"""    (let [ts (seq t)]""", "<unknown>", 257)
mid94 = (u"""      (if (not ts) false""", "<unknown>", 258)
mid95 = (u"""          (if (-instance? (first ts) x)""", "<unknown>", 259)
mid96 = (u"""            (instance? (rest ts) x))))""", "<unknown>", 261)
mid97 = (u"""    (-instance? t x)))""", "<unknown>", 262)
mid98 = (u"""(deftype Reduced [x]""", "<unknown>", 268)
mid99 = (u"""  (-deref [this] x))""", "<unknown>", 270)
mid100 = (u"""  (->Reduced x))""", "<unknown>", 273)
mid101 = (u"""  (instance? Reduced x))""", "<unknown>", 276)
mid102 = (u"""  (if (-satisfies? ISeqable p)""", "<unknown>", 289)
mid103 = (u"""    (let [ps (seq p)]""", "<unknown>", 290)
mid104 = (u"""      (if (not ps) true""", "<unknown>", 291)
mid105 = (u"""          (if (not (-satisfies? (first ps) x))""", "<unknown>", 292)
mid106 = (u"""            (satisfies? (rest ps) x))))""", "<unknown>", 294)
mid107 = (u"""    (-satisfies? p x)))""", "<unknown>", 295)
mid108 = (u"""   (let [f (xform rf)""", "<unknown>", 306)
mid109 = (u"""         result (-reduce coll f (f))]""", "<unknown>", 307)
mid110 = (u"""     (f result)))""", "<unknown>", 308)
mid111 = (u"""   (let [result (-reduce coll f (f))]""", "<unknown>", 303)
mid112 = (u"""     (f result)))""", "<unknown>", 304)
mid113 = (u"""   (let [f (xform rf)""", "<unknown>", 310)
mid114 = (u"""         result (-reduce coll f init)]""", "<unknown>", 311)
mid115 = (u"""     (f result))))""", "<unknown>", 312)
mid116 = (u"""   (-reduce col rf init)))""", "<unknown>", 318)
mid117 = (u"""   (reduce rf (rf) col))""", "<unknown>", 316)
mid118 = (u"""   (if (satisfies? IToTransient to)""", "<unknown>", 329)
mid119 = (u"""     (transduce xform conj! (transient to) from)""", "<unknown>", 330)
mid120 = (u"""     (transduce xform conj to from))))""", "<unknown>", 331)
mid121 = (u"""   (if (satisfies? IToTransient to)""", "<unknown>", 325)
mid122 = (u"""     (persistent! (reduce conj! (transient to) from))""", "<unknown>", 326)
mid123 = (u"""     (reduce conj to from)))""", "<unknown>", 327)
mid124 = (u"""       ([] (xf))""", "<unknown>", 340)
mid125 = (u"""       ([result] (xf result))""", "<unknown>", 341)
mid126 = (u"""       ([result item] (xf result (f item))))))""", "<unknown>", 342)
mid127 = (u"""   (lazy-seq*""", "<unknown>", 344)
mid128 = (u"""      (let [s (seq coll)]""", "<unknown>", 346)
mid129 = (u"""        (if s""", "<unknown>", 347)
mid130 = (u"""          (cons (f (first s))""", "<unknown>", 348)
mid131 = (u"""                (map f (rest s)))""", "<unknown>", 349)
mid132 = (u"""                (lazy-seq*""", "<unknown>", 353)
mid133 = (u"""                   (let [ss (map seq cs)]""", "<unknown>", 355)
mid134 = (u"""                     (if (every? identity ss)""", "<unknown>", 356)
mid135 = (u"""                       (cons (map first ss) (step (map rest ss)))""", "<unknown>", 357)
mid136 = (u"""     (map (fn [args] (apply f args)) (step colls)))))""", "<unknown>", 359)
mid137 = (u"""   (let [step (fn step [cs]""", "<unknown>", 352)
mid138 = (u"""(deftype Range [start stop step]""", "<unknown>", 367)
mid139 = (u"""  (-reduce [self f init]""", "<unknown>", 369)
mid140 = (u"""           acc init]""", "<unknown>", 371)
mid141 = (u"""    (loop [i start""", "<unknown>", 370)
mid142 = (u"""      (if (or (and (> step 0) (< i stop))""", "<unknown>", 372)
mid143 = (u"""              (and (< step 0) (> i stop))""", "<unknown>", 373)
mid144 = (u"""              (and (= step 0)))""", "<unknown>", 374)
mid145 = (u"""        (let [acc (f acc i)]""", "<unknown>", 375)
mid146 = (u"""          (if (reduced? acc)""", "<unknown>", 376)
mid147 = (u"""            @acc""", "<unknown>", 377)
mid148 = (u"""            (recur (+ i step) acc)))""", "<unknown>", 378)
mid149 = (u"""        acc)))""", "<unknown>", 379)
mid150 = (u"""  (-count [self]""", "<unknown>", 381)
mid151 = (u"""    (if (or (and (< start stop) (< step 0))""", "<unknown>", 382)
mid152 = (u"""            (and (> start stop) (> step 0))""", "<unknown>", 383)
mid153 = (u"""            (= step 0))""", "<unknown>", 384)
mid154 = (u"""      (abs (quot (- start stop) step))))""", "<unknown>", 386)
mid155 = (u"""  (-nth [self idx]""", "<unknown>", 388)
mid156 = (u"""    (when (or (= start stop 0) (neg? idx))""", "<unknown>", 389)
mid157 = (u"""      (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"]))""", "<unknown>", 390)
mid158 = (u"""    (let [cmp (if (< start stop) < >)""", "<unknown>", 391)
mid159 = (u"""          val (+ start (* idx step))]""", "<unknown>", 392)
mid160 = (u"""      (if (cmp val stop)""", "<unknown>", 393)
mid161 = (u"""        val""", "<unknown>", 394)
mid162 = (u"""        (throw [:pixie.stdlib/OutOfRangeException "Index out of Range"]))))""", "<unknown>", 395)
mid163 = (u"""  (-nth-not-found [self idx not-found]""", "<unknown>", 396)
mid164 = (u"""    (let [cmp (if (< start stop) < >)""", "<unknown>", 397)
mid165 = (u"""          val (+ start (* idx step))]""", "<unknown>", 398)
mid166 = (u"""      (if (cmp val stop)""", "<unknown>", 399)
mid167 = (u"""        val""", "<unknown>", 400)
mid168 = (u"""       not-found)))""", "<unknown>", 401)
mid169 = (u"""  (-seq [self]""", "<unknown>", 403)
mid170 = (u"""    (when (or (and (> step 0) (< start stop))""", "<unknown>", 404)
mid171 = (u"""              (and (< step 0) (> start stop)))""", "<unknown>", 405)
mid172 = (u"""      (cons start (lazy-seq* #(range (+ start step) stop step)))))""", "<unknown>", 406)
mid173 = (u"""  (-str [this sbf]""", "<unknown>", 408)
mid174 = (u"""    (-str (seq this) sbf))""", "<unknown>", 409)
mid175 = (u"""  (-repr [this sbf]""", "<unknown>", 410)
mid176 = (u"""    (-repr (seq this) sbf))""", "<unknown>", 411)
mid177 = (u"""  (-eq [this sb]""", "<unknown>", 412)
mid178 = (u"""  ([] (pixie.stdlib.range/->Range 0 MAX-NUMBER 1))""", "<unknown>", 427)
mid179 = (u"""  ([stop] (pixie.stdlib.range/->Range 0 stop 1))""", "<unknown>", 428)
mid180 = (u"""  ([start stop step] (pixie.stdlib.range/->Range start stop step)))""", "<unknown>", 430)
mid181 = (u"""  ([start stop] (pixie.stdlib.range/->Range start stop 1))""", "<unknown>", 429)
mid182 = (u"""(deftype Node [edit array]""", "<unknown>", 436)
mid183 = (u"""  (-get-field [this name]""", "<unknown>", 438)
mid184 = (u"""    (get-field this name)))""", "<unknown>", 439)
mid185 = (u"""   (new-node edit (make-array 32)))""", "<unknown>", 443)
mid186 = (u"""   (->Node edit array)))""", "<unknown>", 445)
mid187 = (u"""(def EMPTY-NODE (new-node nil))""", "<unknown>", 447)
mid188 = (u"""        (analyze-form (keep-meta `(~'pixie.stdlib/-get-field ~@args ~sym-kw)""", "pixie/compiler.pxi", 307)
mid189 = (u"""  (let [cnt (.-cnt this)]""", "<unknown>", 452)
mid190 = (u"""    (if (< cnt 32)""", "<unknown>", 453)
mid191 = (u"""      (bit-shift-left (bit-shift-right (dec cnt) 5) 5))))""", "<unknown>", 455)
mid192 = (u"""  (if (and (<= 0 i) (< i (.-cnt this)))""", "<unknown>", 458)
mid193 = (u"""    (if (>= i (tailoff this))""", "<unknown>", 459)
mid194 = (u"""      (.-tail this)""", "<unknown>", 460)
mid195 = (u"""      (loop [node (.-root this)""", "<unknown>", 461)
mid196 = (u"""             level (.-shift this)]""", "<unknown>", 462)
mid197 = (u"""        (if (> level 0)""", "<unknown>", 463)
mid198 = (u"""          (recur (aget (.-array node)""", "<unknown>", 464)
mid199 = (u"""                       (bit-and (bit-shift-right i level) 0x01f))""", "<unknown>", 465)
mid200 = (u"""                 (- level 5))""", "<unknown>", 466)
mid201 = (u"""          (.-array node))))""", "<unknown>", 467)
mid202 = (u"""    (throw [:pixie.stdlib/IndexOutOfRangeException""", "<unknown>", 468)
mid203 = (u"""(deftype PersistentVector [cnt shift root tail meta]""", "<unknown>", 471)
mid204 = (u"""  (-get-field [this name]""", "<unknown>", 473)
mid205 = (u"""    (get-field this name))""", "<unknown>", 474)
mid206 = (u"""  (-conj [this val]""", "<unknown>", 477)
mid207 = (u"""    (assert (< cnt 0xFFFFFFFF) "Vector too large")""", "<unknown>", 478)
mid208 = (u"""    (if (< (- cnt (tailoff this)) 32)""", "<unknown>", 480)
mid209 = (u"""      (let [new-tail (array-append tail val)]""", "<unknown>", 481)
mid210 = (u"""        (->PersistentVector (inc cnt) shift root new-tail meta))""", "<unknown>", 482)
mid211 = (u"""      (let [tail-node (->Node (.-edit root) tail)]""", "<unknown>", 484)
mid212 = (u"""        (if (> (bit-shift-right cnt 5) (bit-shift-left 1 shift))""", "<unknown>", 485)
mid213 = (u"""          (let [new-root (new-node (.-edit root))""", "<unknown>", 487)
mid214 = (u"""                new-root-arr (.-array new-root)]""", "<unknown>", 488)
mid215 = (u"""            (aset new-root-arr 0 root)""", "<unknown>", 489)
mid216 = (u"""            (aset new-root-arr 1 (new-path (.-edit root) shift tail-node))""", "<unknown>", 490)
mid217 = (u"""            (->PersistentVector (inc cnt)""", "<unknown>", 491)
mid218 = (u"""                                (+ shift 5)""", "<unknown>", 492)
mid219 = (u"""                                new-root""", "<unknown>", 493)
mid220 = (u"""                                (array val)""", "<unknown>", 494)
mid221 = (u"""          (let [new-root (push-tail this shift root tail-node)]""", "<unknown>", 496)
mid222 = (u"""            (->PersistentVector (inc cnt)""", "<unknown>", 497)
mid223 = (u"""                                new-root""", "<unknown>", 499)
mid224 = (u"""                                (array val)""", "<unknown>", 500)
mid225 = (u"""  (-nth [self i]""", "<unknown>", 503)
mid226 = (u"""    (if (and (<= 0 i)""", "<unknown>", 504)
mid227 = (u"""             (< i cnt))""", "<unknown>", 505)
mid228 = (u"""      (let [node (array-for self i)]""", "<unknown>", 506)
mid229 = (u"""        (aget node (bit-and i 0x01F)))""", "<unknown>", 507)
mid230 = (u"""      (throw [:pixie.stdlib/IndexOutOfRange""", "<unknown>", 508)
mid231 = (u"""              (str "Index out of range, got " i " only have " cnt)])))""", "<unknown>", 509)
mid232 = (u"""  (-nth-not-found [self i not-found]""", "<unknown>", 511)
mid233 = (u"""    (if (and (<= 0 i)""", "<unknown>", 512)
mid234 = (u"""             (< i cnt))""", "<unknown>", 513)
mid235 = (u"""      (let [node (array-for self i)]""", "<unknown>", 514)
mid236 = (u"""        (aget node (bit-and i 0x01F)))""", "<unknown>", 515)
mid237 = (u"""      not-found))""", "<unknown>", 516)
mid238 = (u"""  (-get [this val]""", "<unknown>", 521)
mid239 = (u"""    (-nth-not-found self val nil))""", "<unknown>", 522)
mid240 = (u"""  (-count [this] cnt)""", "<unknown>", 526)
mid241 = (u"""  (-pop [this]""", "<unknown>", 529)
mid242 = (u"""    (assert (!= cnt) "Can't pop an empty vector")""", "<unknown>", 530)
mid243 = (u"""    (if (== cnt 1)""", "<unknown>", 532)
mid244 = (u"""      EMPTY""", "<unknown>", 533)
mid245 = (u"""      (if (> (- cnt (tailoff this)) 1)""", "<unknown>", 534)
mid246 = (u"""        (let [size (dec (count tail))""", "<unknown>", 535)
mid247 = (u"""              new-tail (array-resize size)]""", "<unknown>", 536)
mid248 = (u"""          (->PersistentVector (dec cnt)""", "<unknown>", 537)
mid249 = (u"""                              new-tail""", "<unknown>", 540)
mid250 = (u"""        (let [new-tail (array-for this (- cnt 2))""", "<unknown>", 542)
mid251 = (u"""              new-root (pop-tail shift root)]""", "<unknown>", 543)
mid252 = (u"""            (nil? new-root)""", "<unknown>", 545)
mid253 = (u"""            (->PersisentVector (dec cnt)""", "<unknown>", 546)
mid254 = (u"""                               EMPTY-NODE""", "<unknown>", 548)
mid255 = (u"""                               new-tail""", "<unknown>", 549)
mid256 = (u"""            (and (> shift 5)""", "<unknown>", 551)
mid257 = (u"""                 (nil? (aget (.-array new-root) 1)))""", "<unknown>", 552)
mid258 = (u"""            (->PersistentVector (dec cnt)""", "<unknown>", 553)
mid259 = (u"""                                (- shift 5)""", "<unknown>", 554)
mid260 = (u"""                                (aget (.-array new-root) 0)""", "<unknown>", 555)
mid261 = (u"""                                new-tail""", "<unknown>", 556)
mid262 = (u"""            (->PersistentVector (dec cnt)""", "<unknown>", 560)
mid263 = (u"""                                new-root""", "<unknown>", 562)
mid264 = (u"""                                new-tail""", "<unknown>", 563)
mid265 = (u"""          (cond""", "<unknown>", 544)
mid266 = (u"""  (let [subidx (bit-and (bit-shift-right (dec (.-cnt this)) level) 0x01f)""", "<unknown>", 568)
mid267 = (u"""        ret-array (array-clone (.-array parent))""", "<unknown>", 569)
mid268 = (u"""        node-to-insert (if (= level 5)""", "<unknown>", 570)
mid269 = (u"""                         tail-node""", "<unknown>", 571)
mid270 = (u"""                         (let [child (aget (.-array parent) subidx)]""", "<unknown>", 572)
mid271 = (u"""                           (if (= child nil)""", "<unknown>", 573)
mid272 = (u"""                             (new-path (.-edit (.-root this))""", "<unknown>", 574)
mid273 = (u"""                                       (- level 5)""", "<unknown>", 575)
mid274 = (u"""                                       tail-node)""", "<unknown>", 576)
mid275 = (u"""                             (push-tail this""", "<unknown>", 577)
mid276 = (u"""                                        (- level 5)""", "<unknown>", 578)
mid277 = (u"""                                        child""", "<unknown>", 579)
mid278 = (u"""                                        tail-node))))]""", "<unknown>", 580)
mid279 = (u"""    (aset ret-array subidx node-to-insert)""", "<unknown>", 581)
mid280 = (u"""    (->Node (.-edit parent) ret-array)))""", "<unknown>", 582)
mid281 = (u"""  (let [sub-idx (bit-and (bit-shift-right (dec (.-cnt)) level) 0x01F)]""", "<unknown>", 585)
mid282 = (u"""      (> level 5)""", "<unknown>", 587)
mid283 = (u"""      (let [new-child (pop-tail (- level 5)""", "<unknown>", 588)
mid284 = (u"""                                (aget (.-array node) sub-idx))]""", "<unknown>", 589)
mid285 = (u"""        (if (or (nil? new-child)""", "<unknown>", 590)
mid286 = (u"""                (= sub-idx 0))""", "<unknown>", 591)
mid287 = (u"""          (let [root (.-root this)""", "<unknown>", 593)
mid288 = (u"""                ret (->Node (.-edit root)""", "<unknown>", 594)
mid289 = (u"""                            (.-array node))]""", "<unknown>", 595)
mid290 = (u"""            (aset (.-array ret) sub-idx new-child)""", "<unknown>", 596)
mid291 = (u"""            ret)))""", "<unknown>", 597)
mid292 = (u"""      (= sub-idx 0)""", "<unknown>", 599)
mid293 = (u"""      (let [root (.-root this)""", "<unknown>", 603)
mid294 = (u"""            ret (->Node (.-edit root)""", "<unknown>", 604)
mid295 = (u"""                        (aclone (.-array node)))]""", "<unknown>", 605)
mid296 = (u"""        (aset (.-array ret) nil)""", "<unknown>", 606)
mid297 = (u"""        ret))))""", "<unknown>", 607)
mid298 = (u"""    (cond""", "<unknown>", 586)
mid299 = (u"""  (if (= level 0)""", "<unknown>", 610)
mid300 = (u"""    node""", "<unknown>", 611)
mid301 = (u"""    (let [nnode (new-node edit)]""", "<unknown>", 612)
mid302 = (u"""      (aset (.-array nnode) 0 (new-path edit (- level 5) node))""", "<unknown>", 613)
mid303 = (u"""      nnode)))""", "<unknown>", 614)
mid304 = (u"""(def EMPTY (->PersistentVector 0 5 EMPTY-NODE (array 0) nil))""", "<unknown>", 617)
mid305 = (u"""  (if (< (count arr) 32)""", "<unknown>", 620)
mid306 = (u"""    (->PersistentVector (count arr) 5 EMPTY-NODE arr nil)""", "<unknown>", 621)
mid307 = (u"""    (into [] arr)))""", "<unknown>", 622)
mid308 = (u"""  (-reduce [this f init]""", "<unknown>", 636)
mid309 = (u"""(extend-type Array""", "<unknown>", 626)
mid310 = (u"""           acc init]""", "<unknown>", 638)
mid311 = (u"""    (loop [idx 0""", "<unknown>", 637)
mid312 = (u"""      (if (reduced? acc)""", "<unknown>", 639)
mid313 = (u"""        @acc""", "<unknown>", 640)
mid314 = (u"""        (if (< idx (count this))""", "<unknown>", 641)
mid315 = (u"""          (recur (inc idx)""", "<unknown>", 642)
mid316 = (u"""                 (f acc (aget this idx)))""", "<unknown>", 643)
mid317 = (u"""          acc)))))""", "<unknown>", 644)
mid318 = (u"""  (-count ([arr]""", "<unknown>", 632)
mid319 = (u"""           (.-count arr)))""", "<unknown>", 633)
mid320 = (u"""  (-conj [arr itm]""", "<unknown>", 628)
mid321 = (u"""    (conj (vector-from-array arr) itm))""", "<unknown>", 629)
mid322 = (u"""  (loop [idx 0]""", "<unknown>", 647)
mid323 = (u"""    (when (< idx size)""", "<unknown>", 648)
mid324 = (u"""      (do (aset to (+ to-idx idx) (aget from (+ from-idx idx)))""", "<unknown>", 649)
mid325 = (u"""          (recur (inc idx))))))""", "<unknown>", 650)
mid326 = (u"""  (let [new-array (make-array (inc (count arr)))]""", "<unknown>", 653)
mid327 = (u"""    (array-copy arr 0 new-array 0 (count arr))""", "<unknown>", 654)
mid328 = (u"""    (aset new-array (count arr) val)""", "<unknown>", 655)
mid329 = (u"""    new-array))""", "<unknown>", 656)
mid330 = (u"""  (let [new-array (make-array (count arr))]""", "<unknown>", 659)
mid331 = (u"""    (array-copy arr 0 new-array 0 (count arr))""", "<unknown>", 660)
mid332 = (u"""    new-array))""", "<unknown>", 661)
mid333 = (u"""      v (into [] (range MAX))]""", "<unknown>", 666)
mid334 = (u"""  (dotimes [x MAX]""", "<unknown>", 667)
mid335 = (u"""    (println x)""", "<unknown>", 668)
mid336 = (u"""    (assert (= x (nth v x)))))""", "<unknown>", 669)
mid337 = (u"""(let [MAX 1024""", "<unknown>", 665)
mid338 = (u"""(do ;; This file is used to build what we need to even start running stdlib.pxi""", "<unknown>", 1)

 
code_ast=i.Do(
  args=[
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/ISeq)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"ISeq")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"ISeq")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-first)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-first")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-first")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ISeq"), meta=i.Meta(mid2, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-next)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-next")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-next")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ISeq"), meta=i.Meta(mid2, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid2, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/ISeqable)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"ISeqable")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"ISeqable")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-seq)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-seq")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-seq")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ISeqable"), meta=i.Meta(mid3, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid3, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/ICounted)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"ICounted")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"ICounted")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-count)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-count")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-count")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ICounted"), meta=i.Meta(mid4, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid4, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IIndexed)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IIndexed")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IIndexed")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-nth)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-nth")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-nth")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IIndexed"), meta=i.Meta(mid5, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-nth-not-found)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-nth-not-found")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-nth-not-found")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IIndexed"), meta=i.Meta(mid5, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid5, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IPersistentCollection)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IPersistentCollection")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IPersistentCollection")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-conj)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-conj")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-conj")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IPersistentCollection"), meta=i.Meta(mid6, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-disj)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-disj")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-disj")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IPersistentCollection"), meta=i.Meta(mid6, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid6, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IEmpty)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IEmpty")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IEmpty")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-empty)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-empty")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-empty")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IEmpty"), meta=i.Meta(mid7, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid7, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IObject)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IObject")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IObject")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-hash)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-hash")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-hash")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IObject"), meta=i.Meta(mid8, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-eq)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-eq")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-eq")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IObject"), meta=i.Meta(mid8, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-str)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-str")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-str")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IObject"), meta=i.Meta(mid8, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-repr)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-repr")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-repr")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IObject"), meta=i.Meta(mid8, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid8, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IReduce)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IReduce")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IReduce")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-reduce)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-reduce")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-reduce")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IReduce"), meta=i.Meta(mid9, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid9, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IDeref)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IDeref")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IDeref")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-deref)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-deref")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-deref")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IDeref"), meta=i.Meta(mid10, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid10, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IReset)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IReset")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IReset")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-reset!)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-reset!")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-reset!")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IReset"), meta=i.Meta(mid11, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid11, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/INamed)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"INamed")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"INamed")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-namespace)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-namespace")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-namespace")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"INamed"), meta=i.Meta(mid12, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-name)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-name")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-name")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"INamed"), meta=i.Meta(mid12, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid12, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IAssociative)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IAssociative")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IAssociative")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-assoc)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-assoc")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-assoc")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IAssociative"), meta=i.Meta(mid13, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-contains-key)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-contains-key")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-contains-key")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IAssociative"), meta=i.Meta(mid13, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-dissoc)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-dissoc")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-dissoc")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IAssociative"), meta=i.Meta(mid13, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid13, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/ILookup)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"ILookup")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"ILookup")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-get)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-get")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-get")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ILookup"), meta=i.Meta(mid14, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid14, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IMapEntry)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IMapEntry")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IMapEntry")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-key)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-key")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-key")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IMapEntry"), meta=i.Meta(mid15, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-val)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-val")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-val")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IMapEntry"), meta=i.Meta(mid15, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid15, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IStack)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IStack")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IStack")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-push)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-push")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-push")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IStack"), meta=i.Meta(mid16, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid16, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IPop)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IPop")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IPop")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-pop)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-pop")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-pop")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IPop"), meta=i.Meta(mid17, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid17, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IFn)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IFn")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IFn")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-invoke)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-invoke")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-invoke")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IFn"), meta=i.Meta(mid18, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid18, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IDoc)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IDoc")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IDoc")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-doc)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-doc")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-doc")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IDoc"), meta=i.Meta(mid19, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid19, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/IVector)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"IVector")),
      i.Invoke(
        args=[
          i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
          i.Const(rt.wrap(u"IVector")),
        ],
        meta=nil)]),
    i.Invoke(args=[
# (def pixie.stdlib/ISequential)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"ISequential")),
      i.Invoke(
        args=[
          i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
          i.Const(rt.wrap(u"ISequential")),
        ],
        meta=nil)]),
    i.Invoke(args=[
# (def pixie.stdlib/IMap)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"IMap")),
      i.Invoke(
        args=[
          i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
          i.Const(rt.wrap(u"IMap")),
        ],
        meta=nil)]),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IMeta)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IMeta")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IMeta")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-with-meta)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-with-meta")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-with-meta")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IMeta"), meta=i.Meta(mid20, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-meta)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-meta")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-meta")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IMeta"), meta=i.Meta(mid20, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid20, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/ITransientCollection)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"ITransientCollection")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"ITransientCollection")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-conj!)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-conj!")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-conj!")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ITransientCollection"), meta=i.Meta(mid21, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid21, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IToTransient)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IToTransient")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IToTransient")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-transient)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-transient")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-transient")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IToTransient"), meta=i.Meta(mid22, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid22, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/ITransientStack)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"ITransientStack")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"ITransientStack")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-push!)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-push!")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-push!")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ITransientStack"), meta=i.Meta(mid23, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-pop!)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-pop!")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-pop!")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ITransientStack"), meta=i.Meta(mid23, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid23, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IDisposable)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IDisposable")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IDisposable")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-dispose!)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-dispose!")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-dispose!")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IDisposable"), meta=i.Meta(mid24, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid24, 1)),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/IMessageObject)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"IMessageObject")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"protocol"), meta=i.Meta(mid0, 22)),
              i.Const(rt.wrap(u"IMessageObject")),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-get-field)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-get-field")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-get-field")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IMessageObject"), meta=i.Meta(mid25, 14)),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/-invoke-method)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"-invoke-method")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"polymorphic-fn"), meta=i.Meta(mid1, 31)),
              i.Const(rt.wrap(u"-invoke-method")),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"IMessageObject"), meta=i.Meta(mid25, 14)),
            ],
            meta=nil)]),
      ],
    meta=i.Meta(mid25, 1)),
    i.Invoke(
      args=[
        i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=i.Meta(mid26, 2)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid26, 9)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"Object"), meta=i.Meta(mid26, 20)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"-internal-get-field"), meta=i.Meta(mid26, 27)),
      ],
      meta=i.Meta(mid26, 1)),
    i.Do(
      args=[
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-eq"), meta=i.Meta(mid27, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Object"), meta=i.Meta(mid28, 14)),
            i.Fn(args=[kw(u"this"),kw(u"other")],name=kw(u"fn_360"),
              body=i.Const(false),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-repr"), meta=i.Meta(mid29, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Object"), meta=i.Meta(mid28, 14)),
            i.Fn(args=[kw(u"x"),kw(u"sb")],name=kw(u"fn_363"),
              body=i.TailCall(
                args=[
                  i.Lookup(kw(u"sb"), meta=i.Meta(mid30, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-internal-to-repr"), meta=i.Meta(mid30, 10)),
                      i.Lookup(kw(u"x"), meta=i.Meta(mid30, 28)),
                    ],
                    meta=i.Meta(mid30, 9)),
                ],
                meta=i.Meta(mid30, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid31, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Object"), meta=i.Meta(mid28, 14)),
            i.Fn(args=[kw(u"x"),kw(u"sb")],name=kw(u"fn_357"),
              body=i.TailCall(
                args=[
                  i.Lookup(kw(u"sb"), meta=i.Meta(mid32, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-internal-to-str"), meta=i.Meta(mid32, 10)),
                      i.Lookup(kw(u"x"), meta=i.Meta(mid32, 27)),
                    ],
                    meta=i.Meta(mid32, 9)),
                ],
                meta=i.Meta(mid32, 5)),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid28, 1)),
    i.Invoke(
      args=[
        i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid33, 4)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"String"), meta=i.Meta(mid34, 14)),
        i.Fn(args=[kw(u"this"),kw(u"sb")],name=kw(u"fn_366"),
          body=i.TailCall(
            args=[
              i.Lookup(kw(u"sb"), meta=i.Meta(mid35, 6)),
              i.Lookup(kw(u"this"), meta=i.Meta(mid35, 9)),
            ],
            meta=i.Meta(mid35, 5)),
        ),
      ],
      meta=nil),
    i.Invoke(
      args=[
        i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=i.Meta(mid36, 2)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"-eq"), meta=i.Meta(mid36, 9)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"Number"), meta=i.Meta(mid36, 13)),
        i.VDeref(code.intern_var(u"pixie.stdlib", u"-num-eq"), meta=i.Meta(mid36, 20)),
      ],
      meta=i.Meta(mid36, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/+)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"+")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"+")),
              i.Const(rt.wrap(0)), i.Fn(args=[],name=kw(u"+"),
          body=i.Const(rt.wrap(0)),
        ),
        i.Const(rt.wrap(1)), i.Fn(args=[kw(u"x")],name=kw(u"+"),
          body=i.Lookup(kw(u"x"), meta=i.Meta(mid37, 8)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u"+"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-add"), meta=i.Meta(mid38, 11)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid38, 16)),
              i.Lookup(kw(u"y"), meta=i.Meta(mid38, 18)),
            ],
            meta=i.Meta(mid38, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"more")],name=kw(u"+"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-apply"), meta=i.Meta(mid39, 5)),
              i.Lookup(kw(u"+"), meta=i.Meta(mid39, 12)),
              i.Invoke(
                args=[
                  i.Lookup(kw(u"+"), meta=i.Meta(mid39, 15)),
                  i.Lookup(kw(u"x"), meta=i.Meta(mid39, 17)),
                  i.Lookup(kw(u"y"), meta=i.Meta(mid39, 19)),
                ],
                meta=i.Meta(mid39, 14)),
              i.Lookup(kw(u"more"), meta=i.Meta(mid39, 22)),
            ],
            meta=i.Meta(mid39, 4)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/-)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"-")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"-")),
              i.Const(rt.wrap(0)), i.Fn(args=[],name=kw(u"-"),
          body=i.Const(rt.wrap(0)),
        ),
        i.Const(rt.wrap(1)), i.Fn(args=[kw(u"x")],name=kw(u"-"),
          body=i.Lookup(kw(u"x"), meta=i.Meta(mid40, 8)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u"-"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-sub"), meta=i.Meta(mid41, 11)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid41, 16)),
              i.Lookup(kw(u"y"), meta=i.Meta(mid41, 18)),
            ],
            meta=i.Meta(mid41, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"more")],name=kw(u"-"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-apply"), meta=i.Meta(mid42, 5)),
              i.Lookup(kw(u"-"), meta=i.Meta(mid42, 12)),
              i.Invoke(
                args=[
                  i.Lookup(kw(u"-"), meta=i.Meta(mid42, 15)),
                  i.Lookup(kw(u"x"), meta=i.Meta(mid42, 17)),
                  i.Lookup(kw(u"y"), meta=i.Meta(mid42, 19)),
                ],
                meta=i.Meta(mid42, 14)),
              i.Lookup(kw(u"more"), meta=i.Meta(mid42, 22)),
            ],
            meta=i.Meta(mid42, 4)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/inc)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"inc")),
      i.Fn(args=[kw(u"x")],name=kw(u"inc"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid43, 9)),
            i.Lookup(kw(u"x"), meta=i.Meta(mid43, 11)),
            i.Const(rt.wrap(1)),
          ],
          meta=i.Meta(mid43, 8)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/dec)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"dec")),
      i.Fn(args=[kw(u"x")],name=kw(u"dec"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid44, 9)),
            i.Lookup(kw(u"x"), meta=i.Meta(mid44, 11)),
            i.Const(rt.wrap(1)),
          ],
          meta=i.Meta(mid44, 8)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/<)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"<")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"<")),
              i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u"<"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-lt"), meta=i.Meta(mid45, 11)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid45, 15)),
              i.Lookup(kw(u"y"), meta=i.Meta(mid45, 17)),
            ],
            meta=i.Meta(mid45, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"more")],name=kw(u"<"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-apply"), meta=i.Meta(mid46, 5)),
              i.Lookup(kw(u"<"), meta=i.Meta(mid46, 12)),
              i.Invoke(
                args=[
                  i.Lookup(kw(u"<"), meta=i.Meta(mid46, 15)),
                  i.Lookup(kw(u"x"), meta=i.Meta(mid46, 17)),
                  i.Lookup(kw(u"y"), meta=i.Meta(mid46, 19)),
                ],
                meta=i.Meta(mid46, 14)),
              i.Lookup(kw(u"more"), meta=i.Meta(mid46, 22)),
            ],
            meta=i.Meta(mid46, 4)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/>)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u">")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u">")),
              i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u">"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-gt"), meta=i.Meta(mid47, 11)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid47, 15)),
              i.Lookup(kw(u"y"), meta=i.Meta(mid47, 17)),
            ],
            meta=i.Meta(mid47, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"more")],name=kw(u">"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-apply"), meta=i.Meta(mid48, 5)),
              i.Lookup(kw(u">"), meta=i.Meta(mid48, 12)),
              i.Invoke(
                args=[
                  i.Lookup(kw(u">"), meta=i.Meta(mid48, 15)),
                  i.Lookup(kw(u"x"), meta=i.Meta(mid48, 17)),
                  i.Lookup(kw(u"y"), meta=i.Meta(mid48, 19)),
                ],
                meta=i.Meta(mid48, 14)),
              i.Lookup(kw(u"more"), meta=i.Meta(mid48, 22)),
            ],
            meta=i.Meta(mid48, 4)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/<=)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"<=")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"<=")),
              i.Const(rt.wrap(1)), i.Fn(args=[kw(u"x")],name=kw(u"<="),
          body=i.Const(true),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u"<="),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-lte"), meta=i.Meta(mid49, 11)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid49, 16)),
              i.Lookup(kw(u"y"), meta=i.Meta(mid49, 18)),
            ],
            meta=i.Meta(mid49, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"rest")],name=kw(u"<="),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-lte"), meta=i.Meta(mid50, 22)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid50, 27)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid50, 29)),
              ],
              meta=i.Meta(mid50, 21)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"apply"), meta=i.Meta(mid51, 20)),
                i.Lookup(kw(u"<="), meta=i.Meta(mid51, 26)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid51, 29)),
                i.Lookup(kw(u"rest"), meta=i.Meta(mid51, 31)),
              ],
              meta=i.Meta(mid51, 19)),
            els=i.Const(nil),
            meta=i.Meta(mid50, 17)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/>=)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u">=")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u">=")),
              i.Const(rt.wrap(1)), i.Fn(args=[kw(u"x")],name=kw(u">="),
          body=i.Const(true),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u">="),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-gte"), meta=i.Meta(mid52, 11)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid52, 16)),
              i.Lookup(kw(u"y"), meta=i.Meta(mid52, 18)),
            ],
            meta=i.Meta(mid52, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"rest")],name=kw(u">="),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-gte"), meta=i.Meta(mid53, 22)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid53, 27)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid53, 29)),
              ],
              meta=i.Meta(mid53, 21)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"apply"), meta=i.Meta(mid54, 20)),
                i.Lookup(kw(u">="), meta=i.Meta(mid54, 26)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid54, 29)),
                i.Lookup(kw(u"rest"), meta=i.Meta(mid54, 31)),
              ],
              meta=i.Meta(mid54, 19)),
            els=i.Const(nil),
            meta=i.Meta(mid53, 17)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/=)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"=")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"=")),
              i.Const(rt.wrap(1)), i.Fn(args=[kw(u"x")],name=kw(u"="),
          body=i.Const(true),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"x"),kw(u"y")],name=kw(u"="),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"identical?"), meta=i.Meta(mid55, 15)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid55, 26)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid55, 28)),
              ],
              meta=i.Meta(mid55, 14)),
            then=i.Const(true),
            els=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-eq"), meta=i.Meta(mid56, 13)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid56, 17)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid56, 19)),
              ],
              meta=i.Meta(mid56, 12)),
            meta=i.Meta(mid55, 10)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"x"),kw(u"y"),kw(u"rest")],name=kw(u"="),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"eq"), meta=i.Meta(mid57, 22)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid57, 25)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid57, 27)),
              ],
              meta=i.Meta(mid57, 21)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"apply"), meta=i.Meta(mid58, 20)),
                i.Lookup(kw(u"="), meta=i.Meta(mid58, 26)),
                i.Lookup(kw(u"y"), meta=i.Meta(mid58, 28)),
                i.Lookup(kw(u"rest"), meta=i.Meta(mid58, 30)),
              ],
              meta=i.Meta(mid58, 19)),
            els=i.Const(nil),
            meta=i.Meta(mid57, 17)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/conj)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"conj")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"conj")),
              i.Const(rt.wrap(0)), i.Fn(args=[],name=kw(u"conj"),
          body=i.Invoke(args=[
            i.Const(code.intern_var(u"pixie.stdlib", u"array")),            ]),
        ),
        i.Const(rt.wrap(1)), i.Fn(args=[kw(u"coll")],name=kw(u"conj"),
          body=i.Lookup(kw(u"coll"), meta=i.Meta(mid59, 11)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"coll"),kw(u"itm")],name=kw(u"conj"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-conj"), meta=i.Meta(mid60, 16)),
              i.Lookup(kw(u"coll"), meta=i.Meta(mid60, 22)),
              i.Lookup(kw(u"itm"), meta=i.Meta(mid60, 27)),
            ],
            meta=i.Meta(mid60, 15)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(2)), 
        i.Fn(args=[kw(u"coll"),kw(u"item"),kw(u"more")],name=kw(u"conj"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-apply"), meta=i.Meta(mid61, 5)),
              i.Lookup(kw(u"conj"), meta=i.Meta(mid61, 12)),
              i.Invoke(
                args=[
                  i.Lookup(kw(u"conj"), meta=i.Meta(mid61, 18)),
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"x"), meta=i.Meta(mid61, 23)),
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"y"), meta=i.Meta(mid61, 25)),
                ],
                meta=i.Meta(mid61, 17)),
              i.Lookup(kw(u"more"), meta=i.Meta(mid61, 28)),
            ],
            meta=i.Meta(mid61, 4)),
        )])
      ])]),
    i.Invoke(args=[
# (def pixie.stdlib/nth)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"nth")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"nth")),
              i.Const(rt.wrap(3)), i.Fn(args=[kw(u"coll"),kw(u"idx"),kw(u"not-found")],name=kw(u"nth"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth-not-found"), meta=i.Meta(mid62, 26)),
              i.Lookup(kw(u"coll"), meta=i.Meta(mid62, 41)),
              i.Lookup(kw(u"idx"), meta=i.Meta(mid62, 46)),
              i.Lookup(kw(u"not-found"), meta=i.Meta(mid62, 50)),
            ],
            meta=i.Meta(mid62, 25)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"coll"),kw(u"idx")],name=kw(u"nth"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth"), meta=i.Meta(mid63, 16)),
              i.Lookup(kw(u"coll"), meta=i.Meta(mid63, 21)),
              i.Lookup(kw(u"idx"), meta=i.Meta(mid63, 26)),
            ],
            meta=i.Meta(mid63, 15)),
        ),
              ])]),
    i.Invoke(args=[
# (def pixie.stdlib/count)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"count")),
      i.Fn(args=[kw(u"coll")],name=kw(u"count"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-count"), meta=i.Meta(mid64, 12)),
            i.Lookup(kw(u"coll"), meta=i.Meta(mid64, 19)),
          ],
          meta=i.Meta(mid64, 11)),
      )]),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/Cons)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"Cons")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"create-type"), meta=nil),
              i.Const(kw(u"pixie.stdlib.Cons")),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                i.Const(kw(u"first")),
                i.Const(kw(u"next")),
                i.Const(kw(u"meta")),
                ]),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/->Cons)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"->Cons")),
          i.Fn(args=[kw(u"first"),kw(u"next"),kw(u"meta")],name=kw(u"->Cons"),
            body=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"new"), meta=nil),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"Cons"), meta=i.Meta(mid65, 10)),
                i.Lookup(kw(u"first"), meta=nil),
                i.Lookup(kw(u"next"), meta=nil),
                i.Lookup(kw(u"meta"), meta=nil),
              ],
              meta=nil),
          )]),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-first"), meta=i.Meta(mid66, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Cons"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-first_Cons"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid66, 12)),
                  i.Const(kw(u"first")),
                ],
                meta=nil),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-next"), meta=i.Meta(mid67, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Cons"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-next_Cons"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid67, 11)),
                  i.Const(kw(u"next")),
                ],
                meta=nil),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-seq"), meta=i.Meta(mid68, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Cons"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-seq_Cons"),
              body=i.Lookup(kw(u"this"), meta=i.Meta(mid68, 16)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-meta"), meta=i.Meta(mid69, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Cons"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-meta_Cons"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid69, 11)),
                  i.Const(kw(u"meta")),
                ],
                meta=nil),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-with-meta"), meta=i.Meta(mid70, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Cons"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"new-meta")],name=kw(u"-with-meta_Cons"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"->Cons"), meta=i.Meta(mid71, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                      i.Lookup(kw(u"this"), meta=i.Meta(mid70, 16)),
                      i.Const(kw(u"first")),
                    ],
                    meta=nil),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                      i.Lookup(kw(u"this"), meta=i.Meta(mid70, 16)),
                      i.Const(kw(u"next")),
                    ],
                    meta=nil),
                  i.Lookup(kw(u"new-meta"), meta=i.Meta(mid71, 24)),
                ],
                meta=i.Meta(mid71, 5)),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid65, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/cons)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"cons")),
      i.Fn(args=[kw(u"head"),kw(u"tail")],name=kw(u"cons"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"->Cons"), meta=i.Meta(mid72, 4)),
            i.Lookup(kw(u"head"), meta=i.Meta(mid72, 11)),
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid72, 17)),
                i.Lookup(kw(u"tail"), meta=i.Meta(mid72, 21)),
              ],
              meta=i.Meta(mid72, 16)),
            i.Const(nil),
          ],
          meta=i.Meta(mid72, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/string-builder)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"string-builder")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"string-builder")),
              i.Const(rt.wrap(0)), i.Fn(args=[],name=kw(u"string-builder"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-string-builder"), meta=i.Meta(mid73, 8)),
            ],
            meta=i.Meta(mid73, 7)),
        ),
        i.Const(rt.wrap(1)), i.Fn(args=[kw(u"sb")],name=kw(u"string-builder"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid74, 10)),
              i.Lookup(kw(u"sb"), meta=i.Meta(mid74, 15)),
            ],
            meta=i.Meta(mid74, 9)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"sb"),kw(u"x")],name=kw(u"string-builder"),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"instance?"), meta=i.Meta(mid75, 9)),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"String"), meta=i.Meta(mid75, 19)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid75, 26)),
              ],
              meta=i.Meta(mid75, 8)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-add-to-string-builder"), meta=i.Meta(mid76, 7)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid76, 30)),
              ],
              meta=i.Meta(mid76, 6)),
            els=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-add-to-string-bulder"), meta=i.Meta(mid77, 7)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid77, 30)),
                    i.Lookup(kw(u"x"), meta=i.Meta(mid77, 35)),
                  ],
                  meta=i.Meta(mid77, 29)),
              ],
              meta=i.Meta(mid77, 6)),
            meta=i.Meta(mid75, 4)),
        ),
              ])]),
    i.Invoke(args=[
# (def pixie.stdlib/str)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"str")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(0)), 
      i.Fn(args=[kw(u"args")],name=kw(u"str"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"transduce"), meta=i.Meta(mid78, 4)),
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"map"), meta=i.Meta(mid79, 5)),
                i.Lookup(kw(u"str"), meta=i.Meta(mid79, 9)),
              ],
              meta=i.Meta(mid79, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"string-builder"), meta=i.Meta(mid80, 4)),
            i.Lookup(kw(u"args"), meta=i.Meta(mid81, 4)),
          ],
          meta=i.Meta(mid78, 3)),
      )])]),
    i.Invoke(args=[
# (def pixie.stdlib/println)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"println")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(0)), 
      i.Fn(args=[kw(u"args")],name=kw(u"println"),closed_overs=[kw(u"add-fn"),kw(u"sb")],
        body=i.Let(names=[kw(u"sb"),kw(u"add-fn")],
        bindings=[
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-string-builder"), meta=i.Meta(mid82, 13)),
            ],
            meta=i.Meta(mid82, 12)),
          i.Fn(args=[kw(u"x")],name=kw(u"fn_439"),closed_overs=[kw(u"sb")],
            body=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-add-to-string-builder"), meta=i.Meta(mid83, 19)),
                i.Lookup(kw(u"sb"), meta=i.Meta(mid83, 42)),
                i.Lookup(kw(u"x"), meta=i.Meta(mid83, 45)),
              ],
              meta=i.Meta(mid83, 18)),
          ),
          ],
          body=i.Do(
            args=[
              i.Let(names=[kw(u"idx"),kw(u"sb")],
              bindings=[
                i.Const(rt.wrap(0)),
                i.Lookup(kw(u"sb"), meta=i.Meta(mid84, 15)),
                ],
                body=i.Invoke(
                  args=[
                    i.Fn(args=[kw(u"idx"),kw(u"sb")],name=kw(u"pixie.compiler/__loop__fn__"),closed_overs=[kw(u"args"),kw(u"add-fn")],
                      body=i.Let(names=[kw(u"idx"),kw(u"sb")],
                      bindings=[
                        i.Lookup(kw(u"idx"), meta=i.Meta(mid85, 12)),
                        i.Lookup(kw(u"sb"), meta=i.Meta(mid84, 12)),
                        ],
                        body=i.If(
                          test=i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid86, 12)),
                              i.Lookup(kw(u"idx"), meta=i.Meta(mid86, 14)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid86, 19)),
                                  i.Lookup(kw(u"args"), meta=i.Meta(mid86, 25)),
                                ],
                                meta=i.Meta(mid86, 18)),
                            ],
                            meta=i.Meta(mid86, 11)),
                          then=i.TailCall(
                            args=[
                              i.Lookup(kw(u"pixie.compiler/__loop__fn__"), meta=nil),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid87, 17)),
                                  i.Lookup(kw(u"idx"), meta=i.Meta(mid87, 21)),
                                ],
                                meta=i.Meta(mid87, 16)),
                              i.Do(
                                args=[
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid88, 21)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid88, 27)),
                                          i.Lookup(kw(u"args"), meta=i.Meta(mid88, 32)),
                                          i.Lookup(kw(u"idx"), meta=i.Meta(mid88, 37)),
                                        ],
                                        meta=i.Meta(mid88, 26)),
                                      i.Lookup(kw(u"add-fn"), meta=i.Meta(mid88, 42)),
                                    ],
                                    meta=i.Meta(mid88, 20)),
                                  i.Invoke(
                                    args=[
                                      i.Lookup(kw(u"add-fn"), meta=i.Meta(mid89, 21)),
                                      i.Const(rt.wrap(u" ")),
                                    ],
                                    meta=i.Meta(mid89, 20)),
                                  i.Lookup(kw(u"sb"), meta=i.Meta(mid90, 18)),
                                ],
                              meta=i.Meta(mid88, 16)),
                            ],
                            meta=nil),
                          els=i.TailCall(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-blocking-println"), meta=i.Meta(mid91, 10)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-finish-string-builder"), meta=i.Meta(mid91, 29)),
                                  i.Lookup(kw(u"sb"), meta=i.Meta(mid91, 52)),
                                ],
                                meta=i.Meta(mid91, 28)),
                            ],
                            meta=i.Meta(mid91, 9)),
                          meta=i.Meta(mid86, 7)),
                        meta=nil),
                    ),
                    i.Lookup(kw(u"idx"), meta=i.Meta(mid85, 12)),
                    i.Lookup(kw(u"sb"), meta=i.Meta(mid84, 12)),
                  ],
                  meta=nil),
                meta=i.Meta(mid85, 5)),
              i.Const(nil),
            ],
          meta=nil),
          meta=i.Meta(mid82, 3)),
      )])]),
    i.Invoke(args=[
# (def pixie.stdlib/instance?)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"instance?")),
      i.Fn(args=[kw(u"t"),kw(u"x")],name=kw(u"instance?"),
        body=i.If(
          test=i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-satisfies?"), meta=i.Meta(mid92, 8)),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ISeqable"), meta=i.Meta(mid92, 20)),
              i.Lookup(kw(u"t"), meta=i.Meta(mid92, 29)),
            ],
            meta=i.Meta(mid92, 7)),
          then=i.Let(names=[kw(u"ts")],
          bindings=[
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid93, 15)),
                i.Lookup(kw(u"t"), meta=i.Meta(mid93, 19)),
              ],
              meta=i.Meta(mid93, 14)),
            ],
            body=i.If(
              test=i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"not"), meta=i.Meta(mid94, 12)),
                  i.Lookup(kw(u"ts"), meta=i.Meta(mid94, 16)),
                ],
                meta=i.Meta(mid94, 11)),
              then=i.Const(nil),
              els=i.If(
                test=i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"-instance?"), meta=i.Meta(mid95, 16)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"first"), meta=i.Meta(mid95, 28)),
                        i.Lookup(kw(u"ts"), meta=i.Meta(mid95, 34)),
                      ],
                      meta=i.Meta(mid95, 27)),
                    i.Lookup(kw(u"x"), meta=i.Meta(mid95, 38)),
                  ],
                  meta=i.Meta(mid95, 15)),
                then=i.Const(true),
                els=i.TailCall(
                  args=[
                    i.Lookup(kw(u"instance?"), meta=i.Meta(mid96, 14)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"rest"), meta=i.Meta(mid96, 25)),
                        i.Lookup(kw(u"ts"), meta=i.Meta(mid96, 30)),
                      ],
                      meta=i.Meta(mid96, 24)),
                    i.Lookup(kw(u"x"), meta=i.Meta(mid96, 34)),
                  ],
                  meta=i.Meta(mid96, 13)),
                meta=i.Meta(mid95, 11)),
              meta=i.Meta(mid94, 7)),
            meta=i.Meta(mid93, 5)),
          els=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-instance?"), meta=i.Meta(mid97, 6)),
              i.Lookup(kw(u"t"), meta=i.Meta(mid97, 17)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid97, 19)),
            ],
            meta=i.Meta(mid97, 5)),
          meta=i.Meta(mid92, 3)),
      )]),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/Reduced)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"Reduced")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"create-type"), meta=nil),
              i.Const(kw(u"pixie.stdlib.Reduced")),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                i.Const(kw(u"x")),
                ]),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/->Reduced)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"->Reduced")),
          i.Fn(args=[kw(u"x")],name=kw(u"->Reduced"),
            body=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"new"), meta=nil),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"Reduced"), meta=i.Meta(mid98, 10)),
                i.Lookup(kw(u"x"), meta=nil),
              ],
              meta=nil),
          )]),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-deref"), meta=i.Meta(mid99, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Reduced"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-deref_Reduced"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid99, 12)),
                  i.Const(kw(u"x")),
                ],
                meta=nil),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid98, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/reduced)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"reduced")),
      i.Fn(args=[kw(u"x")],name=kw(u"reduced"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"->Reduced"), meta=i.Meta(mid100, 4)),
            i.Lookup(kw(u"x"), meta=i.Meta(mid100, 14)),
          ],
          meta=i.Meta(mid100, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/reduced?)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"reduced?")),
      i.Fn(args=[kw(u"x")],name=kw(u"reduced?"),
        body=i.TailCall(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"instance?"), meta=i.Meta(mid101, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Reduced"), meta=i.Meta(mid101, 14)),
            i.Lookup(kw(u"x"), meta=i.Meta(mid101, 22)),
          ],
          meta=i.Meta(mid101, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/satisfies?)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"satisfies?")),
      i.Fn(args=[kw(u"p"),kw(u"x")],name=kw(u"satisfies?"),
        body=i.If(
          test=i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-satisfies?"), meta=i.Meta(mid102, 8)),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"ISeqable"), meta=i.Meta(mid102, 20)),
              i.Lookup(kw(u"p"), meta=i.Meta(mid102, 29)),
            ],
            meta=i.Meta(mid102, 7)),
          then=i.Let(names=[kw(u"ps")],
          bindings=[
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid103, 15)),
                i.Lookup(kw(u"p"), meta=i.Meta(mid103, 19)),
              ],
              meta=i.Meta(mid103, 14)),
            ],
            body=i.If(
              test=i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"not"), meta=i.Meta(mid104, 12)),
                  i.Lookup(kw(u"ps"), meta=i.Meta(mid104, 16)),
                ],
                meta=i.Meta(mid104, 11)),
              then=i.Const(true),
              els=i.If(
                test=i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"not"), meta=i.Meta(mid105, 16)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"-satisfies?"), meta=i.Meta(mid105, 21)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"first"), meta=i.Meta(mid105, 34)),
                            i.Lookup(kw(u"ps"), meta=i.Meta(mid105, 40)),
                          ],
                          meta=i.Meta(mid105, 33)),
                        i.Lookup(kw(u"x"), meta=i.Meta(mid105, 44)),
                      ],
                      meta=i.Meta(mid105, 20)),
                  ],
                  meta=i.Meta(mid105, 15)),
                then=i.Const(nil),
                els=i.TailCall(
                  args=[
                    i.Lookup(kw(u"satisfies?"), meta=i.Meta(mid106, 14)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"rest"), meta=i.Meta(mid106, 26)),
                        i.Lookup(kw(u"ps"), meta=i.Meta(mid106, 31)),
                      ],
                      meta=i.Meta(mid106, 25)),
                    i.Lookup(kw(u"x"), meta=i.Meta(mid106, 35)),
                  ],
                  meta=i.Meta(mid106, 13)),
                meta=i.Meta(mid105, 11)),
              meta=i.Meta(mid104, 7)),
            meta=i.Meta(mid103, 5)),
          els=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-satisfies?"), meta=i.Meta(mid107, 6)),
              i.Lookup(kw(u"p"), meta=i.Meta(mid107, 18)),
              i.Lookup(kw(u"x"), meta=i.Meta(mid107, 20)),
            ],
            meta=i.Meta(mid107, 5)),
          meta=i.Meta(mid102, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/transduce)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"transduce")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"transduce")),
              i.Const(rt.wrap(3)), i.Fn(args=[kw(u"xform"),kw(u"rf"),kw(u"coll")],name=kw(u"transduce"),
          body=i.Let(names=[kw(u"f"),kw(u"result")],
          bindings=[
            i.Invoke(
              args=[
                i.Lookup(kw(u"xform"), meta=i.Meta(mid108, 13)),
                i.Lookup(kw(u"rf"), meta=i.Meta(mid108, 19)),
              ],
              meta=i.Meta(mid108, 12)),
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-reduce"), meta=i.Meta(mid109, 18)),
                i.Lookup(kw(u"coll"), meta=i.Meta(mid109, 26)),
                i.Lookup(kw(u"f"), meta=i.Meta(mid109, 31)),
                i.Invoke(
                  args=[
                    i.Lookup(kw(u"f"), meta=i.Meta(mid109, 34)),
                  ],
                  meta=i.Meta(mid109, 33)),
              ],
              meta=i.Meta(mid109, 17)),
            ],
            body=i.TailCall(
              args=[
                i.Lookup(kw(u"f"), meta=i.Meta(mid110, 7)),
                i.Lookup(kw(u"result"), meta=i.Meta(mid110, 9)),
              ],
              meta=i.Meta(mid110, 6)),
            meta=i.Meta(mid108, 4)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"f"),kw(u"coll")],name=kw(u"transduce"),
          body=i.Let(names=[kw(u"result")],
          bindings=[
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-reduce"), meta=i.Meta(mid111, 18)),
                i.Lookup(kw(u"coll"), meta=i.Meta(mid111, 26)),
                i.Lookup(kw(u"f"), meta=i.Meta(mid111, 31)),
                i.Invoke(
                  args=[
                    i.Lookup(kw(u"f"), meta=i.Meta(mid111, 34)),
                  ],
                  meta=i.Meta(mid111, 33)),
              ],
              meta=i.Meta(mid111, 17)),
            ],
            body=i.TailCall(
              args=[
                i.Lookup(kw(u"f"), meta=i.Meta(mid112, 7)),
                i.Lookup(kw(u"result"), meta=i.Meta(mid112, 9)),
              ],
              meta=i.Meta(mid112, 6)),
            meta=i.Meta(mid111, 4)),
        ),
        i.Const(rt.wrap(4)), i.Fn(args=[kw(u"xform"),kw(u"rf"),kw(u"init"),kw(u"coll")],name=kw(u"transduce"),
          body=i.Let(names=[kw(u"f"),kw(u"result")],
          bindings=[
            i.Invoke(
              args=[
                i.Lookup(kw(u"xform"), meta=i.Meta(mid113, 13)),
                i.Lookup(kw(u"rf"), meta=i.Meta(mid113, 19)),
              ],
              meta=i.Meta(mid113, 12)),
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-reduce"), meta=i.Meta(mid114, 18)),
                i.Lookup(kw(u"coll"), meta=i.Meta(mid114, 26)),
                i.Lookup(kw(u"f"), meta=i.Meta(mid114, 31)),
                i.Lookup(kw(u"init"), meta=i.Meta(mid114, 33)),
              ],
              meta=i.Meta(mid114, 17)),
            ],
            body=i.TailCall(
              args=[
                i.Lookup(kw(u"f"), meta=i.Meta(mid115, 7)),
                i.Lookup(kw(u"result"), meta=i.Meta(mid115, 9)),
              ],
              meta=i.Meta(mid115, 6)),
            meta=i.Meta(mid113, 4)),
        ),
              ])]),
    i.Invoke(args=[
# (def pixie.stdlib/reduce)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"reduce")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"reduce")),
              i.Const(rt.wrap(3)), i.Fn(args=[kw(u"rf"),kw(u"init"),kw(u"col")],name=kw(u"reduce"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-reduce"), meta=i.Meta(mid116, 5)),
              i.Lookup(kw(u"col"), meta=i.Meta(mid116, 13)),
              i.Lookup(kw(u"rf"), meta=i.Meta(mid116, 17)),
              i.Lookup(kw(u"init"), meta=i.Meta(mid116, 20)),
            ],
            meta=i.Meta(mid116, 4)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"rf"),kw(u"col")],name=kw(u"reduce"),
          body=i.TailCall(
            args=[
              i.Lookup(kw(u"reduce"), meta=i.Meta(mid117, 5)),
              i.Lookup(kw(u"rf"), meta=i.Meta(mid117, 12)),
              i.Invoke(
                args=[
                  i.Lookup(kw(u"rf"), meta=i.Meta(mid117, 16)),
                ],
                meta=i.Meta(mid117, 15)),
              i.Lookup(kw(u"col"), meta=i.Meta(mid117, 20)),
            ],
            meta=i.Meta(mid117, 4)),
        ),
              ])]),
    i.Invoke(args=[
# (def pixie.stdlib/into)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"into")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"into")),
              i.Const(rt.wrap(3)), i.Fn(args=[kw(u"to"),kw(u"xform"),kw(u"from")],name=kw(u"into"),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"satisfies?"), meta=i.Meta(mid118, 9)),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"IToTransient"), meta=i.Meta(mid118, 20)),
                i.Lookup(kw(u"to"), meta=i.Meta(mid118, 33)),
              ],
              meta=i.Meta(mid118, 8)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"transduce"), meta=i.Meta(mid119, 7)),
                i.Lookup(kw(u"xform"), meta=i.Meta(mid119, 17)),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"conj!"), meta=i.Meta(mid119, 23)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"transient"), meta=i.Meta(mid119, 30)),
                    i.Lookup(kw(u"to"), meta=i.Meta(mid119, 40)),
                  ],
                  meta=i.Meta(mid119, 29)),
                i.Lookup(kw(u"from"), meta=i.Meta(mid119, 44)),
              ],
              meta=i.Meta(mid119, 6)),
            els=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"transduce"), meta=i.Meta(mid120, 7)),
                i.Lookup(kw(u"xform"), meta=i.Meta(mid120, 17)),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"conj"), meta=i.Meta(mid120, 23)),
                i.Lookup(kw(u"to"), meta=i.Meta(mid120, 28)),
                i.Lookup(kw(u"from"), meta=i.Meta(mid120, 31)),
              ],
              meta=i.Meta(mid120, 6)),
            meta=i.Meta(mid118, 4)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"to"),kw(u"from")],name=kw(u"into"),
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"satisfies?"), meta=i.Meta(mid121, 9)),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"IToTransient"), meta=i.Meta(mid121, 20)),
                i.Lookup(kw(u"to"), meta=i.Meta(mid121, 33)),
              ],
              meta=i.Meta(mid121, 8)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"persistent!"), meta=i.Meta(mid122, 7)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"reduce"), meta=i.Meta(mid122, 20)),
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"conj!"), meta=i.Meta(mid122, 27)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"transient"), meta=i.Meta(mid122, 34)),
                        i.Lookup(kw(u"to"), meta=i.Meta(mid122, 44)),
                      ],
                      meta=i.Meta(mid122, 33)),
                    i.Lookup(kw(u"from"), meta=i.Meta(mid122, 48)),
                  ],
                  meta=i.Meta(mid122, 19)),
              ],
              meta=i.Meta(mid122, 6)),
            els=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"reduce"), meta=i.Meta(mid123, 7)),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"conj"), meta=i.Meta(mid123, 14)),
                i.Lookup(kw(u"to"), meta=i.Meta(mid123, 19)),
                i.Lookup(kw(u"from"), meta=i.Meta(mid123, 22)),
              ],
              meta=i.Meta(mid123, 6)),
            meta=i.Meta(mid121, 4)),
        ),
              ])]),
    i.Invoke(args=[
# (def pixie.stdlib/map)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"map")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"map")),
              i.Const(rt.wrap(1)), i.Fn(args=[kw(u"f")],name=kw(u"map"),
          body=i.Fn(args=[kw(u"xf")],name=kw(u"fn_476"),closed_overs=[kw(u"f")],
            body=i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"fn_480")),
                          i.Const(rt.wrap(0)), i.Fn(args=[],name=kw(u"fn_480"),closed_overs=[kw(u"xf")],
                body=i.TailCall(
                  args=[
                    i.Lookup(kw(u"xf"), meta=i.Meta(mid124, 13)),
                  ],
                  meta=i.Meta(mid124, 12)),
              ),
              i.Const(rt.wrap(1)), i.Fn(args=[kw(u"result")],name=kw(u"fn_480"),closed_overs=[kw(u"xf")],
                body=i.TailCall(
                  args=[
                    i.Lookup(kw(u"xf"), meta=i.Meta(mid125, 19)),
                    i.Lookup(kw(u"result"), meta=i.Meta(mid125, 22)),
                  ],
                  meta=i.Meta(mid125, 18)),
              ),
              i.Const(rt.wrap(2)), i.Fn(args=[kw(u"result"),kw(u"item")],name=kw(u"fn_480"),closed_overs=[kw(u"xf"),kw(u"f")],
                body=i.TailCall(
                  args=[
                    i.Lookup(kw(u"xf"), meta=i.Meta(mid126, 24)),
                    i.Lookup(kw(u"result"), meta=i.Meta(mid126, 27)),
                    i.Invoke(
                      args=[
                        i.Lookup(kw(u"f"), meta=i.Meta(mid126, 35)),
                        i.Lookup(kw(u"item"), meta=i.Meta(mid126, 37)),
                      ],
                      meta=i.Meta(mid126, 34)),
                  ],
                  meta=i.Meta(mid126, 23)),
              ),
                          ]),
          ),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"f"),kw(u"coll")],name=kw(u"map"),closed_overs=[kw(u"map")],
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"lazy-seq*"), meta=i.Meta(mid127, 5)),
              i.Fn(args=[],name=kw(u"fn_481"),closed_overs=[kw(u"map"),kw(u"f"),kw(u"coll")],
                body=i.Let(names=[kw(u"s")],
                bindings=[
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid128, 16)),
                      i.Lookup(kw(u"coll"), meta=i.Meta(mid128, 20)),
                    ],
                    meta=i.Meta(mid128, 15)),
                  ],
                  body=i.If(
                    test=i.Lookup(kw(u"s"), meta=i.Meta(mid129, 13)),
                    then=i.TailCall(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"cons"), meta=i.Meta(mid130, 12)),
                        i.Invoke(
                          args=[
                            i.Lookup(kw(u"f"), meta=i.Meta(mid130, 18)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"first"), meta=i.Meta(mid130, 21)),
                                i.Lookup(kw(u"s"), meta=i.Meta(mid130, 27)),
                              ],
                              meta=i.Meta(mid130, 20)),
                          ],
                          meta=i.Meta(mid130, 17)),
                        i.Invoke(
                          args=[
                            i.Lookup(kw(u"map"), meta=i.Meta(mid131, 18)),
                            i.Lookup(kw(u"f"), meta=i.Meta(mid131, 22)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"rest"), meta=i.Meta(mid131, 25)),
                                i.Lookup(kw(u"s"), meta=i.Meta(mid131, 30)),
                              ],
                              meta=i.Meta(mid131, 24)),
                          ],
                          meta=i.Meta(mid131, 17)),
                      ],
                      meta=i.Meta(mid130, 11)),
                    els=i.Const(nil),
                    meta=i.Meta(mid129, 9)),
                  meta=i.Meta(mid128, 7)),
              ),
            ],
            meta=i.Meta(mid127, 4)),
        ),
                i.Const(rt.wrap(-1)), 
        i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"variadic-fn")), i.Const(rt.wrap(1)), 
        i.Fn(args=[kw(u"f"),kw(u"colls")],name=kw(u"map"),closed_overs=[kw(u"step"),kw(u"map")],
          body=i.Let(names=[kw(u"step")],
          bindings=[
            i.Fn(args=[kw(u"cs")],name=kw(u"step"),closed_overs=[kw(u"step"),kw(u"map")],
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"lazy-seq*"), meta=i.Meta(mid132, 18)),
                  i.Fn(args=[],name=kw(u"fn_483"),closed_overs=[kw(u"step"),kw(u"map"),kw(u"cs")],
                    body=i.Let(names=[kw(u"ss")],
                    bindings=[
                      i.Invoke(
                        args=[
                          i.Lookup(kw(u"map"), meta=i.Meta(mid133, 30)),
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid133, 34)),
                          i.Lookup(kw(u"cs"), meta=i.Meta(mid133, 38)),
                        ],
                        meta=i.Meta(mid133, 29)),
                      ],
                      body=i.If(
                        test=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"every?"), meta=i.Meta(mid134, 27)),
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"identity"), meta=i.Meta(mid134, 34)),
                            i.Lookup(kw(u"ss"), meta=i.Meta(mid134, 43)),
                          ],
                          meta=i.Meta(mid134, 26)),
                        then=i.TailCall(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"cons"), meta=i.Meta(mid135, 25)),
                            i.Invoke(
                              args=[
                                i.Lookup(kw(u"map"), meta=i.Meta(mid135, 31)),
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"first"), meta=i.Meta(mid135, 35)),
                                i.Lookup(kw(u"ss"), meta=i.Meta(mid135, 41)),
                              ],
                              meta=i.Meta(mid135, 30)),
                            i.Invoke(
                              args=[
                                i.Lookup(kw(u"step"), meta=i.Meta(mid135, 46)),
                                i.Invoke(
                                  args=[
                                    i.Lookup(kw(u"map"), meta=i.Meta(mid135, 52)),
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"rest"), meta=i.Meta(mid135, 56)),
                                    i.Lookup(kw(u"ss"), meta=i.Meta(mid135, 61)),
                                  ],
                                  meta=i.Meta(mid135, 51)),
                              ],
                              meta=i.Meta(mid135, 45)),
                          ],
                          meta=i.Meta(mid135, 24)),
                        els=i.Const(nil),
                        meta=i.Meta(mid134, 22)),
                      meta=i.Meta(mid133, 20)),
                  ),
                ],
                meta=i.Meta(mid132, 17)),
            ),
            ],
            body=i.TailCall(
              args=[
                i.Lookup(kw(u"map"), meta=i.Meta(mid136, 7)),
                i.Fn(args=[kw(u"args")],name=kw(u"fn_485"),closed_overs=[kw(u"f")],
                  body=i.TailCall(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"apply"), meta=i.Meta(mid136, 23)),
                      i.Lookup(kw(u"f"), meta=i.Meta(mid136, 29)),
                      i.Lookup(kw(u"args"), meta=i.Meta(mid136, 31)),
                    ],
                    meta=i.Meta(mid136, 22)),
                ),
                i.Invoke(
                  args=[
                    i.Lookup(kw(u"step"), meta=i.Meta(mid136, 39)),
                    i.Lookup(kw(u"colls"), meta=i.Meta(mid136, 44)),
                  ],
                  meta=i.Meta(mid136, 38)),
              ],
              meta=i.Meta(mid136, 6)),
            meta=i.Meta(mid137, 4)),
        )])
      ])]),
    i.Const(nil),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib.range/Range)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib.range",u"Range")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"create-type"), meta=nil),
              i.Const(kw(u"pixie.stdlib.range.Range")),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                i.Const(kw(u"start")),
                i.Const(kw(u"stop")),
                i.Const(kw(u"step")),
                ]),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib.range/->Range)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib.range",u"->Range")),
          i.Fn(args=[kw(u"start"),kw(u"stop"),kw(u"step")],name=kw(u"->Range"),
            body=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"new"), meta=nil),
                i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=i.Meta(mid138, 10)),
                i.Lookup(kw(u"start"), meta=nil),
                i.Lookup(kw(u"stop"), meta=nil),
                i.Lookup(kw(u"step"), meta=nil),
              ],
              meta=nil),
          )]),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-reduce"), meta=i.Meta(mid139, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"self"),kw(u"f"),kw(u"init")],name=kw(u"-reduce_Range"),
              body=i.Let(names=[kw(u"i"),kw(u"acc")],
              bindings=[
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                    i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                    i.Const(kw(u"start")),
                  ],
                  meta=nil),
                i.Lookup(kw(u"init"), meta=i.Meta(mid140, 16)),
                ],
                body=i.TailCall(
                  args=[
                    i.Fn(args=[kw(u"i"),kw(u"acc")],name=kw(u"pixie.compiler/__loop__fn__"),closed_overs=[kw(u"self"),kw(u"f")],
                      body=i.Let(names=[kw(u"i"),kw(u"acc")],
                      bindings=[
                        i.Lookup(kw(u"i"), meta=i.Meta(mid141, 12)),
                        i.Lookup(kw(u"acc"), meta=i.Meta(mid140, 12)),
                        ],
                        body=i.If(
                          test=i.Let(names=[kw(u"r#__gensym_321")],
                          bindings=[
                            i.If(
                              test=i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid142, 21)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                                      i.Const(kw(u"step")),
                                    ],
                                    meta=nil),
                                  i.Const(rt.wrap(0)),
                                ],
                                meta=i.Meta(mid142, 20)),
                              then=i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid142, 32)),
                                  i.Lookup(kw(u"i"), meta=i.Meta(mid142, 34)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                                      i.Const(kw(u"stop")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid142, 31)),
                              els=i.Const(nil),
                              meta=i.Meta(mid142, 15)),
                            ],
                            body=i.If(
                              test=i.Lookup(kw(u"r#__gensym_321"), meta=nil),
                              then=i.Lookup(kw(u"r#__gensym_321"), meta=nil),
                              els=i.Let(names=[kw(u"r#__gensym_320")],
                              bindings=[
                                i.If(
                                  test=i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid143, 21)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                                          i.Const(kw(u"step")),
                                        ],
                                        meta=nil),
                                      i.Const(rt.wrap(0)),
                                    ],
                                    meta=i.Meta(mid143, 20)),
                                  then=i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid143, 32)),
                                      i.Lookup(kw(u"i"), meta=i.Meta(mid143, 34)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                                          i.Const(kw(u"stop")),
                                        ],
                                        meta=nil),
                                    ],
                                    meta=i.Meta(mid143, 31)),
                                  els=i.Const(nil),
                                  meta=i.Meta(mid143, 15)),
                                ],
                                body=i.If(
                                  test=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                                  then=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                                  els=i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid144, 21)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                                          i.Const(kw(u"step")),
                                        ],
                                        meta=nil),
                                      i.Const(rt.wrap(0)),
                                    ],
                                    meta=i.Meta(mid144, 15)),
                                  meta=nil),
                                meta=nil),
                              meta=nil),
                            meta=i.Meta(mid142, 11)),
                          then=i.Let(names=[kw(u"acc")],
                          bindings=[
                            i.Invoke(
                              args=[
                                i.Lookup(kw(u"f"), meta=i.Meta(mid145, 20)),
                                i.Lookup(kw(u"acc"), meta=i.Meta(mid145, 22)),
                                i.Lookup(kw(u"i"), meta=i.Meta(mid145, 26)),
                              ],
                              meta=i.Meta(mid145, 19)),
                            ],
                            body=i.If(
                              test=i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"reduced?"), meta=i.Meta(mid146, 16)),
                                  i.Lookup(kw(u"acc"), meta=i.Meta(mid146, 25)),
                                ],
                                meta=i.Meta(mid146, 15)),
                              then=i.TailCall(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-deref"), meta=nil),
                                  i.Lookup(kw(u"acc"), meta=i.Meta(mid147, 14)),
                                ],
                                meta=i.Meta(mid147, 13)),
                              els=i.TailCall(
                                args=[
                                  i.Lookup(kw(u"pixie.compiler/__loop__fn__"), meta=nil),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid148, 21)),
                                      i.Lookup(kw(u"i"), meta=i.Meta(mid148, 23)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"self"), meta=i.Meta(mid139, 13)),
                                          i.Const(kw(u"step")),
                                        ],
                                        meta=nil),
                                    ],
                                    meta=i.Meta(mid148, 20)),
                                  i.Lookup(kw(u"acc"), meta=i.Meta(mid148, 31)),
                                ],
                                meta=nil),
                              meta=i.Meta(mid146, 11)),
                            meta=i.Meta(mid145, 9)),
                          els=i.Lookup(kw(u"acc"), meta=i.Meta(mid149, 9)),
                          meta=i.Meta(mid142, 7)),
                        meta=nil),
                    ),
                    i.Lookup(kw(u"i"), meta=i.Meta(mid141, 12)),
                    i.Lookup(kw(u"acc"), meta=i.Meta(mid140, 12)),
                  ],
                  meta=nil),
                meta=i.Meta(mid141, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-count"), meta=i.Meta(mid150, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"self")],name=kw(u"-count_Range"),
              body=i.If(
                test=i.Let(names=[kw(u"r#__gensym_321")],
                bindings=[
                  i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid151, 19)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                            i.Const(kw(u"start")),
                          ],
                          meta=nil),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                            i.Const(kw(u"stop")),
                          ],
                          meta=nil),
                      ],
                      meta=i.Meta(mid151, 18)),
                    then=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid151, 34)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                            i.Const(kw(u"step")),
                          ],
                          meta=nil),
                        i.Const(rt.wrap(0)),
                      ],
                      meta=i.Meta(mid151, 33)),
                    els=i.Const(nil),
                    meta=i.Meta(mid151, 13)),
                  ],
                  body=i.If(
                    test=i.Lookup(kw(u"r#__gensym_321"), meta=nil),
                    then=i.Lookup(kw(u"r#__gensym_321"), meta=nil),
                    els=i.Let(names=[kw(u"r#__gensym_320")],
                    bindings=[
                      i.If(
                        test=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid152, 19)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                                i.Const(kw(u"start")),
                              ],
                              meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                                i.Const(kw(u"stop")),
                              ],
                              meta=nil),
                          ],
                          meta=i.Meta(mid152, 18)),
                        then=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid152, 34)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                                i.Const(kw(u"step")),
                              ],
                              meta=nil),
                            i.Const(rt.wrap(0)),
                          ],
                          meta=i.Meta(mid152, 33)),
                        els=i.Const(nil),
                        meta=i.Meta(mid152, 13)),
                      ],
                      body=i.If(
                        test=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                        then=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                        els=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid153, 14)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                                i.Const(kw(u"step")),
                              ],
                              meta=nil),
                            i.Const(rt.wrap(0)),
                          ],
                          meta=i.Meta(mid153, 13)),
                        meta=nil),
                      meta=nil),
                    meta=nil),
                  meta=i.Meta(mid151, 9)),
                then=i.Const(rt.wrap(0)),
                els=i.TailCall(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"abs"), meta=i.Meta(mid154, 8)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"quot"), meta=i.Meta(mid154, 13)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid154, 19)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                                i.Const(kw(u"start")),
                              ],
                              meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                                i.Const(kw(u"stop")),
                              ],
                              meta=nil),
                          ],
                          meta=i.Meta(mid154, 18)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid150, 12)),
                            i.Const(kw(u"step")),
                          ],
                          meta=nil),
                      ],
                      meta=i.Meta(mid154, 12)),
                  ],
                  meta=i.Meta(mid154, 7)),
                meta=i.Meta(mid151, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth"), meta=i.Meta(mid155, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"self"),kw(u"idx")],name=kw(u"-nth_Range"),
              body=i.Do(
                args=[
                  i.If(
                    test=i.Let(names=[kw(u"r#__gensym_320")],
                    bindings=[
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid156, 16)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                              i.Const(kw(u"start")),
                            ],
                            meta=nil),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                              i.Const(kw(u"stop")),
                            ],
                            meta=nil),
                          i.Const(rt.wrap(0)),
                        ],
                        meta=i.Meta(mid156, 15)),
                      ],
                      body=i.If(
                        test=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                        then=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                        els=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"neg?"), meta=i.Meta(mid156, 33)),
                            i.Lookup(kw(u"idx"), meta=i.Meta(mid156, 38)),
                          ],
                          meta=i.Meta(mid156, 32)),
                        meta=nil),
                      meta=i.Meta(mid156, 11)),
                    then=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=i.Meta(mid157, 8)),
                        i.Invoke(args=[
                          i.Const(code.intern_var(u"pixie.stdlib", u"array")),                          i.Const(kw(u"pixie.stdlib/OutOfRangeException")),
                          i.Const(rt.wrap(u"Index out of Range")),
                          ]),
                      ],
                      meta=i.Meta(mid157, 7)),
                    els=i.Const(nil),
                    meta=i.Meta(mid156, 5)),
                  i.Let(names=[kw(u"cmp"),kw(u"val")],
                  bindings=[
                    i.If(
                      test=i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid158, 20)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                              i.Const(kw(u"start")),
                            ],
                            meta=nil),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                              i.Const(kw(u"stop")),
                            ],
                            meta=nil),
                        ],
                        meta=i.Meta(mid158, 19)),
                      then=i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid158, 34)),
                      els=i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid158, 36)),
                      meta=i.Meta(mid158, 15)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid159, 16)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                            i.Const(kw(u"start")),
                          ],
                          meta=nil),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"*"), meta=i.Meta(mid159, 25)),
                            i.Lookup(kw(u"idx"), meta=i.Meta(mid159, 27)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                                i.Const(kw(u"step")),
                              ],
                              meta=nil),
                          ],
                          meta=i.Meta(mid159, 24)),
                      ],
                      meta=i.Meta(mid159, 15)),
                    ],
                    body=i.If(
                      test=i.Invoke(
                        args=[
                          i.Lookup(kw(u"cmp"), meta=i.Meta(mid160, 12)),
                          i.Lookup(kw(u"val"), meta=i.Meta(mid160, 16)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid155, 10)),
                              i.Const(kw(u"stop")),
                            ],
                            meta=nil),
                        ],
                        meta=i.Meta(mid160, 11)),
                      then=i.Lookup(kw(u"val"), meta=i.Meta(mid161, 9)),
                      els=i.TailCall(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=i.Meta(mid162, 10)),
                          i.Invoke(args=[
                            i.Const(code.intern_var(u"pixie.stdlib", u"array")),                            i.Const(kw(u"pixie.stdlib/OutOfRangeException")),
                            i.Const(rt.wrap(u"Index out of Range")),
                            ]),
                        ],
                        meta=i.Meta(mid162, 9)),
                      meta=i.Meta(mid160, 7)),
                    meta=i.Meta(mid158, 5)),
                ],
              meta=nil),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth-not-found"), meta=i.Meta(mid163, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"self"),kw(u"idx"),kw(u"not-found")],name=kw(u"-nth-not-found_Range"),
              body=i.Let(names=[kw(u"cmp"),kw(u"val")],
              bindings=[
                i.If(
                  test=i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid164, 20)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                          i.Lookup(kw(u"self"), meta=i.Meta(mid163, 20)),
                          i.Const(kw(u"start")),
                        ],
                        meta=nil),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                          i.Lookup(kw(u"self"), meta=i.Meta(mid163, 20)),
                          i.Const(kw(u"stop")),
                        ],
                        meta=nil),
                    ],
                    meta=i.Meta(mid164, 19)),
                  then=i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid164, 34)),
                  els=i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid164, 36)),
                  meta=i.Meta(mid164, 15)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid165, 16)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                        i.Lookup(kw(u"self"), meta=i.Meta(mid163, 20)),
                        i.Const(kw(u"start")),
                      ],
                      meta=nil),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"*"), meta=i.Meta(mid165, 25)),
                        i.Lookup(kw(u"idx"), meta=i.Meta(mid165, 27)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid163, 20)),
                            i.Const(kw(u"step")),
                          ],
                          meta=nil),
                      ],
                      meta=i.Meta(mid165, 24)),
                  ],
                  meta=i.Meta(mid165, 15)),
                ],
                body=i.If(
                  test=i.Invoke(
                    args=[
                      i.Lookup(kw(u"cmp"), meta=i.Meta(mid166, 12)),
                      i.Lookup(kw(u"val"), meta=i.Meta(mid166, 16)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                          i.Lookup(kw(u"self"), meta=i.Meta(mid163, 20)),
                          i.Const(kw(u"stop")),
                        ],
                        meta=nil),
                    ],
                    meta=i.Meta(mid166, 11)),
                  then=i.Lookup(kw(u"val"), meta=i.Meta(mid167, 9)),
                  els=i.Lookup(kw(u"not-found"), meta=i.Meta(mid168, 8)),
                  meta=i.Meta(mid166, 7)),
                meta=i.Meta(mid164, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-seq"), meta=i.Meta(mid169, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"self")],name=kw(u"-seq_Range"),
              body=i.If(
                test=i.Let(names=[kw(u"r#__gensym_320")],
                bindings=[
                  i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid170, 21)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                            i.Const(kw(u"step")),
                          ],
                          meta=nil),
                        i.Const(rt.wrap(0)),
                      ],
                      meta=i.Meta(mid170, 20)),
                    then=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid170, 32)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                            i.Const(kw(u"start")),
                          ],
                          meta=nil),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                            i.Const(kw(u"stop")),
                          ],
                          meta=nil),
                      ],
                      meta=i.Meta(mid170, 31)),
                    els=i.Const(nil),
                    meta=i.Meta(mid170, 15)),
                  ],
                  body=i.If(
                    test=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                    then=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                    els=i.If(
                      test=i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid171, 21)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                              i.Const(kw(u"step")),
                            ],
                            meta=nil),
                          i.Const(rt.wrap(0)),
                        ],
                        meta=i.Meta(mid171, 20)),
                      then=i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid171, 32)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                              i.Const(kw(u"start")),
                            ],
                            meta=nil),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                              i.Const(kw(u"stop")),
                            ],
                            meta=nil),
                        ],
                        meta=i.Meta(mid171, 31)),
                      els=i.Const(nil),
                      meta=i.Meta(mid171, 15)),
                    meta=nil),
                  meta=i.Meta(mid170, 11)),
                then=i.TailCall(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"cons"), meta=i.Meta(mid172, 8)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                        i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                        i.Const(kw(u"start")),
                      ],
                      meta=nil),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"lazy-seq*"), meta=i.Meta(mid172, 20)),
                        i.Fn(args=[],name=kw(u"fn_504"),closed_overs=[kw(u"self")],
                          body=i.TailCall(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"range"), meta=i.Meta(mid172, 32)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid172, 39)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                                      i.Const(kw(u"start")),
                                    ],
                                    meta=nil),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                                      i.Const(kw(u"step")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid172, 38)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                                  i.Const(kw(u"stop")),
                                ],
                                meta=nil),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"self"), meta=i.Meta(mid169, 10)),
                                  i.Const(kw(u"step")),
                                ],
                                meta=nil),
                            ],
                            meta=i.Meta(mid172, 31)),
                        ),
                      ],
                      meta=i.Meta(mid172, 19)),
                  ],
                  meta=i.Meta(mid172, 7)),
                els=i.Const(nil),
                meta=i.Meta(mid170, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid173, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"sbf")],name=kw(u"-str_Range"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-str"), meta=i.Meta(mid174, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid174, 12)),
                      i.Lookup(kw(u"this"), meta=i.Meta(mid174, 16)),
                    ],
                    meta=i.Meta(mid174, 11)),
                  i.Lookup(kw(u"sbf"), meta=i.Meta(mid174, 22)),
                ],
                meta=i.Meta(mid174, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-repr"), meta=i.Meta(mid175, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"sbf")],name=kw(u"-repr_Range"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-repr"), meta=i.Meta(mid176, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"seq"), meta=i.Meta(mid176, 13)),
                      i.Lookup(kw(u"this"), meta=i.Meta(mid176, 17)),
                    ],
                    meta=i.Meta(mid176, 12)),
                  i.Lookup(kw(u"sbf"), meta=i.Meta(mid176, 23)),
                ],
                meta=i.Meta(mid176, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-eq"), meta=i.Meta(mid177, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib.range", u"Range"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"sb")],name=kw(u"-eq_Range"),
              body=i.Const(nil),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid138, 1)),
    i.Invoke(args=[
# (def pixie.stdlib.range/MAX-NUMBER)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib.range",u"MAX-NUMBER")),
      i.Const(rt.wrap(4294967295))]),
    i.Const(nil),
    i.Invoke(args=[
# (def pixie.stdlib/range)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"range")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"range")),
              i.Const(rt.wrap(0)), i.Fn(args=[],name=kw(u"range"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib.range", u"->Range"), meta=i.Meta(mid178, 8)),
              i.Const(rt.wrap(0)),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"MAX-NUMBER"), meta=i.Meta(mid178, 37)),
              i.Const(rt.wrap(1)),
            ],
            meta=i.Meta(mid178, 7)),
        ),
        i.Const(rt.wrap(1)), i.Fn(args=[kw(u"stop")],name=kw(u"range"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib.range", u"->Range"), meta=i.Meta(mid179, 12)),
              i.Const(rt.wrap(0)),
              i.Lookup(kw(u"stop"), meta=i.Meta(mid179, 41)),
              i.Const(rt.wrap(1)),
            ],
            meta=i.Meta(mid179, 11)),
        ),
        i.Const(rt.wrap(3)), i.Fn(args=[kw(u"start"),kw(u"stop"),kw(u"step")],name=kw(u"range"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib.range", u"->Range"), meta=i.Meta(mid180, 23)),
              i.Lookup(kw(u"start"), meta=i.Meta(mid180, 50)),
              i.Lookup(kw(u"stop"), meta=i.Meta(mid180, 56)),
              i.Lookup(kw(u"step"), meta=i.Meta(mid180, 61)),
            ],
            meta=i.Meta(mid180, 22)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"start"),kw(u"stop")],name=kw(u"range"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib.range", u"->Range"), meta=i.Meta(mid181, 18)),
              i.Lookup(kw(u"start"), meta=i.Meta(mid181, 45)),
              i.Lookup(kw(u"stop"), meta=i.Meta(mid181, 51)),
              i.Const(rt.wrap(1)),
            ],
            meta=i.Meta(mid181, 17)),
        ),
              ])]),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/Node)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"Node")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"create-type"), meta=nil),
              i.Const(kw(u"pixie.stdlib.Node")),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                i.Const(kw(u"edit")),
                i.Const(kw(u"array")),
                ]),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/->Node)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"->Node")),
          i.Fn(args=[kw(u"edit"),kw(u"array")],name=kw(u"->Node"),
            body=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"new"), meta=nil),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"Node"), meta=i.Meta(mid182, 10)),
                i.Lookup(kw(u"edit"), meta=nil),
                i.Lookup(kw(u"array"), meta=nil),
              ],
              meta=nil),
          )]),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid183, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Node"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"name")],name=kw(u"-get-field_Node"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=i.Meta(mid184, 6)),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid184, 16)),
                  i.Lookup(kw(u"name"), meta=i.Meta(mid184, 21)),
                ],
                meta=i.Meta(mid184, 5)),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid182, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/new-node)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"new-node")),
      i.Invoke([i.Const(code.intern_var(u"pixie.stdlib", u"multi-arity-fn")), i.Const(rt.wrap(u"new-node")),
              i.Const(rt.wrap(1)), i.Fn(args=[kw(u"edit")],name=kw(u"new-node"),
          body=i.TailCall(
            args=[
              i.Lookup(kw(u"new-node"), meta=i.Meta(mid185, 5)),
              i.Lookup(kw(u"edit"), meta=i.Meta(mid185, 14)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"make-array"), meta=i.Meta(mid185, 20)),
                  i.Const(rt.wrap(32)),
                ],
                meta=i.Meta(mid185, 19)),
            ],
            meta=i.Meta(mid185, 4)),
        ),
        i.Const(rt.wrap(2)), i.Fn(args=[kw(u"edit"),kw(u"array")],name=kw(u"new-node"),
          body=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"->Node"), meta=i.Meta(mid186, 5)),
              i.Lookup(kw(u"edit"), meta=i.Meta(mid186, 12)),
              i.Lookup(kw(u"array"), meta=i.Meta(mid186, 17)),
            ],
            meta=i.Meta(mid186, 4)),
        ),
              ])]),
    i.Invoke(args=[
# (def pixie.stdlib/EMPTY-NODE)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"EMPTY-NODE")),
      i.Invoke(
        args=[
          i.VDeref(code.intern_var(u"pixie.stdlib", u"new-node"), meta=i.Meta(mid187, 18)),
          i.Const(nil),
        ],
        meta=i.Meta(mid187, 17))]),
    i.Invoke(args=[
# (def pixie.stdlib/tailoff)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"tailoff")),
      i.Fn(args=[kw(u"this")],name=kw(u"tailoff"),
        body=i.Let(names=[kw(u"cnt")],
        bindings=[
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
              i.Lookup(kw(u"this"), meta=i.Meta(mid189, 20)),
              i.Const(kw(u"cnt")),
            ],
            meta=i.Meta(mid189, 13)),
          ],
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid190, 10)),
                i.Lookup(kw(u"cnt"), meta=i.Meta(mid190, 12)),
                i.Const(rt.wrap(32)),
              ],
              meta=i.Meta(mid190, 9)),
            then=i.Const(rt.wrap(0)),
            els=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-left"), meta=i.Meta(mid191, 8)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-right"), meta=i.Meta(mid191, 24)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid191, 41)),
                        i.Lookup(kw(u"cnt"), meta=i.Meta(mid191, 45)),
                      ],
                      meta=i.Meta(mid191, 40)),
                    i.Const(rt.wrap(5)),
                  ],
                  meta=i.Meta(mid191, 23)),
                i.Const(rt.wrap(5)),
              ],
              meta=i.Meta(mid191, 7)),
            meta=i.Meta(mid190, 5)),
          meta=i.Meta(mid189, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/array-for)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"array-for")),
      i.Fn(args=[kw(u"this"),kw(u"i")],name=kw(u"array-for"),
        body=i.If(
          test=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"<="), meta=i.Meta(mid192, 13)),
                i.Const(rt.wrap(0)),
                i.Lookup(kw(u"i"), meta=i.Meta(mid192, 18)),
              ],
              meta=i.Meta(mid192, 12)),
            then=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid192, 22)),
                i.Lookup(kw(u"i"), meta=i.Meta(mid192, 24)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                    i.Lookup(kw(u"this"), meta=i.Meta(mid192, 33)),
                    i.Const(kw(u"cnt")),
                  ],
                  meta=i.Meta(mid192, 26)),
              ],
              meta=i.Meta(mid192, 21)),
            els=i.Const(nil),
            meta=i.Meta(mid192, 7)),
          then=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u">="), meta=i.Meta(mid193, 10)),
                i.Lookup(kw(u"i"), meta=i.Meta(mid193, 13)),
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"tailoff"), meta=i.Meta(mid193, 16)),
                    i.Lookup(kw(u"this"), meta=i.Meta(mid193, 24)),
                  ],
                  meta=i.Meta(mid193, 15)),
              ],
              meta=i.Meta(mid193, 9)),
            then=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                i.Lookup(kw(u"this"), meta=i.Meta(mid194, 15)),
                i.Const(kw(u"tail")),
              ],
              meta=i.Meta(mid194, 7)),
            els=i.Let(names=[kw(u"node"),kw(u"level")],
            bindings=[
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid195, 27)),
                  i.Const(kw(u"root")),
                ],
                meta=i.Meta(mid195, 19)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid196, 29)),
                  i.Const(kw(u"shift")),
                ],
                meta=i.Meta(mid196, 20)),
              ],
              body=i.TailCall(
                args=[
                  i.Fn(args=[kw(u"node"),kw(u"level")],name=kw(u"pixie.compiler/__loop__fn__"),closed_overs=[kw(u"i")],
                    body=i.Let(names=[kw(u"node"),kw(u"level")],
                    bindings=[
                      i.Lookup(kw(u"node"), meta=i.Meta(mid195, 14)),
                      i.Lookup(kw(u"level"), meta=i.Meta(mid196, 14)),
                      ],
                      body=i.If(
                        test=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid197, 14)),
                            i.Lookup(kw(u"level"), meta=i.Meta(mid197, 16)),
                            i.Const(rt.wrap(0)),
                          ],
                          meta=i.Meta(mid197, 13)),
                        then=i.TailCall(
                          args=[
                            i.Lookup(kw(u"pixie.compiler/__loop__fn__"), meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid198, 19)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                                    i.Lookup(kw(u"node"), meta=i.Meta(mid198, 33)),
                                    i.Const(kw(u"array")),
                                  ],
                                  meta=i.Meta(mid198, 24)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-and"), meta=i.Meta(mid199, 25)),
                                    i.Invoke(
                                      args=[
                                        i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-right"), meta=i.Meta(mid199, 34)),
                                        i.Lookup(kw(u"i"), meta=i.Meta(mid199, 50)),
                                        i.Lookup(kw(u"level"), meta=i.Meta(mid199, 52)),
                                      ],
                                      meta=i.Meta(mid199, 33)),
                                    i.Const(rt.wrap(31)),
                                  ],
                                  meta=i.Meta(mid199, 24)),
                              ],
                              meta=i.Meta(mid198, 18)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid200, 19)),
                                i.Lookup(kw(u"level"), meta=i.Meta(mid200, 21)),
                                i.Const(rt.wrap(5)),
                              ],
                              meta=i.Meta(mid200, 18)),
                          ],
                          meta=nil),
                        els=i.TailCall(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                            i.Lookup(kw(u"node"), meta=i.Meta(mid201, 20)),
                            i.Const(kw(u"array")),
                          ],
                          meta=i.Meta(mid201, 11)),
                        meta=i.Meta(mid197, 9)),
                      meta=nil),
                  ),
                  i.Lookup(kw(u"node"), meta=i.Meta(mid195, 14)),
                  i.Lookup(kw(u"level"), meta=i.Meta(mid196, 14)),
                ],
                meta=nil),
              meta=i.Meta(mid195, 7)),
            meta=i.Meta(mid193, 5)),
          els=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=i.Meta(mid202, 6)),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                i.Const(kw(u"pixie.stdlib/IndexOutOfRangeException")),
                i.Const(rt.wrap(u"Index out of range")),
                ]),
            ],
            meta=i.Meta(mid202, 5)),
          meta=i.Meta(mid192, 3)),
      )]),
    i.Do(
      args=[
        i.Invoke(args=[
# (def pixie.stdlib/PersistentVector)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"PersistentVector")),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"create-type"), meta=nil),
              i.Const(kw(u"pixie.stdlib.PersistentVector")),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                i.Const(kw(u"cnt")),
                i.Const(kw(u"shift")),
                i.Const(kw(u"root")),
                i.Const(kw(u"tail")),
                i.Const(kw(u"meta")),
                ]),
            ],
            meta=nil)]),
        i.Invoke(args=[
# (def pixie.stdlib/->PersistentVector)
          i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
          i.Const(code.intern_var(u"pixie.stdlib",u"->PersistentVector")),
          i.Fn(args=[kw(u"cnt"),kw(u"shift"),kw(u"root"),kw(u"tail"),kw(u"meta")],name=kw(u"->PersistentVector"),
            body=i.TailCall(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"new"), meta=nil),
                i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=i.Meta(mid203, 10)),
                i.Lookup(kw(u"cnt"), meta=nil),
                i.Lookup(kw(u"shift"), meta=nil),
                i.Lookup(kw(u"root"), meta=nil),
                i.Lookup(kw(u"tail"), meta=nil),
                i.Lookup(kw(u"meta"), meta=nil),
              ],
              meta=nil),
          )]),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid204, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"name")],name=kw(u"-get-field_PersistentVector"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=i.Meta(mid205, 6)),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid205, 16)),
                  i.Lookup(kw(u"name"), meta=i.Meta(mid205, 21)),
                ],
                meta=i.Meta(mid205, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-conj"), meta=i.Meta(mid206, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"val")],name=kw(u"-conj_PersistentVector"),
              body=i.Do(
                args=[
                  i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid207, 14)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                            i.Const(kw(u"cnt")),
                          ],
                          meta=nil),
                        i.Const(rt.wrap(4294967295)),
                      ],
                      meta=i.Meta(mid207, 13)),
                    then=i.Const(nil),
                    els=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=nil),
                        i.Invoke(args=[
                          i.Const(code.intern_var(u"pixie.stdlib", u"array")),                          i.Const(kw(u"pixie.stdlib/AssertionException")),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"str"), meta=nil),
                              i.Const(rt.wrap(u"Assert failed: ")),
                              i.Const(rt.wrap(u"Vector too large")),
                            ],
                            meta=nil),
                          ]),
                      ],
                      meta=nil),
                    meta=i.Meta(mid207, 5)),
                  i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid208, 10)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid208, 13)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                i.Const(kw(u"cnt")),
                              ],
                              meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"tailoff"), meta=i.Meta(mid208, 20)),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid208, 28)),
                              ],
                              meta=i.Meta(mid208, 19)),
                          ],
                          meta=i.Meta(mid208, 12)),
                        i.Const(rt.wrap(32)),
                      ],
                      meta=i.Meta(mid208, 9)),
                    then=i.Let(names=[kw(u"new-tail")],
                    bindings=[
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"array-append"), meta=i.Meta(mid209, 23)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                              i.Const(kw(u"tail")),
                            ],
                            meta=nil),
                          i.Lookup(kw(u"val"), meta=i.Meta(mid209, 41)),
                        ],
                        meta=i.Meta(mid209, 22)),
                      ],
                      body=i.TailCall(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid210, 10)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid210, 30)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                  i.Const(kw(u"cnt")),
                                ],
                                meta=nil),
                            ],
                            meta=i.Meta(mid210, 29)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                              i.Const(kw(u"shift")),
                            ],
                            meta=nil),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                              i.Const(kw(u"root")),
                            ],
                            meta=nil),
                          i.Lookup(kw(u"new-tail"), meta=i.Meta(mid210, 50)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                              i.Const(kw(u"meta")),
                            ],
                            meta=nil),
                        ],
                        meta=i.Meta(mid210, 9)),
                      meta=i.Meta(mid209, 7)),
                    els=i.Let(names=[kw(u"tail-node")],
                    bindings=[
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"->Node"), meta=i.Meta(mid211, 24)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                  i.Const(kw(u"root")),
                                ],
                                meta=nil),
                              i.Const(kw(u"edit")),
                            ],
                            meta=i.Meta(mid211, 31)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                              i.Const(kw(u"tail")),
                            ],
                            meta=nil),
                        ],
                        meta=i.Meta(mid211, 23)),
                      ],
                      body=i.If(
                        test=i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid212, 14)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-right"), meta=i.Meta(mid212, 17)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                    i.Const(kw(u"cnt")),
                                  ],
                                  meta=nil),
                                i.Const(rt.wrap(5)),
                              ],
                              meta=i.Meta(mid212, 16)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-left"), meta=i.Meta(mid212, 41)),
                                i.Const(rt.wrap(1)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                    i.Const(kw(u"shift")),
                                  ],
                                  meta=nil),
                              ],
                              meta=i.Meta(mid212, 40)),
                          ],
                          meta=i.Meta(mid212, 13)),
                        then=i.Let(names=[kw(u"new-root"),kw(u"new-root-arr")],
                        bindings=[
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"new-node"), meta=i.Meta(mid213, 27)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                      i.Const(kw(u"root")),
                                    ],
                                    meta=nil),
                                  i.Const(kw(u"edit")),
                                ],
                                meta=i.Meta(mid213, 36)),
                            ],
                            meta=i.Meta(mid213, 26)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                              i.Lookup(kw(u"new-root"), meta=i.Meta(mid214, 39)),
                              i.Const(kw(u"array")),
                            ],
                            meta=i.Meta(mid214, 30)),
                          ],
                          body=i.Do(
                            args=[
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid215, 14)),
                                  i.Lookup(kw(u"new-root-arr"), meta=i.Meta(mid215, 19)),
                                  i.Const(rt.wrap(0)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                      i.Const(kw(u"root")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid215, 13)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid216, 14)),
                                  i.Lookup(kw(u"new-root-arr"), meta=i.Meta(mid216, 19)),
                                  i.Const(rt.wrap(1)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"new-path"), meta=i.Meta(mid216, 35)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                                          i.Invoke(
                                            args=[
                                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                              i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                              i.Const(kw(u"root")),
                                            ],
                                            meta=nil),
                                          i.Const(kw(u"edit")),
                                        ],
                                        meta=i.Meta(mid216, 44)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                          i.Const(kw(u"shift")),
                                        ],
                                        meta=nil),
                                      i.Lookup(kw(u"tail-node"), meta=i.Meta(mid216, 64)),
                                    ],
                                    meta=i.Meta(mid216, 34)),
                                ],
                                meta=i.Meta(mid216, 13)),
                              i.TailCall(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid217, 14)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid217, 34)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                          i.Const(kw(u"cnt")),
                                        ],
                                        meta=nil),
                                    ],
                                    meta=i.Meta(mid217, 33)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid218, 34)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                          i.Const(kw(u"shift")),
                                        ],
                                        meta=nil),
                                      i.Const(rt.wrap(5)),
                                    ],
                                    meta=i.Meta(mid218, 33)),
                                  i.Lookup(kw(u"new-root"), meta=i.Meta(mid219, 33)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"array"), meta=i.Meta(mid220, 34)),
                                      i.Lookup(kw(u"val"), meta=i.Meta(mid220, 40)),
                                    ],
                                    meta=i.Meta(mid220, 33)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                      i.Const(kw(u"meta")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid217, 13)),
                            ],
                          meta=nil),
                          meta=i.Meta(mid213, 11)),
                        els=i.Let(names=[kw(u"new-root")],
                        bindings=[
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"push-tail"), meta=i.Meta(mid221, 27)),
                              i.Lookup(kw(u"this"), meta=i.Meta(mid221, 37)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                  i.Const(kw(u"shift")),
                                ],
                                meta=nil),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                  i.Const(kw(u"root")),
                                ],
                                meta=nil),
                              i.Lookup(kw(u"tail-node"), meta=i.Meta(mid221, 53)),
                            ],
                            meta=i.Meta(mid221, 26)),
                          ],
                          body=i.TailCall(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid222, 14)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid222, 34)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                      i.Const(kw(u"cnt")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid222, 33)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                  i.Const(kw(u"shift")),
                                ],
                                meta=nil),
                              i.Lookup(kw(u"new-root"), meta=i.Meta(mid223, 33)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"array"), meta=i.Meta(mid224, 34)),
                                  i.Lookup(kw(u"val"), meta=i.Meta(mid224, 40)),
                                ],
                                meta=i.Meta(mid224, 33)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid206, 11)),
                                  i.Const(kw(u"meta")),
                                ],
                                meta=nil),
                            ],
                            meta=i.Meta(mid222, 13)),
                          meta=i.Meta(mid221, 11)),
                        meta=i.Meta(mid212, 9)),
                      meta=i.Meta(mid211, 7)),
                    meta=i.Meta(mid208, 5)),
                ],
              meta=nil),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth"), meta=i.Meta(mid225, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"self"),kw(u"i")],name=kw(u"-nth_PersistentVector"),
              body=i.If(
                test=i.If(
                  test=i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"<="), meta=i.Meta(mid226, 15)),
                      i.Const(rt.wrap(0)),
                      i.Lookup(kw(u"i"), meta=i.Meta(mid226, 20)),
                    ],
                    meta=i.Meta(mid226, 14)),
                  then=i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid227, 15)),
                      i.Lookup(kw(u"i"), meta=i.Meta(mid227, 17)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                          i.Lookup(kw(u"self"), meta=i.Meta(mid225, 10)),
                          i.Const(kw(u"cnt")),
                        ],
                        meta=nil),
                    ],
                    meta=i.Meta(mid227, 14)),
                  els=i.Const(nil),
                  meta=i.Meta(mid226, 9)),
                then=i.Let(names=[kw(u"node")],
                bindings=[
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"array-for"), meta=i.Meta(mid228, 19)),
                      i.Lookup(kw(u"self"), meta=i.Meta(mid228, 29)),
                      i.Lookup(kw(u"i"), meta=i.Meta(mid228, 34)),
                    ],
                    meta=i.Meta(mid228, 18)),
                  ],
                  body=i.TailCall(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid229, 10)),
                      i.Lookup(kw(u"node"), meta=i.Meta(mid229, 15)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-and"), meta=i.Meta(mid229, 21)),
                          i.Lookup(kw(u"i"), meta=i.Meta(mid229, 29)),
                          i.Const(rt.wrap(31)),
                        ],
                        meta=i.Meta(mid229, 20)),
                    ],
                    meta=i.Meta(mid229, 9)),
                  meta=i.Meta(mid228, 7)),
                els=i.TailCall(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=i.Meta(mid230, 8)),
                    i.Invoke(args=[
                      i.Const(code.intern_var(u"pixie.stdlib", u"array")),                      i.Const(kw(u"pixie.stdlib/IndexOutOfRange")),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"str"), meta=i.Meta(mid231, 16)),
                          i.Const(rt.wrap(u"Index out of range, got ")),
                          i.Lookup(kw(u"i"), meta=i.Meta(mid231, 47)),
                          i.Const(rt.wrap(u" only have ")),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                              i.Lookup(kw(u"self"), meta=i.Meta(mid225, 10)),
                              i.Const(kw(u"cnt")),
                            ],
                            meta=nil),
                        ],
                        meta=i.Meta(mid231, 15)),
                      ]),
                  ],
                  meta=i.Meta(mid230, 7)),
                meta=i.Meta(mid226, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth-not-found"), meta=i.Meta(mid232, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"self"),kw(u"i"),kw(u"not-found")],name=kw(u"-nth-not-found_PersistentVector"),
              body=i.If(
                test=i.If(
                  test=i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"<="), meta=i.Meta(mid233, 15)),
                      i.Const(rt.wrap(0)),
                      i.Lookup(kw(u"i"), meta=i.Meta(mid233, 20)),
                    ],
                    meta=i.Meta(mid233, 14)),
                  then=i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid234, 15)),
                      i.Lookup(kw(u"i"), meta=i.Meta(mid234, 17)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                          i.Lookup(kw(u"self"), meta=i.Meta(mid232, 20)),
                          i.Const(kw(u"cnt")),
                        ],
                        meta=nil),
                    ],
                    meta=i.Meta(mid234, 14)),
                  els=i.Const(nil),
                  meta=i.Meta(mid233, 9)),
                then=i.Let(names=[kw(u"node")],
                bindings=[
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"array-for"), meta=i.Meta(mid235, 19)),
                      i.Lookup(kw(u"self"), meta=i.Meta(mid235, 29)),
                      i.Lookup(kw(u"i"), meta=i.Meta(mid235, 34)),
                    ],
                    meta=i.Meta(mid235, 18)),
                  ],
                  body=i.TailCall(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid236, 10)),
                      i.Lookup(kw(u"node"), meta=i.Meta(mid236, 15)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-and"), meta=i.Meta(mid236, 21)),
                          i.Lookup(kw(u"i"), meta=i.Meta(mid236, 29)),
                          i.Const(rt.wrap(31)),
                        ],
                        meta=i.Meta(mid236, 20)),
                    ],
                    meta=i.Meta(mid236, 9)),
                  meta=i.Meta(mid235, 7)),
                els=i.Lookup(kw(u"not-found"), meta=i.Meta(mid237, 7)),
                meta=i.Meta(mid233, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-get"), meta=i.Meta(mid238, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"this"),kw(u"val")],name=kw(u"-get_PersistentVector"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-nth-not-found"), meta=i.Meta(mid239, 6)),
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"self"), meta=i.Meta(mid239, 21)),
                  i.Lookup(kw(u"val"), meta=i.Meta(mid239, 26)),
                  i.Const(nil),
                ],
                meta=i.Meta(mid239, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-count"), meta=i.Meta(mid240, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-count_PersistentVector"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                  i.Lookup(kw(u"this"), meta=i.Meta(mid240, 12)),
                  i.Const(kw(u"cnt")),
                ],
                meta=nil),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-pop"), meta=i.Meta(mid241, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"PersistentVector"), meta=nil),
            i.Fn(args=[kw(u"this")],name=kw(u"-pop_PersistentVector"),
              body=i.Do(
                args=[
                  i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"!="), meta=i.Meta(mid242, 14)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                            i.Const(kw(u"cnt")),
                          ],
                          meta=nil),
                      ],
                      meta=i.Meta(mid242, 13)),
                    then=i.Const(nil),
                    els=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=nil),
                        i.Invoke(args=[
                          i.Const(code.intern_var(u"pixie.stdlib", u"array")),                          i.Const(kw(u"pixie.stdlib/AssertionException")),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"str"), meta=nil),
                              i.Const(rt.wrap(u"Assert failed: ")),
                              i.Const(rt.wrap(u"Can't pop an empty vector")),
                            ],
                            meta=nil),
                          ]),
                      ],
                      meta=nil),
                    meta=i.Meta(mid242, 5)),
                  i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"=="), meta=i.Meta(mid243, 10)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                            i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                            i.Const(kw(u"cnt")),
                          ],
                          meta=nil),
                        i.Const(rt.wrap(1)),
                      ],
                      meta=i.Meta(mid243, 9)),
                    then=i.VDeref(code.intern_var(u"pixie.stdlib", u"EMPTY"), meta=i.Meta(mid244, 7)),
                    els=i.If(
                      test=i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid245, 12)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid245, 15)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                  i.Const(kw(u"cnt")),
                                ],
                                meta=nil),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"tailoff"), meta=i.Meta(mid245, 22)),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid245, 30)),
                                ],
                                meta=i.Meta(mid245, 21)),
                            ],
                            meta=i.Meta(mid245, 14)),
                          i.Const(rt.wrap(1)),
                        ],
                        meta=i.Meta(mid245, 11)),
                      then=i.Let(names=[kw(u"size"),kw(u"new-tail")],
                      bindings=[
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid246, 21)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid246, 26)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                    i.Const(kw(u"tail")),
                                  ],
                                  meta=nil),
                              ],
                              meta=i.Meta(mid246, 25)),
                          ],
                          meta=i.Meta(mid246, 20)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"array-resize"), meta=i.Meta(mid247, 25)),
                            i.Lookup(kw(u"size"), meta=i.Meta(mid247, 38)),
                          ],
                          meta=i.Meta(mid247, 24)),
                        ],
                        body=i.TailCall(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid248, 12)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid248, 32)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                    i.Const(kw(u"cnt")),
                                  ],
                                  meta=nil),
                              ],
                              meta=i.Meta(mid248, 31)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                i.Const(kw(u"shift")),
                              ],
                              meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                i.Const(kw(u"root")),
                              ],
                              meta=nil),
                            i.Lookup(kw(u"new-tail"), meta=i.Meta(mid249, 31)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                i.Const(kw(u"meta")),
                              ],
                              meta=nil),
                          ],
                          meta=i.Meta(mid248, 11)),
                        meta=i.Meta(mid246, 9)),
                      els=i.Let(names=[kw(u"new-tail"),kw(u"new-root")],
                      bindings=[
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"array-for"), meta=i.Meta(mid250, 25)),
                            i.Lookup(kw(u"this"), meta=i.Meta(mid250, 35)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid250, 41)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                    i.Const(kw(u"cnt")),
                                  ],
                                  meta=nil),
                                i.Const(rt.wrap(2)),
                              ],
                              meta=i.Meta(mid250, 40)),
                          ],
                          meta=i.Meta(mid250, 24)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"pop-tail"), meta=i.Meta(mid251, 25)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                i.Const(kw(u"shift")),
                              ],
                              meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                i.Const(kw(u"root")),
                              ],
                              meta=nil),
                          ],
                          meta=i.Meta(mid251, 24)),
                        ],
                        body=i.If(
                          test=i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"nil?"), meta=i.Meta(mid252, 14)),
                              i.Lookup(kw(u"new-root"), meta=i.Meta(mid252, 19)),
                            ],
                            meta=i.Meta(mid252, 13)),
                          then=i.TailCall(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersisentVector"), meta=i.Meta(mid253, 14)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid253, 33)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                      i.Const(kw(u"cnt")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid253, 32)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                  i.Const(kw(u"shift")),
                                ],
                                meta=nil),
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"EMPTY-NODE"), meta=i.Meta(mid254, 32)),
                              i.Lookup(kw(u"new-tail"), meta=i.Meta(mid255, 32)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                  i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                  i.Const(kw(u"meta")),
                                ],
                                meta=nil),
                            ],
                            meta=i.Meta(mid253, 13)),
                          els=i.If(
                            test=i.If(
                              test=i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid256, 19)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                      i.Const(kw(u"shift")),
                                    ],
                                    meta=nil),
                                  i.Const(rt.wrap(5)),
                                ],
                                meta=i.Meta(mid256, 18)),
                              then=i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"nil?"), meta=i.Meta(mid257, 19)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid257, 25)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                                          i.Lookup(kw(u"new-root"), meta=i.Meta(mid257, 39)),
                                          i.Const(kw(u"array")),
                                        ],
                                        meta=i.Meta(mid257, 30)),
                                      i.Const(rt.wrap(1)),
                                    ],
                                    meta=i.Meta(mid257, 24)),
                                ],
                                meta=i.Meta(mid257, 18)),
                              els=i.Const(nil),
                              meta=i.Meta(mid256, 13)),
                            then=i.TailCall(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid258, 14)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid258, 34)),
                                    i.Invoke(
                                      args=[
                                        i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                        i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                        i.Const(kw(u"cnt")),
                                      ],
                                      meta=nil),
                                  ],
                                  meta=i.Meta(mid258, 33)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid259, 34)),
                                    i.Invoke(
                                      args=[
                                        i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                        i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                        i.Const(kw(u"shift")),
                                      ],
                                      meta=nil),
                                    i.Const(rt.wrap(5)),
                                  ],
                                  meta=i.Meta(mid259, 33)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid260, 34)),
                                    i.Invoke(
                                      args=[
                                        i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                                        i.Lookup(kw(u"new-root"), meta=i.Meta(mid260, 48)),
                                        i.Const(kw(u"array")),
                                      ],
                                      meta=i.Meta(mid260, 39)),
                                    i.Const(rt.wrap(0)),
                                  ],
                                  meta=i.Meta(mid260, 33)),
                                i.Lookup(kw(u"new-tail"), meta=i.Meta(mid261, 33)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                    i.Const(kw(u"meta")),
                                  ],
                                  meta=nil),
                              ],
                              meta=i.Meta(mid258, 13)),
                            els=i.If(
                              test=i.Const(kw(u"else")),
                              then=i.TailCall(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid262, 14)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid262, 34)),
                                      i.Invoke(
                                        args=[
                                          i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                          i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                          i.Const(kw(u"cnt")),
                                        ],
                                        meta=nil),
                                    ],
                                    meta=i.Meta(mid262, 33)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                      i.Const(kw(u"shift")),
                                    ],
                                    meta=nil),
                                  i.Lookup(kw(u"new-root"), meta=i.Meta(mid263, 33)),
                                  i.Lookup(kw(u"new-tail"), meta=i.Meta(mid264, 33)),
                                  i.Invoke(
                                    args=[
                                      i.VDeref(code.intern_var(u"pixie.stdlib", u"get-field"), meta=nil),
                                      i.Lookup(kw(u"this"), meta=i.Meta(mid241, 10)),
                                      i.Const(kw(u"meta")),
                                    ],
                                    meta=nil),
                                ],
                                meta=i.Meta(mid262, 13)),
                              els=i.Const(nil),
                              meta=nil),
                            meta=nil),
                          meta=i.Meta(mid265, 11)),
                        meta=i.Meta(mid250, 9)),
                      meta=i.Meta(mid245, 7)),
                    meta=i.Meta(mid243, 5)),
                ],
              meta=nil),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid203, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/push-tail)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"push-tail")),
      i.Fn(args=[kw(u"this"),kw(u"level"),kw(u"parent"),kw(u"tail-node")],name=kw(u"push-tail"),
        body=i.Let(names=[kw(u"subidx"),kw(u"ret-array"),kw(u"node-to-insert")],
        bindings=[
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-and"), meta=i.Meta(mid266, 17)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-right"), meta=i.Meta(mid266, 26)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid266, 43)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                          i.Lookup(kw(u"this"), meta=i.Meta(mid266, 54)),
                          i.Const(kw(u"cnt")),
                        ],
                        meta=i.Meta(mid266, 47)),
                    ],
                    meta=i.Meta(mid266, 42)),
                  i.Lookup(kw(u"level"), meta=i.Meta(mid266, 61)),
                ],
                meta=i.Meta(mid266, 25)),
              i.Const(rt.wrap(31)),
            ],
            meta=i.Meta(mid266, 16)),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"array-clone"), meta=i.Meta(mid267, 20)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                  i.Lookup(kw(u"parent"), meta=i.Meta(mid267, 41)),
                  i.Const(kw(u"array")),
                ],
                meta=i.Meta(mid267, 32)),
            ],
            meta=i.Meta(mid267, 19)),
          i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid268, 29)),
                i.Lookup(kw(u"level"), meta=i.Meta(mid268, 31)),
                i.Const(rt.wrap(5)),
              ],
              meta=i.Meta(mid268, 28)),
            then=i.Lookup(kw(u"tail-node"), meta=i.Meta(mid269, 26)),
            els=i.Let(names=[kw(u"child")],
            bindings=[
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid270, 39)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                      i.Lookup(kw(u"parent"), meta=i.Meta(mid270, 53)),
                      i.Const(kw(u"array")),
                    ],
                    meta=i.Meta(mid270, 44)),
                  i.Lookup(kw(u"subidx"), meta=i.Meta(mid270, 61)),
                ],
                meta=i.Meta(mid270, 38)),
              ],
              body=i.If(
                test=i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid271, 33)),
                    i.Lookup(kw(u"child"), meta=i.Meta(mid271, 35)),
                    i.Const(nil),
                  ],
                  meta=i.Meta(mid271, 32)),
                then=i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"new-path"), meta=i.Meta(mid272, 31)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                            i.Lookup(kw(u"this"), meta=i.Meta(mid272, 56)),
                            i.Const(kw(u"root")),
                          ],
                          meta=i.Meta(mid272, 48)),
                        i.Const(kw(u"edit")),
                      ],
                      meta=i.Meta(mid272, 40)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid273, 41)),
                        i.Lookup(kw(u"level"), meta=i.Meta(mid273, 43)),
                        i.Const(rt.wrap(5)),
                      ],
                      meta=i.Meta(mid273, 40)),
                    i.Lookup(kw(u"tail-node"), meta=i.Meta(mid274, 40)),
                  ],
                  meta=i.Meta(mid272, 30)),
                els=i.Invoke(
                  args=[
                    i.Lookup(kw(u"push-tail"), meta=i.Meta(mid275, 31)),
                    i.Lookup(kw(u"this"), meta=i.Meta(mid275, 41)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid276, 42)),
                        i.Lookup(kw(u"level"), meta=i.Meta(mid276, 44)),
                        i.Const(rt.wrap(5)),
                      ],
                      meta=i.Meta(mid276, 41)),
                    i.Lookup(kw(u"child"), meta=i.Meta(mid277, 41)),
                    i.Lookup(kw(u"tail-node"), meta=i.Meta(mid278, 41)),
                  ],
                  meta=i.Meta(mid275, 30)),
                meta=i.Meta(mid271, 28)),
              meta=i.Meta(mid270, 26)),
            meta=i.Meta(mid268, 24)),
          ],
          body=i.Do(
            args=[
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid279, 6)),
                  i.Lookup(kw(u"ret-array"), meta=i.Meta(mid279, 11)),
                  i.Lookup(kw(u"subidx"), meta=i.Meta(mid279, 21)),
                  i.Lookup(kw(u"node-to-insert"), meta=i.Meta(mid279, 28)),
                ],
                meta=i.Meta(mid279, 5)),
              i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"->Node"), meta=i.Meta(mid280, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                      i.Lookup(kw(u"parent"), meta=i.Meta(mid280, 21)),
                      i.Const(kw(u"edit")),
                    ],
                    meta=i.Meta(mid280, 13)),
                  i.Lookup(kw(u"ret-array"), meta=i.Meta(mid280, 29)),
                ],
                meta=i.Meta(mid280, 5)),
            ],
          meta=nil),
          meta=i.Meta(mid266, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/pop-tail)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"pop-tail")),
      i.Fn(args=[kw(u"this"),kw(u"level"),kw(u"node")],name=kw(u"pop-tail"),
        body=i.Let(names=[kw(u"sub-idx")],
        bindings=[
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-and"), meta=i.Meta(mid281, 18)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"bit-shift-right"), meta=i.Meta(mid281, 27)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"dec"), meta=i.Meta(mid281, 44)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                          i.Const(kw(u"cnt")),
                        ],
                        meta=i.Meta(mid281, 48)),
                    ],
                    meta=i.Meta(mid281, 43)),
                  i.Lookup(kw(u"level"), meta=i.Meta(mid281, 57)),
                ],
                meta=i.Meta(mid281, 26)),
              i.Const(rt.wrap(31)),
            ],
            meta=i.Meta(mid281, 17)),
          ],
          body=i.If(
            test=i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u">"), meta=i.Meta(mid282, 8)),
                i.Lookup(kw(u"level"), meta=i.Meta(mid282, 10)),
                i.Const(rt.wrap(5)),
              ],
              meta=i.Meta(mid282, 7)),
            then=i.Let(names=[kw(u"new-child")],
            bindings=[
              i.Invoke(
                args=[
                  i.Lookup(kw(u"pop-tail"), meta=i.Meta(mid283, 24)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid283, 34)),
                      i.Lookup(kw(u"level"), meta=i.Meta(mid283, 36)),
                      i.Const(rt.wrap(5)),
                    ],
                    meta=i.Meta(mid283, 33)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid284, 34)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                          i.Lookup(kw(u"node"), meta=i.Meta(mid284, 48)),
                          i.Const(kw(u"array")),
                        ],
                        meta=i.Meta(mid284, 39)),
                      i.Lookup(kw(u"sub-idx"), meta=i.Meta(mid284, 54)),
                    ],
                    meta=i.Meta(mid284, 33)),
                ],
                meta=i.Meta(mid283, 23)),
              ],
              body=i.If(
                test=i.Let(names=[kw(u"r#__gensym_320")],
                bindings=[
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"nil?"), meta=i.Meta(mid285, 18)),
                      i.Lookup(kw(u"new-child"), meta=i.Meta(mid285, 23)),
                    ],
                    meta=i.Meta(mid285, 17)),
                  ],
                  body=i.If(
                    test=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                    then=i.Lookup(kw(u"r#__gensym_320"), meta=nil),
                    els=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid286, 18)),
                        i.Lookup(kw(u"sub-idx"), meta=i.Meta(mid286, 20)),
                        i.Const(rt.wrap(0)),
                      ],
                      meta=i.Meta(mid286, 17)),
                    meta=nil),
                  meta=i.Meta(mid285, 13)),
                then=i.Const(nil),
                els=i.Let(names=[kw(u"root"),kw(u"ret")],
                bindings=[
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                      i.Lookup(kw(u"this"), meta=i.Meta(mid287, 30)),
                      i.Const(kw(u"root")),
                    ],
                    meta=i.Meta(mid287, 22)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"->Node"), meta=i.Meta(mid288, 22)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                          i.Lookup(kw(u"root"), meta=i.Meta(mid288, 37)),
                          i.Const(kw(u"edit")),
                        ],
                        meta=i.Meta(mid288, 29)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                          i.Lookup(kw(u"node"), meta=i.Meta(mid289, 38)),
                          i.Const(kw(u"array")),
                        ],
                        meta=i.Meta(mid289, 29)),
                    ],
                    meta=i.Meta(mid288, 21)),
                  ],
                  body=i.Do(
                    args=[
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid290, 14)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                              i.Lookup(kw(u"ret"), meta=i.Meta(mid290, 28)),
                              i.Const(kw(u"array")),
                            ],
                            meta=i.Meta(mid290, 19)),
                          i.Lookup(kw(u"sub-idx"), meta=i.Meta(mid290, 33)),
                          i.Lookup(kw(u"new-child"), meta=i.Meta(mid290, 41)),
                        ],
                        meta=i.Meta(mid290, 13)),
                      i.Lookup(kw(u"ret"), meta=i.Meta(mid291, 13)),
                    ],
                  meta=nil),
                  meta=i.Meta(mid287, 11)),
                meta=i.Meta(mid285, 9)),
              meta=i.Meta(mid283, 7)),
            els=i.If(
              test=i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid292, 8)),
                  i.Lookup(kw(u"sub-idx"), meta=i.Meta(mid292, 10)),
                  i.Const(rt.wrap(0)),
                ],
                meta=i.Meta(mid292, 7)),
              then=i.Const(nil),
              els=i.If(
                test=i.Const(kw(u"else")),
                then=i.Let(names=[kw(u"root"),kw(u"ret")],
                bindings=[
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                      i.Lookup(kw(u"this"), meta=i.Meta(mid293, 26)),
                      i.Const(kw(u"root")),
                    ],
                    meta=i.Meta(mid293, 18)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"->Node"), meta=i.Meta(mid294, 18)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                          i.Lookup(kw(u"root"), meta=i.Meta(mid294, 33)),
                          i.Const(kw(u"edit")),
                        ],
                        meta=i.Meta(mid294, 25)),
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"aclone"), meta=i.Meta(mid295, 26)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                              i.Lookup(kw(u"node"), meta=i.Meta(mid295, 42)),
                              i.Const(kw(u"array")),
                            ],
                            meta=i.Meta(mid295, 33)),
                        ],
                        meta=i.Meta(mid295, 25)),
                    ],
                    meta=i.Meta(mid294, 17)),
                  ],
                  body=i.Do(
                    args=[
                      i.Invoke(
                        args=[
                          i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid296, 10)),
                          i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                              i.Lookup(kw(u"ret"), meta=i.Meta(mid296, 24)),
                              i.Const(kw(u"array")),
                            ],
                            meta=i.Meta(mid296, 15)),
                          i.Const(nil),
                        ],
                        meta=i.Meta(mid296, 9)),
                      i.Lookup(kw(u"ret"), meta=i.Meta(mid297, 9)),
                    ],
                  meta=nil),
                  meta=i.Meta(mid293, 7)),
                els=i.Const(nil),
                meta=nil),
              meta=nil),
            meta=i.Meta(mid298, 5)),
          meta=i.Meta(mid281, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/new-path)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"new-path")),
      i.Fn(args=[kw(u"edit"),kw(u"level"),kw(u"node")],name=kw(u"new-path"),
        body=i.If(
          test=i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid299, 8)),
              i.Lookup(kw(u"level"), meta=i.Meta(mid299, 10)),
              i.Const(rt.wrap(0)),
            ],
            meta=i.Meta(mid299, 7)),
          then=i.Lookup(kw(u"node"), meta=i.Meta(mid300, 5)),
          els=i.Let(names=[kw(u"nnode")],
          bindings=[
            i.Invoke(
              args=[
                i.VDeref(code.intern_var(u"pixie.stdlib", u"new-node"), meta=i.Meta(mid301, 18)),
                i.Lookup(kw(u"edit"), meta=i.Meta(mid301, 27)),
              ],
              meta=i.Meta(mid301, 17)),
            ],
            body=i.Do(
              args=[
                i.Invoke(
                  args=[
                    i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid302, 8)),
                    i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                        i.Lookup(kw(u"nnode"), meta=i.Meta(mid302, 22)),
                        i.Const(kw(u"array")),
                      ],
                      meta=i.Meta(mid302, 13)),
                    i.Const(rt.wrap(0)),
                    i.Invoke(
                      args=[
                        i.Lookup(kw(u"new-path"), meta=i.Meta(mid302, 32)),
                        i.Lookup(kw(u"edit"), meta=i.Meta(mid302, 41)),
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"-"), meta=i.Meta(mid302, 47)),
                            i.Lookup(kw(u"level"), meta=i.Meta(mid302, 49)),
                            i.Const(rt.wrap(5)),
                          ],
                          meta=i.Meta(mid302, 46)),
                        i.Lookup(kw(u"node"), meta=i.Meta(mid302, 58)),
                      ],
                      meta=i.Meta(mid302, 31)),
                  ],
                  meta=i.Meta(mid302, 7)),
                i.Lookup(kw(u"nnode"), meta=i.Meta(mid303, 7)),
              ],
            meta=nil),
            meta=i.Meta(mid301, 5)),
          meta=i.Meta(mid299, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/EMPTY)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"EMPTY")),
      i.Invoke(
        args=[
          i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid304, 13)),
          i.Const(rt.wrap(0)),
          i.Const(rt.wrap(5)),
          i.VDeref(code.intern_var(u"pixie.stdlib", u"EMPTY-NODE"), meta=i.Meta(mid304, 36)),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"array"), meta=i.Meta(mid304, 48)),
              i.Const(rt.wrap(0)),
            ],
            meta=i.Meta(mid304, 47)),
          i.Const(nil),
        ],
        meta=i.Meta(mid304, 12))]),
    i.Invoke(args=[
# (def pixie.stdlib/vector-from-array)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"vector-from-array")),
      i.Fn(args=[kw(u"arr")],name=kw(u"vector-from-array"),
        body=i.If(
          test=i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid305, 8)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid305, 11)),
                  i.Lookup(kw(u"arr"), meta=i.Meta(mid305, 17)),
                ],
                meta=i.Meta(mid305, 10)),
              i.Const(rt.wrap(32)),
            ],
            meta=i.Meta(mid305, 7)),
          then=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"->PersistentVector"), meta=i.Meta(mid306, 6)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid306, 26)),
                  i.Lookup(kw(u"arr"), meta=i.Meta(mid306, 32)),
                ],
                meta=i.Meta(mid306, 25)),
              i.Const(rt.wrap(5)),
              i.VDeref(code.intern_var(u"pixie.stdlib", u"EMPTY-NODE"), meta=i.Meta(mid306, 39)),
              i.Lookup(kw(u"arr"), meta=i.Meta(mid306, 50)),
              i.Const(nil),
            ],
            meta=i.Meta(mid306, 5)),
          els=i.TailCall(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"into"), meta=i.Meta(mid307, 6)),
              i.Invoke(args=[
                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                ]),
              i.Lookup(kw(u"arr"), meta=i.Meta(mid307, 14)),
            ],
            meta=i.Meta(mid307, 5)),
          meta=i.Meta(mid305, 3)),
      )]),
    i.Do(
      args=[
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-reduce"), meta=i.Meta(mid308, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Array"), meta=i.Meta(mid309, 14)),
            i.Fn(args=[kw(u"this"),kw(u"f"),kw(u"init")],name=kw(u"fn_564"),
              body=i.Let(names=[kw(u"idx"),kw(u"acc")],
              bindings=[
                i.Const(rt.wrap(0)),
                i.Lookup(kw(u"init"), meta=i.Meta(mid310, 16)),
                ],
                body=i.TailCall(
                  args=[
                    i.Fn(args=[kw(u"idx"),kw(u"acc")],name=kw(u"pixie.compiler/__loop__fn__"),closed_overs=[kw(u"this"),kw(u"f")],
                      body=i.Let(names=[kw(u"idx"),kw(u"acc")],
                      bindings=[
                        i.Lookup(kw(u"idx"), meta=i.Meta(mid311, 12)),
                        i.Lookup(kw(u"acc"), meta=i.Meta(mid310, 12)),
                        ],
                        body=i.If(
                          test=i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"reduced?"), meta=i.Meta(mid312, 12)),
                              i.Lookup(kw(u"acc"), meta=i.Meta(mid312, 21)),
                            ],
                            meta=i.Meta(mid312, 11)),
                          then=i.TailCall(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"-deref"), meta=nil),
                              i.Lookup(kw(u"acc"), meta=i.Meta(mid313, 10)),
                            ],
                            meta=i.Meta(mid313, 9)),
                          els=i.If(
                            test=i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid314, 14)),
                                i.Lookup(kw(u"idx"), meta=i.Meta(mid314, 16)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid314, 21)),
                                    i.Lookup(kw(u"this"), meta=i.Meta(mid314, 27)),
                                  ],
                                  meta=i.Meta(mid314, 20)),
                              ],
                              meta=i.Meta(mid314, 13)),
                            then=i.TailCall(
                              args=[
                                i.Lookup(kw(u"pixie.compiler/__loop__fn__"), meta=nil),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid315, 19)),
                                    i.Lookup(kw(u"idx"), meta=i.Meta(mid315, 23)),
                                  ],
                                  meta=i.Meta(mid315, 18)),
                                i.Invoke(
                                  args=[
                                    i.Lookup(kw(u"f"), meta=i.Meta(mid316, 19)),
                                    i.Lookup(kw(u"acc"), meta=i.Meta(mid316, 21)),
                                    i.Invoke(
                                      args=[
                                        i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid316, 26)),
                                        i.Lookup(kw(u"this"), meta=i.Meta(mid316, 31)),
                                        i.Lookup(kw(u"idx"), meta=i.Meta(mid316, 36)),
                                      ],
                                      meta=i.Meta(mid316, 25)),
                                  ],
                                  meta=i.Meta(mid316, 18)),
                              ],
                              meta=nil),
                            els=i.Lookup(kw(u"acc"), meta=i.Meta(mid317, 11)),
                            meta=i.Meta(mid314, 9)),
                          meta=i.Meta(mid312, 7)),
                        meta=nil),
                    ),
                    i.Lookup(kw(u"idx"), meta=i.Meta(mid311, 12)),
                    i.Lookup(kw(u"acc"), meta=i.Meta(mid310, 12)),
                  ],
                  meta=nil),
                meta=i.Meta(mid311, 5)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-count"), meta=i.Meta(mid318, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Array"), meta=i.Meta(mid309, 14)),
            i.Fn(args=[kw(u"arr")],name=kw(u"fn_568"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"-get-field"), meta=i.Meta(mid188, 37)),
                  i.Lookup(kw(u"arr"), meta=i.Meta(mid319, 21)),
                  i.Const(kw(u"count")),
                ],
                meta=i.Meta(mid319, 12)),
            ),
          ],
          meta=nil),
        i.Invoke(
          args=[
            i.VDeref(code.intern_var(u"pixie.stdlib", u"extend"), meta=nil),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"-conj"), meta=i.Meta(mid320, 4)),
            i.VDeref(code.intern_var(u"pixie.stdlib", u"Array"), meta=i.Meta(mid309, 14)),
            i.Fn(args=[kw(u"arr"),kw(u"itm")],name=kw(u"fn_560"),
              body=i.TailCall(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"conj"), meta=i.Meta(mid321, 6)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"vector-from-array"), meta=i.Meta(mid321, 12)),
                      i.Lookup(kw(u"arr"), meta=i.Meta(mid321, 30)),
                    ],
                    meta=i.Meta(mid321, 11)),
                  i.Lookup(kw(u"itm"), meta=i.Meta(mid321, 35)),
                ],
                meta=i.Meta(mid321, 5)),
            ),
          ],
          meta=nil),
      ],
    meta=i.Meta(mid309, 1)),
    i.Invoke(args=[
# (def pixie.stdlib/array-copy)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"array-copy")),
      i.Fn(args=[kw(u"from"),kw(u"from-idx"),kw(u"to"),kw(u"to-idx"),kw(u"size")],name=kw(u"array-copy"),
        body=i.Let(names=[kw(u"idx")],
        bindings=[
          i.Const(rt.wrap(0)),
          ],
          body=i.TailCall(
            args=[
              i.Fn(args=[kw(u"idx")],name=kw(u"pixie.compiler/__loop__fn__"),closed_overs=[kw(u"size"),kw(u"from-idx"),kw(u"to"),kw(u"to-idx"),kw(u"from")],
                body=i.Let(names=[kw(u"idx")],
                bindings=[
                  i.Lookup(kw(u"idx"), meta=i.Meta(mid322, 10)),
                  ],
                  body=i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"<"), meta=i.Meta(mid323, 12)),
                        i.Lookup(kw(u"idx"), meta=i.Meta(mid323, 14)),
                        i.Lookup(kw(u"size"), meta=i.Meta(mid323, 18)),
                      ],
                      meta=i.Meta(mid323, 11)),
                    then=i.Do(
                      args=[
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid324, 12)),
                            i.Lookup(kw(u"to"), meta=i.Meta(mid324, 17)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid324, 21)),
                                i.Lookup(kw(u"to-idx"), meta=i.Meta(mid324, 23)),
                                i.Lookup(kw(u"idx"), meta=i.Meta(mid324, 30)),
                              ],
                              meta=i.Meta(mid324, 20)),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"aget"), meta=i.Meta(mid324, 36)),
                                i.Lookup(kw(u"from"), meta=i.Meta(mid324, 41)),
                                i.Invoke(
                                  args=[
                                    i.VDeref(code.intern_var(u"pixie.stdlib", u"+"), meta=i.Meta(mid324, 47)),
                                    i.Lookup(kw(u"from-idx"), meta=i.Meta(mid324, 49)),
                                    i.Lookup(kw(u"idx"), meta=i.Meta(mid324, 58)),
                                  ],
                                  meta=i.Meta(mid324, 46)),
                              ],
                              meta=i.Meta(mid324, 35)),
                          ],
                          meta=i.Meta(mid324, 11)),
                        i.TailCall(
                          args=[
                            i.Lookup(kw(u"pixie.compiler/__loop__fn__"), meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid325, 19)),
                                i.Lookup(kw(u"idx"), meta=i.Meta(mid325, 23)),
                              ],
                              meta=i.Meta(mid325, 18)),
                          ],
                          meta=nil),
                      ],
                    meta=i.Meta(mid324, 7)),
                    els=i.Const(nil),
                    meta=i.Meta(mid323, 5)),
                  meta=nil),
              ),
              i.Lookup(kw(u"idx"), meta=i.Meta(mid322, 10)),
            ],
            meta=nil),
          meta=i.Meta(mid322, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/array-append)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"array-append")),
      i.Fn(args=[kw(u"arr"),kw(u"val")],name=kw(u"array-append"),
        body=i.Let(names=[kw(u"new-array")],
        bindings=[
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"make-array"), meta=i.Meta(mid326, 20)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=i.Meta(mid326, 32)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid326, 37)),
                      i.Lookup(kw(u"arr"), meta=i.Meta(mid326, 43)),
                    ],
                    meta=i.Meta(mid326, 36)),
                ],
                meta=i.Meta(mid326, 31)),
            ],
            meta=i.Meta(mid326, 19)),
          ],
          body=i.Do(
            args=[
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"array-copy"), meta=i.Meta(mid327, 6)),
                  i.Lookup(kw(u"arr"), meta=i.Meta(mid327, 17)),
                  i.Const(rt.wrap(0)),
                  i.Lookup(kw(u"new-array"), meta=i.Meta(mid327, 23)),
                  i.Const(rt.wrap(0)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid327, 36)),
                      i.Lookup(kw(u"arr"), meta=i.Meta(mid327, 42)),
                    ],
                    meta=i.Meta(mid327, 35)),
                ],
                meta=i.Meta(mid327, 5)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"aset"), meta=i.Meta(mid328, 6)),
                  i.Lookup(kw(u"new-array"), meta=i.Meta(mid328, 11)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid328, 22)),
                      i.Lookup(kw(u"arr"), meta=i.Meta(mid328, 28)),
                    ],
                    meta=i.Meta(mid328, 21)),
                  i.Lookup(kw(u"val"), meta=i.Meta(mid328, 33)),
                ],
                meta=i.Meta(mid328, 5)),
              i.Lookup(kw(u"new-array"), meta=i.Meta(mid329, 5)),
            ],
          meta=nil),
          meta=i.Meta(mid326, 3)),
      )]),
    i.Invoke(args=[
# (def pixie.stdlib/array-clone)
      i.Const(code.intern_var(u"pixie.stdlib", u"set-var-root!")),
      i.Const(code.intern_var(u"pixie.stdlib",u"array-clone")),
      i.Fn(args=[kw(u"arr")],name=kw(u"array-clone"),
        body=i.Let(names=[kw(u"new-array")],
        bindings=[
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"make-array"), meta=i.Meta(mid330, 20)),
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid330, 32)),
                  i.Lookup(kw(u"arr"), meta=i.Meta(mid330, 38)),
                ],
                meta=i.Meta(mid330, 31)),
            ],
            meta=i.Meta(mid330, 19)),
          ],
          body=i.Do(
            args=[
              i.Invoke(
                args=[
                  i.VDeref(code.intern_var(u"pixie.stdlib", u"array-copy"), meta=i.Meta(mid331, 6)),
                  i.Lookup(kw(u"arr"), meta=i.Meta(mid331, 17)),
                  i.Const(rt.wrap(0)),
                  i.Lookup(kw(u"new-array"), meta=i.Meta(mid331, 23)),
                  i.Const(rt.wrap(0)),
                  i.Invoke(
                    args=[
                      i.VDeref(code.intern_var(u"pixie.stdlib", u"count"), meta=i.Meta(mid331, 36)),
                      i.Lookup(kw(u"arr"), meta=i.Meta(mid331, 42)),
                    ],
                    meta=i.Meta(mid331, 35)),
                ],
                meta=i.Meta(mid331, 5)),
              i.Lookup(kw(u"new-array"), meta=i.Meta(mid332, 5)),
            ],
          meta=nil),
          meta=i.Meta(mid330, 3)),
      )]),
    i.Let(names=[kw(u"MAX"),kw(u"v")],
    bindings=[
      i.Const(rt.wrap(1024)),
      i.Invoke(
        args=[
          i.VDeref(code.intern_var(u"pixie.stdlib", u"into"), meta=i.Meta(mid333, 10)),
          i.Invoke(args=[
            i.Const(code.intern_var(u"pixie.stdlib", u"array")),            ]),
          i.Invoke(
            args=[
              i.VDeref(code.intern_var(u"pixie.stdlib", u"range"), meta=i.Meta(mid333, 19)),
              i.Lookup(kw(u"MAX"), meta=i.Meta(mid333, 25)),
            ],
            meta=i.Meta(mid333, 18)),
        ],
        meta=i.Meta(mid333, 9)),
      ],
      body=i.Let(names=[kw(u"max#__gensym_319")],
      bindings=[
        i.Lookup(kw(u"MAX"), meta=i.Meta(mid334, 15)),
        ],
        body=i.Let(names=[kw(u"x")],
        bindings=[
          i.Const(rt.wrap(0)),
          ],
          body=i.Invoke(
            args=[
              i.Fn(args=[kw(u"x")],name=kw(u"pixie.compiler/__loop__fn__"),closed_overs=[kw(u"v"),kw(u"max#__gensym_319")],
                body=i.Let(names=[kw(u"x")],
                bindings=[
                  i.Lookup(kw(u"x"), meta=i.Meta(mid334, 13)),
                  ],
                  body=i.If(
                    test=i.Invoke(
                      args=[
                        i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=nil),
                        i.Lookup(kw(u"x"), meta=i.Meta(mid334, 13)),
                        i.Lookup(kw(u"max#__gensym_319"), meta=nil),
                      ],
                      meta=nil),
                    then=i.Const(nil),
                    els=i.Do(
                      args=[
                        i.Invoke(
                          args=[
                            i.VDeref(code.intern_var(u"pixie.stdlib", u"println"), meta=i.Meta(mid335, 6)),
                            i.Lookup(kw(u"x"), meta=i.Meta(mid335, 14)),
                          ],
                          meta=i.Meta(mid335, 5)),
                        i.If(
                          test=i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"="), meta=i.Meta(mid336, 14)),
                              i.Lookup(kw(u"x"), meta=i.Meta(mid336, 16)),
                              i.Invoke(
                                args=[
                                  i.VDeref(code.intern_var(u"pixie.stdlib", u"nth"), meta=i.Meta(mid336, 19)),
                                  i.Lookup(kw(u"v"), meta=i.Meta(mid336, 23)),
                                  i.Lookup(kw(u"x"), meta=i.Meta(mid336, 25)),
                                ],
                                meta=i.Meta(mid336, 18)),
                            ],
                            meta=i.Meta(mid336, 13)),
                          then=i.Const(nil),
                          els=i.Invoke(
                            args=[
                              i.VDeref(code.intern_var(u"pixie.stdlib", u"throw"), meta=nil),
                              i.Invoke(args=[
                                i.Const(code.intern_var(u"pixie.stdlib", u"array")),                                i.Const(kw(u"pixie.stdlib/AssertionException")),
                                i.Const(rt.wrap(u"Assert failed")),
                                ]),
                            ],
                            meta=nil),
                          meta=i.Meta(mid336, 5)),
                        i.TailCall(
                          args=[
                            i.Lookup(kw(u"pixie.compiler/__loop__fn__"), meta=nil),
                            i.Invoke(
                              args=[
                                i.VDeref(code.intern_var(u"pixie.stdlib", u"inc"), meta=nil),
                                i.Lookup(kw(u"x"), meta=i.Meta(mid334, 13)),
                              ],
                              meta=nil),
                          ],
                          meta=nil),
                      ],
                    meta=nil),
                    meta=nil),
                  meta=nil),
              ),
              i.Lookup(kw(u"x"), meta=i.Meta(mid334, 13)),
            ],
            meta=nil),
          meta=nil),
        meta=i.Meta(mid334, 3)),
      meta=i.Meta(mid337, 1)),
    i.Const(nil),
  ],
meta=i.Meta(mid338, 1))