(ns pixie.tests.test-compare
  (require pixie.test :as t))

(t/deftest test-compare-numbers
  (t/assert= (compare 1   1)  0)
  (t/assert= (compare 1   2) -1)
  (t/assert= (compare 1  -1)  1)
  
  (t/assert= (compare 1    1.0)  0)
  (t/assert= (compare 1.0    1)  0)
  (t/assert= (compare 1.0  2.0) -1)
  (t/assert= (compare 1.0 -1.0)  1)

  (t/assert= (compare 1/2  1/2)  0)
  (t/assert= (compare 1/3  1/2) -1)
  (t/assert= (compare 1/2  1/3)  1))

(t/deftest test-compare-strings
  (t/assert= (compare "a" "a")   0)
  (t/assert= (compare "a" "b")  -1)
  (t/assert= (compare "b" "a")   1)
  
  (t/assert= (compare "aa" "a")   1)
  (t/assert= (compare "a"  "aa")  -1)

  (t/assert= (compare "aa" "b")   -1)
  (t/assert= (compare "b"  "aa")   1)

  (t/assert= (compare "aaaaaaaa" "azaaaaaa") -1)
  (t/assert= (compare "azaaaaaa" "aaaaaaaa")  1))

(t/deftest test-compare-keywords
  (t/assert= (compare :a :a) 0)
  (t/assert= (compare :a :b) -1)
  (t/assert= (compare :b :a) 1)
  (t/assert= (compare :ns/a :ns/a) 0)
  (t/assert= (compare :ns/a :ns/b) -1)
  (t/assert= (compare :a :aa) -1)
  (t/assert= (compare :aa :a) 1))

(t/deftest test-compare-symbols
  (t/assert= (compare 'a 'a) 0)
  (t/assert= (compare 'a 'b) -1)
  (t/assert= (compare 'b 'a) 1)
  (t/assert= (compare 'ns/a 'ns/a) 0)
  (t/assert= (compare 'ns/a 'ns/b) -1)
  (t/assert= (compare 'a 'aa) -1)
  (t/assert= (compare 'aa 'a) 1))

(t/deftest test-compare-vectors
  (t/assert= (compare []    [])    0)
  (t/assert= (compare [1]   []) 1)
  (t/assert= (compare [1] [2]) -1)
  (t/assert= (compare [1 2] [1 3]) -1)
  (t/assert= (compare [:a] [:a]) 0)
  (t/assert= (compare [:a] [:b]) -1)
  (t/assert= (compare [:a] [:a :a]) -1)
  (t/assert= (compare ["a"] ["a"]) 0)
  (t/assert= (compare ["a"] ["a" "b"]) -1))
