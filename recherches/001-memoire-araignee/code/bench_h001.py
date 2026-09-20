"""H001 — compression math : tokens, rappel, latence.

Corpus : 12 principes texte (distillation EvolveR + synthétiques) et leur
version math manuelle. Mesure :
  1. tokens moyens (tiktoken cl100k) texte vs math
  2. rappel top-3 : requête texte → trouve version math ? (BM25 pur, fair)
  3. latence p50 des deux côtés

Sortie JSON : benchmarks/runs/H001.json
Usage : python code/bench_h001.py --out ../benchmarks/runs/H001.json
"""

import argparse
import json
import time
from pathlib import Path

PAIRS = [
    ("Prioritize CLMM pools with fee 0.05% when 4h TVL growth exceeds 15% and pool age above 90 days",
     "CLMM(f=0.05%) & gTVL4h>15% & age>90j -> prioriser"),
    ("Avoid yield farming on protocols under 30 days old, high APR is a rug signal when TVL erratic",
     "farm(APY?) & age<30j & TVL~erratique -> eviter #rug"),
    ("Cache routing signals in RAM to serve principle search under 1ms",
     "cache(signaux, RAM) -> p50<1ms"),
    ("Refresh L2 cache when distilled DB file changes with 5s cooldown",
     "watch(l2.db) & cooldown=5s -> refresh"),
    ("Warm up embeddings during robot inactivity after 60 seconds idle",
     "idle>60s -> warmup(embeddings)"),
    ("Detect cross-domain links between principles sharing triples",
     "liens(a,b) si triples(a)n triples(b)!=0"),
    ("Slippage impact grows with pool size and latency of execution",
     "slippage ~ f(taille_pool, latence)"),
    ("Require TVL above 1M and maturity above 30 days before recommending",
     "reco si TVL>1M & age>30j"),
    ("Penalize principles unused for 35 days with exponential decay",
     "score *= exp(-0.01*idle_j)"),
    ("Deduplicate principles by cosine similarity above threshold",
     "dedup si cosine>seuil"),
    ("Distill successful trajectories into guiding principles with triples",
     "trajectoire(succes) -> principe + triples"),
    ("Distill failed trajectories into cautionary principles",
     "trajectoire(echec) -> principe prudence"),
]

QUERIES = ["CLMM TVL growth pool", "yield farming rug risk", "cache RAM search latency",
           "refresh DB cooldown", "idle warmup embeddings", "cross-domain triples link"]


def bm25_top(rows, task, top_k=3):
    qw = set(task.lower().split())
    sc = []
    for i, text in rows:
        b = len(qw & set(text.lower().split())) / max(len(qw), 1)
        sc.append((b, i))
    sc.sort(reverse=True)
    return [i for _, i in sc[:top_k]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    tt = [len(enc.encode(t)) for t, _ in PAIRS]
    tm = [len(enc.encode(m)) for _, m in PAIRS]

    texts = [(i, t) for i, (t, _) in enumerate(PAIRS)]
    maths = [(i, m) for i, (_, m) in enumerate(PAIRS)]

    # rappel : requête texte -> top-3 math contient le bon id ?
    hits_tm = sum(1 for q, (tid, _) in zip(QUERIES, PAIRS[:6])
                  for _ in [bm25_top(maths, q)] if tid in bm25_top(maths, q))
    hits_tt = sum(1 for q, (tid, _) in zip(QUERIES, PAIRS[:6])
                  if tid in bm25_top(texts, q))

    def p50(fn, reps=50):
        vals = []
        for _ in range(reps):
            s = time.perf_counter()
            fn()
            vals.append((time.perf_counter() - s) * 1000)
        return round(sorted(vals)[len(vals) // 2], 4)

    lat_t = p50(lambda: bm25_top(texts, QUERIES[0]))
    lat_m = p50(lambda: bm25_top(maths, QUERIES[0]))

    res = {
        "tokens_texte_mean": round(sum(tt) / len(tt), 1),
        "tokens_math_mean": round(sum(tm) / len(tm), 1),
        "tokens_ratio": round((sum(tm) / len(tm)) / (sum(tt) / len(tt)), 2),
        "rappel_texte_vers_texte": f"{hits_tt}/6",
        "rappel_texte_vers_math": f"{hits_tm}/6",
        "lat_p50_texte_ms": lat_t,
        "lat_p50_math_ms": lat_m,
    }
    print(json.dumps(res, indent=2))
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
