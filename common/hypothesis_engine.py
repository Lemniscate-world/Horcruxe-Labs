"""Moteur d'hypothèses LABO — ne jamais perdre la root.

Labo-wide : --recherche 001-memoire-araignee (défaut) ou --recherche 002-xxx.
Chaque recherche a son ledger : recherches/<slug>/hypotheses/ledger.json

Usage :
  python hypothesis_engine.py add --recherche 001-memoire-araignee --id H004 --question "..." --metric "rappel top5"
  python hypothesis_engine.py run --recherche 001-memoire-araignee --id H004 --bench "..." --result "..."
  python hypothesis_engine.py decide --recherche 001-memoire-araignee --id H004 --decision merge
  python hypothesis_engine.py list --recherche 001-memoire-araignee
"""

import argparse
import json
from pathlib import Path

REPO = Path(__file__).parent.parent


def ledger_path(recherche: str) -> Path:
    return REPO / "recherches" / recherche / "hypotheses" / "ledger.json"


def load(recherche: str):
    p = ledger_path(recherche)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"root": "main", "recherche": recherche, "hypotheses": {}}


def save(recherche: str, d):
    p = ledger_path(recherche)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recherche", default="001-memoire-araignee")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--question", required=True)
    a.add_argument("--metric", default="p50, rappel top5")
    r = sub.add_parser("run")
    r.add_argument("--id", required=True)
    r.add_argument("--bench", required=True)
    r.add_argument("--result", default="")
    d = sub.add_parser("decide")
    d.add_argument("--id", required=True)
    d.add_argument("--decision", choices=["merge", "abandon", "reformuler"], required=True)
    sub.add_parser("list")
    args = ap.parse_args()

    db = load(args.recherche)
    if args.cmd == "add":
        db["hypotheses"][args.id] = {
            "question": args.question, "metric": args.metric,
            "status": "a-tester", "branch": f"hyp/{args.recherche}/{args.id}", "runs": [],
        }
    elif args.cmd == "run":
        h = db["hypotheses"][args.id]
        h["runs"].append({"bench": args.bench, "result": args.result})
        h["status"] = "en-cours"
    elif args.cmd == "decide":
        db["hypotheses"][args.id]["status"] = args.decision
    save(args.recherche, db)
    if args.cmd == "list":
        print(json.dumps(db, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(db["hypotheses"].get(args.id, {}), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
