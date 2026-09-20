"""Bench V2 simple et fair — Toile 1.

Fair = même candidats des deux côtés, même seed, embed désactivé.
- Génère N principes (seed fixe), 2 domaines
- Baseline SQLite : ORDER BY score LIMIT 50 puis rescore BM25+score (comme memory_agent)
- Cache : même limite TOP 50 par score puis rescore (pour comparer à armes égales)
- 2e mesure : full-scan cache (vrai usage) vs SQLite LIMIT 50
- Sortie JSON + ligne markdown pour papier

Usage :
  python bench_v2.py --n 2000 --queries 30 --seed 42 --out ../papers/draft-001-spider-hot-cache/bench-v2.json
"""

import argparse
import json
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

VOCAB = ["slippage", "yield", "pool", "tvl", "cache", "memory", "signal", "routing"]


def make_db(path: Path, n: int, seed: int):
    rnd = random.Random(seed)
    conn = sqlite3.connect(str(path))
    conn.executescript(
        "CREATE TABLE principles (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, type TEXT, domain TEXT, score REAL, embedding BLOB, triples_json TEXT, last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP);"
    )
    for i in range(n):
        words = " ".join(rnd.choice(VOCAB) for _ in range(5)) + f" {i}"
        conn.execute(
            "INSERT INTO principles (text,type,domain,score) VALUES (?,?,?,?)",
            (words, "guiding", "defi_quant" if i % 2 == 0 else "memory", round(rnd.uniform(0.2, 0.9), 3)),
        )
    conn.commit()
    conn.close()


def bm25_ids(rows, task, top_k=5):
    qw = set(task.lower().split())
    scored = []
    for _id, text, score in rows:
        b = len(qw & set(text.lower().split())) / max(len(qw), 1)
        scored.append((b + score * 0.3, _id))
    scored.sort(reverse=True)
    return [i for _, i in scored[:top_k]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--queries", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "v2.db"
        make_db(db, args.n, args.seed)
        cache = spider_mod.SpiderCache(db_path=db)
        cache._embed_query = lambda t: None  # fair : BM25 pur des deux côtés

        rnd = random.Random(args.seed + 1)
        tasks = [" ".join(rnd.choice(VOCAB) for _ in range(3)) for _ in range(args.queries)]

        conn = sqlite3.connect(str(db))
        t_sql, t_fair, t_full, parity = [], [], [], 0
        for t in tasks:
            for dom in ("defi_quant", "memory"):
                rows = conn.execute(
                    "SELECT id, text, score FROM principles WHERE domain=? ORDER BY score DESC LIMIT 50",
                    (dom,),
                ).fetchall()

                s = time.perf_counter()
                r_sql = bm25_ids(rows, t)
                t_sql.append((time.perf_counter() - s) * 1000)

                # cache fair : mêmes 50 candidats
                ids50 = {r[0] for r in rows}
                sub = [p for p in cache.principles if p.id in ids50 and (p.domain or "general") == dom]
                s = time.perf_counter()
                qw = set(t.lower().split())
                sc = []
                for p in sub:
                    b = len(qw & set(p.text.lower().split())) / max(len(qw), 1)
                    sc.append((b + p.score * 0.3, p.id))
                sc.sort(reverse=True)
                r_fair = [i for _, i in sc[:5]]
                t_fair.append((time.perf_counter() - s) * 1000)

                s = time.perf_counter()
                r_full = [d["id"] for d in cache.search(t, domain=dom, top_k=5)]
                t_full.append((time.perf_counter() - s) * 1000)

                if r_sql == r_fair:
                    parity += 1
        conn.close()

        def stats(v):
            s = sorted(v)
            return {"mean": round(statistics.mean(v), 3), "p50": round(s[len(s) // 2], 3)}

        res = {
            "n": args.n, "seed": args.seed,
            "sqlite_limit50": stats(t_sql),
            "cache_fair50": stats(t_fair),
            "cache_fullscan": stats(t_full),
            "parity_fair": f"{parity}/{args.queries * 2}",
        }
        print(json.dumps(res, indent=2))
        if args.out:
            Path(args.out).write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
