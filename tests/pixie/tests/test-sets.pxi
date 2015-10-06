(ns pixie.test.test-sets
  (require pixie.test :as t)
  (require pixie.set :as s))

(t/deftest test-union
  (let [magic #{:bibbidi :bobbidi :boo}
        work #{:got :no :time :to :dilly-dally}
        dreams #{:the :dreams :that :i :wish}
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
