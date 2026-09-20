"""Bench propre Toile 1 — SpiderCache RAM vs SQLite direct.

Reproductible, seed fixe, sans dépendance lourde.
- Génère une DB L2 synthétique (texte + scores, embeddings NULL -> cosine=0)
- Compare SpiderCache.search() vs requête SQLite directe (même formule)
- Mesure p50/p95/mean, parité qualité, RAM approximative
- Sortie JSON pour papier draft-001

Usage:
  python bench_latency.py --n 500 --queries 50 --seed 42
"""

import argparse
import json
import math
import random
import sqlite3
import statistics
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "spider_cache", str(Path(__file__).parent / "spider_cache.py")
)
spider_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(spider_mod)
SpiderCache = spider_mod.SpiderCache

VOCAB = [
    "slippage", "yield", "pool", "tvl", "arbitrage", "latency", "cache",
    "memory", "consolidation", "principle", "routing", "retrieval",
    "distillation", "trajectory", "policy", "oracle", "signal", "hedge",
]


def make_db(path: Path, n: int, seed: int):
    rnd = random.Random(seed)
    conn = sqlite3.connect(str(path))
    conn.executescript(
        """
        CREATE TABLE principles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            type TEXT,
            domain TEXT,
            score REAL DEFAULT 0.5,
            embedding BLOB,
            triples_json TEXT,
            last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    domains = ["defi_quant", "memory"]
    for i in range(n):
        words = " ".join(rnd.choice(VOCAB) for _ in range(rnd.randint(3, 8)))
        dom = domains[i % 2]
        score = round(rnd.uniform(0.2, 0.9), 3)
        conn.execute(
            "INSERT INTO principles (text, type, domain, score) VALUES (?,?,?,?)",
            (f"{words} {i}", "guiding", dom, score),
        )
    conn.commit()
    conn.close()


def sqlite_search(db: Path, task: str, domain: str, top_k=5):
    """Copie du chemin SQLite de tools/memory_tools.py (sans cache, sans embedding)."""
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, text, type, score FROM principles WHERE domain=? ORDER BY score DESC LIMIT 50",
        (domain,),
    ).fetchall()
    conn.close()
    qw = set(task.lower().split())
    scored = []
    for r in rows:
        bm25 = len(qw & set(r["text"].lower().split())) / max(len(qw), 1)
        combined = bm25 + r["score"] * 0.3  # cosine=0, decay~1 (fresh)
        scored.append((combined, r["id"]))
    scored.sort(reverse=True)
    return [i for _, i in scored[:top_k]]


def pct(data, p):
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    return s[f] if f == c else s[f] + (s[c] - s[f]) * (k - f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--queries", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "bench.db"
        make_db(db, args.n, args.seed)
        cache = SpiderCache(db_path=db)

        rnd = random.Random(args.seed + 1)
        tasks = [" ".join(rnd.choice(VOCAB) for _ in range(3)) for _ in range(args.queries)]

        t_cache, t_sql, parity = [], [], 0
        for t in tasks:
            for dom in ("defi_quant", "memory"):
                s = time.perf_counter()
                r1 = [d["id"] for d in cache.search(t, domain=dom, top_k=5)]
                t_cache.append((time.perf_counter() - s) * 1000)

                s = time.perf_counter()
                r2 = sqlite_search(db, t, dom)
                t_sql.append((time.perf_counter() - s) * 1000)

                if r1 == r2:
                    parity += 1

        total = args.queries * 2
        res = {
            "n": args.n,
            "queries": total,
            "seed": args.seed,
            "cache_ms": {
                "mean": round(statistics.mean(t_cache), 3),
                "p50": round(pct(t_cache, 50), 3),
                "p95": round(pct(t_cache, 95), 3),
            },
            "sqlite_ms": {
                "mean": round(statistics.mean(t_sql), 3),
                "p50": round(pct(t_sql, 50), 3),
                "p95": round(pct(t_sql, 95), 3),
            },
            "speedup_p50": round(pct(t_sql, 50) / max(pct(t_cache, 50), 1e-9), 2),
            "parity": f"{parity}/{total}",
            "principles_loaded": len(cache.principles),
        }
        print(json.dumps(res, indent=2))
        print(
            f"\n| N={args.n} | cache p50 {res['cache_ms']['p50']}ms | "
            f"sqlite p50 {res['sqlite_ms']['p50']}ms | x{res['speedup_p50']} | parité {res['parity']} |"
        )
        if args.out:
            Path(args.out).write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
