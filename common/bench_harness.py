"""Harness bench commun Horcruxe Labs.

Toutes les recherches utilisent les mêmes métriques pour que les papiers
soient comparables : mean/p50/p95, seed fixe, sortie JSON.

Usage per-recherche :
  from common.bench_harness import Bench
  bench = Bench(name="toile1-vs-sqlite", seed=42)
  bench.time("cache", lambda: cache.search(...))
  bench.time("sqlite", lambda: sqlite_search(...))
  bench.report(out="bench_results.json")
"""

import json
import math
import statistics
import time
from pathlib import Path


def pct(data, p):
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * p / 100
    f = math.floor(k)
    c = math.ceil(k)
    return s[f] if f == c else s[f] + (s[c] - s[f]) * (k - f)


class Bench:
    def __init__(self, name: str, seed: int = 42):
        self.name = name
        self.seed = seed
        self.series = {}

    def time(self, label: str, fn, reps: int = 1):
        """Mesure fn() reps fois, stocke en ms."""
        vals = self.series.setdefault(label, [])
        for _ in range(reps):
            s = time.perf_counter()
            fn()
            vals.append((time.perf_counter() - s) * 1000)
        return vals

    def summary(self):
        out = {"name": self.name, "seed": self.seed, "metrics": {}}
        for label, vals in self.series.items():
            out["metrics"][label] = {
                "n": len(vals),
                "mean": round(statistics.mean(vals), 3) if vals else 0,
                "p50": round(pct(vals, 50), 3),
                "p95": round(pct(vals, 95), 3),
            }
        labels = list(self.series.keys())
        if len(labels) == 2:
            a, b = labels
            pa = pct(self.series[a], 50)
            pb = pct(self.series[b], 50)
            out["speedup_p50"] = round(pb / max(pa, 1e-9), 2)
            out["note"] = f"{a} p50={pa}ms vs {b} p50={pb}ms"
        return out

    def report(self, out: str = ""):
        res = self.summary()
        print(json.dumps(res, indent=2))
        if out:
            Path(out).write_text(json.dumps(res, indent=2), encoding="utf-8")
        return res
