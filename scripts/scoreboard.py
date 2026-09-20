"""Scoreboard LABO — agrège TOUTES les recherches.

Lit recherches/*/hypotheses/ledger.json + recherches/*/papers/*/bench-*.json
Écrit papers/SCOREBOARD.md (labo entier).
Usage : python scripts/scoreboard.py
"""

import json
from pathlib import Path

REPO = Path(__file__).parent.parent
OUT = REPO / "papers" / "SCOREBOARD.md"


def main():
    lines = ["# Scoreboard LABO — toutes recherches, par chiffres", ""]
    for rdir in sorted((REPO / "recherches").glob("*")):
        if not rdir.is_dir():
            continue
        lines.append(f"## {rdir.name}")
        for bj in sorted((rdir / "papers").glob("*/bench-*.json")):
            try:
                b = json.loads(bj.read_text(encoding="utf-8"))
                lines.append(f"- `{bj.parent.name}/{bj.name}` N={b.get('n','?')} : {b}")
            except Exception:
                pass
        lp = rdir / "hypotheses" / "ledger.json"
        if lp.exists():
            db = json.loads(lp.read_text(encoding="utf-8"))
            lines += ["", "| Hypothèse | Question | Statut | Runs |", "|---|---|---|---|"]
            for hid, h in db.get("hypotheses", {}).items():
                lines.append(f"| {hid} | {h.get('question','')} | {h.get('status','')} | {len(h.get('runs',[]))} |")
        lines.append("")
    lines.append("_Mis à jour par scripts/scoreboard.py. Pas de rang sans JSON._")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
