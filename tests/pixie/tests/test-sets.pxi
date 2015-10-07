(ns pixie.test.test-sets
  (require pixie.test :as t)
  (require pixie.set :as s))

(let [magic #{:bibbidi :bobbidi :boo}
      work #{:got :no :time :to :dilly-dally}]

  (t/deftest test-union
    (let [dreams #{:the :dreams :that :i :wish}
          magical-work #{:bibbidi :bobbidi :boo
                         :got :no :time :to :dilly-dally}
          dream-of-magical-work #{:bibbidi :bobbidi :boo
                                  :got :no :time :to :dilly-dally
                                  :the :dreams :that :i :wish}]
      (t/assert= (s/union) #{})
      (t/assert= (s/union magic) magic)
      (t/assert= (s/union magic magic) magic)
      (t/assert= (s/union magic magic magic) magic)
      (t/assert= (s/union magic work) magical-work)
      (t/assert= (s/union work magic) magical-work)
      (t/assert= (s/union magic work dreams) dream-of-magical-work)
      (t/assert-throws? (s/union [:i :only] [:love :sets]))))

  (t/deftest test-difference
    (t/assert= (s/difference) #{})
    (t/assert= (s/difference magic) magic)
    (t/assert= (s/difference magic #{:boo}) #{:bibbidi :bobbidi})
    (t/assert= (s/difference magic work) magic)
    (t/assert= (s/difference magic #{:bibbidi} #{:bobbidi}) #{:boo})
    (t/assert-throws? (s/difference [:i :only] [:love :sets])))

  (t/deftest test-intersection
    (t/assert= (s/intersection) #{})
    (t/assert= (s/intersection magic) magic)
    (t/assert= (s/intersection magic magic) magic)
    (t/assert= (s/intersection magic work) #{})
    (t/assert= (s/intersection magic #{:boo}) #{:boo})
    (t/assert= (s/intersection #{:boo} magic) #{:boo})
    (t/assert= (s/intersection magic #{:bobbidi :boo}) #{:bobbidi :boo})
    (t/assert= (s/intersection magic #{:bibbidi :boo} #{:bobbidi :boo}) #{:boo})
    (t/assert-throws? (s/intersection [:i :only] [:love :sets]))))
