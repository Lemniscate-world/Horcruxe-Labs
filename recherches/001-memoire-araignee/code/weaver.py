"""Toile 4 — Weaver (draft labo).

But : détecter des liens cross-domaines entre principes L2, aujourd'hui
impossibles car `WHERE domain=?` isole les silos (cf. PLAN Phase 12).

V1 minimale, sans dépendance :
- lien si overlap lexical >= min_overlap mots (hors stopwords chiffres/ids)
- bonus si overlap triples (s,p,o)
- score = overlap + 0.5 * triple_overlap + 0.2 * score_moyen

Sortie : liste d'arêtes {a_id, a_domain, b_id, b_domain, score, evidence}.

Usage :
  from weaver import find_links
  edges = find_links(principles)  # principles = cache.principles ou dicts
"""

from itertools import combinations


def _tokens(text: str) -> set:
    toks = set()
    for w in text.lower().split():
        w = w.strip(".,;:()[]")
        if len(w) < 3 or w.isdigit():
            continue
        toks.add(w)
    return toks


def find_links(principles, min_overlap: int = 2, top_k: int = 50):
    """principes: objets avec .id/.text/.domain/.score/.triples ou dicts."""
    def get(p, k, d=None):
        return p.get(k, d) if isinstance(p, dict) else getattr(p, k, d)

    # Grouper par domaine pour ne comparer que inter-domaines
    by_dom = {}
    for p in principles:
        by_dom.setdefault(get(p, "domain", "general") or "general", []).append(p)

    doms = list(by_dom.keys())
    edges = []
    for i in range(len(doms)):
        for j in range(i + 1, len(doms)):
            for a in by_dom[doms[i]]:
                ta = _tokens(get(a, "text", ""))
                tra = get(a, "triples", []) or []
                sa = {str(t) for t in tra} if isinstance(tra, list) else set()
                for b in by_dom[doms[j]]:
                    tb = _tokens(get(b, "text", ""))
                    inter = ta & tb
                    if len(inter) < min_overlap:
                        continue
                    trb = get(b, "triples", []) or []
                    sb = {str(t) for t in trb} if isinstance(trb, list) else set()
                    tri_over = len(sa & sb) if (sa and sb) else 0
                    score = (
                        len(inter)
                        + 0.5 * tri_over
                        + 0.2 * ((get(a, "score", 0.5) or 0.5) + (get(b, "score", 0.5) or 0.5)) / 2
                    )
                    edges.append(
                        {
                            "a_id": get(a, "id"),
                            "a_domain": doms[i],
                            "b_id": get(b, "id"),
                            "b_domain": doms[j],
                            "score": round(score, 3),
                            "evidence": sorted(inter)[:8],
                            "triple_overlap": tri_over,
                        }
                    )
    edges.sort(key=lambda e: e["score"], reverse=True)
    return edges[:top_k]


if __name__ == "__main__":
    demo = [
        {"id": 1, "text": "tvl growth signal routing cache", "domain": "defi_quant", "score": 0.8, "triples": []},
        {"id": 2, "text": "cache routing signal consolidation memory", "domain": "memory", "score": 0.7, "triples": []},
        {"id": 3, "text": "unrelated lonely words xyz", "domain": "memory", "score": 0.5, "triples": []},
    ]
    import json
    print(json.dumps(find_links(demo), indent=2, ensure_ascii=False))
