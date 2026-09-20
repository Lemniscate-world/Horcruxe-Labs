# Draft-001 — Spider Hot Cache : outline

Titre provisoire : *Spider Memory : a Hot RAM Cache with Background Watchers for Agent Long-Term Memory*

1. Intro : L2 distillée, coût SQLite+decode+BM25/cosine à chaque appel.
2. Méthode :
   - Load full-RAM + decode une fois + index domaine
   - Scoring `BM25 + 0.5*cosine + 0.3*score*exp(-0.01*idle)`
   - Watcher FS + idle warmup
3. Expés à faire :
   - latence p50/p95 vs SQLite (N=100,1k,10k)
   - RAM vs N
   - parité qualité (même formule)
   - ablation BM25/cosine/decay
4. Related : EvolveR distillation, Obsidian 3-layer memory, hybrid search BM25+vector.
5. Limites : silos domaines, triples non utilisés (→ Toile 4).

Fichiers à ajouter : `paper.md`, `figures/`, `refs.bib`, `NOTES.md`.
