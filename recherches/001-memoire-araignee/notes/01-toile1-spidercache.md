# Toile 1 — SpiderCache

Fichier : `code/spider_cache.py:54` (`class SpiderCache`), `search()` ligne 144.

- Load : `SELECT ... FROM principles ORDER BY score DESC`, décode BLOB embedding une fois (`np.frombuffer`), parse `triples_json`, index par domaine.
- Search : `BM25 (overlap mots) + cosine*0.5 + score*0.3*decay(exp(-0.01*days_idle))`, top_k, filtre domaine.
- Perf annoncée russel-agent : 1.9ms vs 15-50ms. À re-bencher ici proprement.
- Limites connues : `WHERE domain=?` = silos, pas de cross-domain ; triples stockés mais non utilisés au retrieval (voir `.full-review/03-qualitative-cognitive.md:365`).

À mesurer pour papier draft-001 : latence p50/p95, RAM vs N principes, hit qualité vs SQLite (même formule → doit être identique), ablation decay/cosine/BM25.
