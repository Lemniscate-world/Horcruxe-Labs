# 001 — Mémoire Araignée / La Forme Araignée

Question : comment servir une mémoire d'agent (principes L2) en <1ms sans requêter SQLite à chaque fois, tout en restant fraîche quand la base évolue ?

Hypothèse : charger tout en RAM au démarrage (embeddings décodés une fois), scorer en RAM (BM25 + cosine + score Laplace + decay temporel), et rafraîchir en background via watchers.

## État importé depuis russel-agent (2026-09-20)

- `code/spider_cache.py` — copie exacte de `russel-agent/memory/spider_cache.py`
- `tests/test_spider_cache.py` — copie exacte de `russel-agent/tests/test_spider_cache.py`
- Provenance logique :
  - `russel-agent/tools/memory_tools.py:189` — `search_principles()` avec injection SpiderCache
  - `russel-agent/core/dashboard.py:243` — démarrage watcher + idle warmup
  - `russel-agent/PLAN.md:84` — Phases 11-12, Toiles 1-7

## Ce qu'on fait ici (et pas dans russel-agent)

1. Version labo propre, découplée de l'orchestrateur.
2. Benchs reproductibles pour papier.
3. Toiles 4-7 : Weaver, LRU 2.0, Mmap, Spider cron.
4. Papiers au fur et à mesure dans `papers/`.

Voir `ROADMAP_TOILES.md` et `notes/`.
