# H001 — Compression en notations mathématiques

Ton idée : un principe en phrase prend 30-50 tokens. En notation math ça prend 10-15 et le matching devient plus strict.

Exemple :
- Texte : "Prioriser les pools CLMM avec fee 0.05% quand TVL 4h croît >15% et âge >90 jours"
- Math : `CLMM(f=0.05%) | gTVL4h>15% & age>90j -> prioriser`
- Triples : `(pool, requires, age>90j)`, `(pool, signal, gTVL4h>15%)`

Pourquoi ça peut marcher : moins de bruit lexical pour BM25, vecteurs plus denses pour cosine, moins de tokens injectés dans le prompt agent.

Pourquoi ça peut rater : l'embedder `all-MiniLM-L6-v2` est entraîné sur phrases naturelles, pas sur tes notations. Cosine peut chuter.

Test sans perdre la root :
1. Branche `hyp/H001-math-notation` depuis `main`.
2. Corpus double : 100 principes en texte + leur version math (manuelle ou règle simple).
3. Bench V2 avec `common/bench_harness.py` :
   - tokens moyens (texte vs math)
   - rappel top-5 (requête texte → trouve version math ? et inverse)
   - p50 latence
4. Si tokens -30% à rappel égal ou meilleur → merge. Sinon → H002.

Statut : à tester. Ne touche pas à `main`.
