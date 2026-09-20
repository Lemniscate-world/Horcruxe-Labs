# Hypothèses — sans perdre la root

Root = `main` (stable, qui compile + benchs verts). On ne touche jamais `main` direct.

Pour chaque idée : 1 dossier `hypotheses/H00X-slug/` + 1 branche `hyp/H00X-slug`.

```
hypotheses/
  README.md           # ce fichier = arbre vivant
  _TEMPLATE.md        # copier pour chaque hypothèse
  H001-math-notation/ # ton idée compression math
  H002-triples-only/
  H003-graph-weaver/
```

Arbre actuel :
- root `main` (Toiles 1-3 stables)
  - `hyp/H001-math-notation` — compresser principes en notations math, moins de tokens, plus facile à matcher ?
  - `hyp/H002-triples-only` — scorer seulement sur triples (s,p,o), pas sur texte ?
  - `hyp/H003-graph-weaver` — graphe cross-domain + PageRank pour retrieval ?

Règles :
1. 1 hypothèse = 1 question falsifiable + 1 métrique (ex : tokens -30% à qualité égale).
2. Baseline toujours re-mesurée sur `main` avant de comparer.
3. On merge dans `main` seulement si bench V2 gagne + tests verts.
4. OpenResearch ou git worktree : 1 worktree par hypothèse pour tester en parallèle sans salir la root.

Voir `_TEMPLATE.md` et `H001-math-notation/README.md`.
