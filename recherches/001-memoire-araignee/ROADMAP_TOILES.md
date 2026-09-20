# Roadmap — Les Toiles

Source : `russel-agent/PLAN.md:84-98`

- [x] Toile 1 — SpiderCache : cache RAM des principes L2, `search()` BM25+cosine+score+decay, 1.9ms vs 15-50ms SQLite (10-25x)
- [x] Toile 2 — SpiderWatcher : watch `l2_distilled.db`, auto-refresh, cooldown 5s, watchdog + fallback polling
- [x] Toile 3 — IdleWatcher : détecte inactivité (event_bus), callback background (warmup embeddings), cooldown, 60s seuil dashboard
- [ ] Toile 4 — Weaver : détection liens cross-domaines entre principes, stockage graphe RAM
- [ ] Toile 5 — Hot Cache 2.0 : LRU évolutif (garder N plus utilisés)
- [ ] Toile 6 — Mmap Layer : embeddings en `numpy.memmap` pour réduire RSS
- [ ] Toile 7 — Spider cron : refresh planifié 10-30 min dans scheduler

Ordre conseillé ici : bench Toile 1 proprement → papier draft-001 → puis Toile 4 (vrai apport recherche) → Toile 5/6 (perf) → Toile 7 (ops).
