# Harness commun

- `bench_harness.py` — `Bench` : `time(label, fn)`, `summary()` (mean/p50/p95), `report(out.json)`. Seed fixe, JSON pour papiers.
- Règle : chaque recherche a son `code/bench_*.py` qui utilise ce harness. Mêmes métriques partout.
- Exemple : `recherches/001-memoire-araignee/code/bench_latency.py` à migrer vers `Bench` en V2.
