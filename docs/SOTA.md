# SOTA — nous vs autres (vitesse + qualité)

Mis à jour par bench, pas par avis. Sources en bas.

| Système | Latence recherche | Candidats vus | Cross-domain | Code ouvert |
|---|---|---|---|---|
| SQLite russel-agent (baseline) | p50 0.082ms (N=2000, LIMIT 50) | 50 | non (`WHERE domain=?`) | oui (ce repo) |
| SpiderCache fair50 (nous) | p50 0.076ms, parité 60/60 | 50 | non (V2) | oui |
| SpiderCache fullscan (nous) | p50 1.69ms (N=2000) | ~1000/domaine | non (V2) | oui |
| SpiderCache annonce d'origine | 1.9ms vs 15-50ms (cas réel avec embeddings) | tout | non | oui |
| MemGPT / Letta (RAG mémoire) | ~50-200ms (LLM + vector DB) | top-k ANN | partiel | oui |
| EvolveR distillation seule | pas de recherche (offline) | — | non | papier 2510.16079 |

Conclusion honnête : à petit N sans embeddings, on n'est PAS plus rapides, on est à égalité fair. Le gain vient avec : decode embedding une fois (pas à chaque fois), gros N, et fullscan exhaustif. Le vrai + à publier = Weaver cross-domain + méthode fair + compression tokens.

## Tracker papiers (R81)

- EvolveR 2510.16079 : distillation trajectoire→principe + triples. On reprend, on ajoute decay + cache.
- Sentence-BERT 1908.10084 : embeddings phrases. On utilise `all-MiniLM-L6-v2`.
- MemGPT : mémoire OS avec pagination. Nous : hot RAM + watchers, pas de pagination.
- Chaque nouveau papier lu → ligne ici + `references/README.md` + `evidence-matrix` (copier `Neural-Research/research/evidence-matrix.csv` quand on l'active).
