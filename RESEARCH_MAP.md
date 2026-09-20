# RESEARCH_MAP

| N | Slug | Titre | Statut | Dossier | Papiers |
|---|------|-------|--------|---------|---------|
| 001 | memoire-araignee | Mémoire Araignée — Hot RAM cache + Watchers (La Forme Araignée) | active — Toiles 1-3 faites, 4-7 à faire | `recherches/001-memoire-araignee/` | draft-001 en cours |
| 002 | _à venir_ | _réservé_ | vide | — | — |

## 001 — mémoire-araignée en bref

- Origine : `russel-agent/memory/spider_cache.py:1`, `russel-agent/tests/test_spider_cache.py:1`, `russel-agent/tools/memory_tools.py:189`, `russel-agent/core/dashboard.py:243`, `russel-agent/PLAN.md:84`
- Toile 1 : SpiderCache RAM (<1ms, 10-25x vs SQLite)
- Toile 2 : SpiderWatcher auto-refresh (watchdog + polling fallback)
- Toile 3 : IdleWatcher (warmup background après 60s inactivité)
- Toile 4-7 : Weaver cross-domain, LRU Hot Cache 2.0, Mmap Layer, Spider cron — à faire ici
