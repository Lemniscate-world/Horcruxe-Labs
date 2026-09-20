# Toile 2 & 3 — Watchers

- `SpiderWatcher` (`code/spider_cache.py:253`) : `Observer` watchdog sur dossier parent, `on_modified` si `resolve()==db.resolve()`, cooldown 5s, fallback polling thread 3s.
- `IdleWatcher` (`code/spider_cache.py:436`) : lit `MAX(processed_at, created_at)` depuis `event_bus.db`, seuil 60s dans dashboard (`russel-agent/core/dashboard.py:259`), callback warmup : `sum()` embeddings.
- Singleton : `get_cache()`, `start_watcher()`, `start_idle_watcher()`.

Points recherche : cooldown optimal ? faux refresh SQLite WAL ? inactivité = vraie fenêtre d'optimisation ou juste warmup ? Logger actions_count pour papier.
