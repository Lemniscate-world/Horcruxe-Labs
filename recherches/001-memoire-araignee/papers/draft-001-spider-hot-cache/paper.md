# Draft-001 — Spider Memory: Hot RAM Cache with Background Watchers (2 pages)

## Abstract

Agent long-term memory (distilled L2 principles) is usually served from SQLite per query: reopen, decode embeddings, rescore. We load everything once in RAM (SpiderCache), refresh in background (SpiderWatcher, IdleWatcher), and report honest numbers: fair 50-vs-50 parity 60/60 at equal speed (0.076 vs 0.082ms p50, N=2000), fullscan exhaustiveness at 20x cost, and a negative result on hand-written math compression (no token saving under cl100k, 0.98x).

## 1. Problem

`retrieve_relevant` (`memory_agent.py`) scores `BM25 + 0.5*cosine + 0.3*score*decay` over SQLite rows each call. Cost per call: open + `ORDER BY score LIMIT 50` + `np.frombuffer` decode + rescore. Announced pain: 15-50ms in the real loop with embeddings.

## 2. Method

- **Toile 1 — SpiderCache** (`code/spider_cache.py`): full load at boot, one-time BLOB decode, domain index, same formula in RAM.
- **Toile 2 — SpiderWatcher**: watchdog on `l2_distilled.db`, 5s cooldown, polling fallback.
- **Toile 3 — IdleWatcher**: reads `event_bus.db` inactivity, embedding warmup after 60s.
- **Fair bench** (`code/bench_v2.py`, seed 42): same 50 candidates both sides, BM25-only, p50/p95, JSON frozen.

## 3. Results

| Config (N=2000) | p50 | Note |
|---|---|---|
| SQLite LIMIT50 | 0.082ms | baseline |
| Cache fair50 | 0.076ms | parity 60/60 |
| Cache fullscan | 1.69ms | sees ~1000/domain, 20x cost |

Figure `figures/bench-v2.png`. Figure `figures/embeddings-pca.png` (TF-IDF+PCA demo of principle space).

**H001 math compression (negative)**: 12 text↔math pairs, cl100k: 13.6 vs 13.2 tokens (0.98x — symbols cost tokens too), BM25 recall 0/6 both ways on micro-corpus. Conclusion: hand notation needs a real codebook + embedding-side test, not BM25 on 12 items.

## 4. Limits & next

Domain silos (`WHERE domain=?`), triples stored but unused at retrieval, nocturnal distillation on empty steps. Next: Toile 4 Weaver cross-domain (`code/weaver.py`) measured, H001 with codebook + cosine recall.

Code MIT, text CC-BY-4.0. Bench JSON: `bench-v2.json`, `benchmarks/runs/H001.json`.
