"""Scoreboard auto — classement des hypothèses par chiffres, pas par avis.

Lit hypotheses/ledger.json + bench-v2.json, écrit papers/SCOREBOARD.md.
Usage : python scripts/scoreboard.py
"""

import json
from pathlib import Path

REPO = Path(__file__).parent.parent
LEDGER = REPO / "recherches" / "001-memoire-araignee" / "hypotheses" / "ledger.json"
BENCH = REPO / "recherches" / "001-memoire-araignee" / "papers" / "draft-001-spider-hot-cache" / "bench-v2.json"
OUT = REPO / "papers" / "SCOREBOARD.md"


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"hypotheses": {}}
    bench = json.loads(BENCH.read_text(encoding="utf-8")) if BENCH.exists() else {}

    lines = ["# Scoreboard — classement par chiffres", ""]
    lines.append(f"Baseline bench V2 (N={bench.get('n','?')}) : sqlite p50 {bench.get('sqlite_limit50',{}).get('p50','?')}ms | cache fair p50 {bench.get('cache_fair50',{}).get('p50','?')}ms | fullscan p50 {bench.get('cache_fullscan',{}).get('p50','?')}ms | parité {bench.get('parity_fair','?')}")
    lines += ["", "| Hypothèse | Question | Statut | Runs |", "|---|---|---|---|"]
    for hid, h in ledger.get("hypotheses", {}).items():
        lines.append(f"| {hid} | {h.get('question','')} | {h.get('status','')} | {len(h.get('runs',[]))} |")
    lines += ["", "_Mis à jour par scripts/scoreboard.py. Pas de rang sans JSON._"]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
