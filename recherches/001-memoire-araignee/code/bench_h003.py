"""H003 — Weaver : rappel cross-domain graphe vs texte seul.

Corpus : 10 principes, 2 domaines (defi/memory), 4 paires liées connues.
- Baseline texte : requête d'un domaine, top-3 BM25 sur l'autre domaine
- Weaver : find_links() puis rappel via voisins (si requête matche A, on propose ses voisins B)
- Métrique : paires retrouvées /4, + liens totaux détectés

Sortie JSON : benchmarks/runs/H003.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from weaver import find_links

PRINCIPES = [
    {"id": 1, "text": "tvl growth signal routing cache pool", "domain": "defi_quant", "score": 0.8, "triples": []},
    {"id": 2, "text": "cache routing signal consolidation memory store", "domain": "memory", "score": 0.7, "triples": []},
    {"id": 3, "text": "pool fee prioritization tvl growth age maturity", "domain": "defi_quant", "score": 0.75, "triples": []},
    {"id": 4, "text": "memory consolidation policy retrieval routing", "domain": "memory", "score": 0.65, "triples": []},
    {"id": 5, "text": "slippage impact analysis pool execution latency", "domain": "defi_quant", "score": 0.7, "triples": []},
    {"id": 6, "text": "latency execution trace profiling debug memory", "domain": "memory", "score": 0.6, "triples": []},
    {"id": 7, "text": "yield farming caution protocol age risk", "domain": "defi_quant", "score": 0.6, "triples": []},
    {"id": 8, "text": "distillation trajectory policy retrieval principle", "domain": "memory", "score": 0.55, "triples": []},
    {"id": 9, "text": "arbitrage oracle signal hedge pool", "domain": "defi_quant", "score": 0.5, "triples": []},
    {"id": 10, "text": "unrelated lonely words xyz quantum", "domain": "memory", "score": 0.4, "triples": []},
]

# paires liées attendues (vérité terrain) : (1,2) cache/routing/signal, (3,4) routing/policy?, (5,6) latency/execution
ATTENDUES = [(1, 2), (5, 6)]

# Corpus DUR : synonymes sans mots communs, liés seulement par triples typés
DUR = [
    {"id": 101, "text": "tvl growth momentum pool expansion", "domain": "defi_quant", "score": 0.8,
     "triples": [{"s": "pool", "p": "signal", "o": "growth"}]},
    {"id": 102, "text": "capital increase velocity vault enlargement", "domain": "memory", "score": 0.7,
     "triples": [{"s": "pool", "p": "signal", "o": "growth"}]},
    {"id": 103, "text": "slippage cost execution delay", "domain": "defi_quant", "score": 0.7,
     "triples": [{"s": "trade", "p": "cost", "o": "delay"}]},
    {"id": 104, "text": "friction expense fulfillment lag", "domain": "memory", "score": 0.6,
     "triples": [{"s": "trade", "p": "cost", "o": "delay"}]},
    # distracteurs : aucun mot ni triple en commun avec les paires
    {"id": 105, "text": "solar panel voltage regulator circuit", "domain": "memory", "score": 0.5, "triples": []},
    {"id": 106, "text": "baking sourdough crust fermentation timer", "domain": "memory", "score": 0.45, "triples": []},
    {"id": 107, "text": "lunar orbit trajectory correction burn", "domain": "memory", "score": 0.4, "triples": []},
    {"id": 108, "text": "chess opening gambit sacrifice exchange", "domain": "memory", "score": 0.35, "triples": []},
    {"id": 109, "text": "concrete curing humidity control blanket", "domain": "defi_quant", "score": 0.4, "triples": []},
    {"id": 110, "text": "opera libretto aria staging rehearsal", "domain": "defi_quant", "score": 0.35, "triples": []},
]
ATTENDUES_DUR = [(101, 102), (103, 104)]


def bm25_top(rows, task, top_k=3):
    qw = set(task.lower().split())
    sc = []
    for p in rows:
        b = len(qw & set(p["text"].lower().split())) / max(len(qw), 1)
        sc.append((b, p["id"]))
    sc.sort(reverse=True)
    return [i for _, i in sc[:top_k]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    s = time.perf_counter()
    edges = find_links(PRINCIPES, min_overlap=2, top_k=50)
    lat = round((time.perf_counter() - s) * 1000, 3)
    paires = {(min(e["a_id"], e["b_id"]), max(e["a_id"], e["b_id"])) for e in edges}
    retrouvées = [p for p in ATTENDUES if p in paires]

    # baseline texte : requête = texte du principe A, top-3 BM25 côté autre domaine
    hits_base = 0
    for a, b in ATTENDUES:
        qa = next(p["text"] for p in PRINCIPES if p["id"] == a)
        autres = [p for p in PRINCIPES if p["domain"] != next(x["domain"] for x in PRINCIPES if x["id"] == a)]
        if b in bm25_top(autres, qa):
            hits_base += 1

    res = {
        "liens_detectes": len(edges),
        "paires_retrouvees_weaver": f"{len(retrouvées)}/{len(ATTENDUES)}",
        "paires_retrouvees_bm25": f"{hits_base}/{len(ATTENDUES)}",
        "lat_weaver_ms": lat,
    }

    # Corpus DUR : mots disjoints, seuls les triples relient
    edges_dur = find_links(DUR, min_overlap=0, top_k=50)
    paires_dur = {(min(e["a_id"], e["b_id"]), max(e["a_id"], e["b_id"])) for e in edges_dur
                  if e["triple_overlap"] > 0}
    retrouv_dur = [p for p in ATTENDUES_DUR if p in paires_dur]
    hits_dur = 0
    for a, b in ATTENDUES_DUR:
        qa = next(p["text"] for p in DUR if p["id"] == a)
        autres = [p for p in DUR if p["id"] != a and p["domain"] != next(x["domain"] for x in DUR if x["id"] == a)]
        if b in bm25_top(autres, qa):
            hits_dur += 1
    res["dur_weaver_triples"] = f"{len(retrouv_dur)}/{len(ATTENDUES_DUR)}"
    res["dur_bm25"] = f"{hits_dur}/{len(ATTENDUES_DUR)}"
    print(json.dumps(res, indent=2))
    print("edges:", json.dumps(edges[:5], ensure_ascii=False))
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
