# Ton idée : transformers et mémoires comme structures math composables

Ce que tu dis : un transformer n'est pas du texte, c'est une fonction `f: tokens -> vecteurs` avec des lois (attention = moyenne pondérée, résiduel = addition, norme = projection). Deux structures qui se parlent sémantiquement = deux fonctions qu'on peut composer, comparer, inverser — pas juste stocker des phrases.

Traduction concrète pour Spider :

1. **Principe = objet typé, pas phrase** : `(sujet, relation, objet)` + type + domaine + score. Tes triples EvolveR sont déjà ça. Ex : `(pool, requires, age>90j)` est un objet qu'on peut croiser avec `(farm, requires, age>30j)` par la relation `requires`, même si les mots diffèrent.
2. **Composition** : `principe A ∘ principe B` = règle combinée (ex : TVL>1M ET âge>30j → reco). Aujourd'hui on ne fait que lister top-5 ; demain on les compose en graphe (Weaver H003) avec des lois (transitivité, contradiction → score baisse).
3. **Objets plus performants** : vecteurs 384 (rapide, flou) → triplets typés (strict, lent) → graphe (raisonnement). Le bon objet dépend de l'étape : vecteur pour retrouver vite, graphe pour raisonner juste.

Nouvelle hypothèse H004 posée dans le ledger : principes stockés en triples typés + composition graphe, bench rappel cross-domain vs texte seul. À tester après H003.
