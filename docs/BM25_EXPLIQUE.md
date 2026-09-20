# BM25 depuis zéro (tous domaines)

Tu cherches `chat dort`. 3 documents :
- D1 : `chat dort bien`
- D2 : `chien dort bien bien`
- D3 : `soleil quantique`

BM25 = pour chaque mot de ta requête, on compte, puis on pondère.

1. **Compter (TF)** : `chat` apparaît 1x dans D1, 0 ailleurs. `dort` 1x dans D1 et D2.
2. **Rareté (IDF)** : `chat` est rare (1 doc sur 3) → vaut cher. `dort` est commun (2 docs) → vaut moins. `bien` très commun → vaut presque rien.
3. **Longueur** : D2 est plus long, on le pénalise un peu (sinon les pavés gagnent toujours).
4. **Score** = somme sur tes mots. Ici D1 gagne (`chat` rare + `dort`), D2 deuxième, D3 zéro.

Notre version Spider (`code/spider_cache.py:174`) est un BM25 simplifié : proportion de tes mots trouvés dans le principe. Pas d'IDF ni longueur — suffisant à petit N, à améliorer en Toile 5.

Limite : que des mots exacts. `dort` ne matche pas `sommeille`. D'où cosine à côté (même sens, mots différents).
