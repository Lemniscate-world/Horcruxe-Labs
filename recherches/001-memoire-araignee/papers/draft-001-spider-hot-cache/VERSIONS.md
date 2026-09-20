# Versions — draft-001 spider-hot-cache

Chaque version = snapshot daté + chiffres + décision. On ne réécrit jamais l'histoire.

- **v0.1 (2026-09-20)** : outline + bench V1 honnête (x0.68, parité 3/60) + figure embeddings-pca.png. Statut : bench non fair, à refaire.
- **v0.2 (2026-09-20)** : bench V2 fair (`bench_v2.py`, `bench-v2.json`) — parité 60/60, sqlite 0.082ms vs cache fair 0.075ms vs fullscan 1.69ms + chart `bench-v2.png`. Statut : baseline propre.
- **v0.3 (à venir)** : papier 2 pages + Weaver H003 premiers liens cross-domain.

Règle : `vX.Y/` contient `paper.md` figé + `bench-*.json` figé. `outline.md` reste vivant.
