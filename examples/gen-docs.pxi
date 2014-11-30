#!/usr/bin/env pixie-vm

; generate html docs for a given namespace
(ns gen-ns-docs
  (use 'hiccup.core))

(defn munge [nm]
  (-> (str nm)
      (replace "-" "_")
      (replace "?" "")))

(defn generate-docs [ns]
  (html [:html
         [:head
          [:title ns]
          [:meta {:charset "utf-8"}]
          [:style {:type "text/css"}
"
.version {
  color: #aaa;
}
"]]
         [:body
          [:h1 ns]
          (let [syms (ns-map ns)
                infos (transduce (comp (map (fn [sym]
                                              (when-let [info (meta @(resolve-in (the-ns ns) sym))]
                                                (assoc info :name (hiccup.util/escape-html sym)))))
                                       (filter (complement nil?)))
                                 conj
                                 (keys (ns-map ns)))]
            (list [:section
                   [:h2 "Overview"]
                   [:ul
                    (for [{name :name} infos]
                      [:li [:a {:href (str "#" ns "/" name)} (str ns "/" name)]])]]
                  (seq (map (fn [{:keys [name doc signatures added examples]}]
                              [:article
                               [:h2 {:id (str ns "/" name)} name (when added [:span.version (str " (since " added ")")])]
                               (when signatures
                                 [:pre (pr-str (seq signatures))])
                               (when doc
                                 [:pre doc])
                               (when examples
                                 [:section.examples
                                  [:ul
                                   (for [[expr output result] examples]
                                     [:pre (str "user => " expr (as-str output) "\n" (as-str result))])]])])
                            infos))))]]))

(defn main [file ns]
  (load-file file)
  (println (str "<!doctype html>\n" (generate-docs (read-string ns)))))

(if (< (count program-arguments) 2)
  (println "Usage: gen-ns-docs <file> <ns>")
  (let [[file ns] program-arguments]
    (main file ns)))
