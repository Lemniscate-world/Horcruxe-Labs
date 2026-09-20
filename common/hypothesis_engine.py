"""Moteur d'hypothèses minimal — ne jamais perdre la root.

Ledger JSON : chaque hypothèse a un état, une baseline, des runs.
- root = branche main, commit stable
- tester = branche hyp/* + bench harness
- décider = merge seulement si gagne

Usage :
  python hypothesis_engine.py add --id H004 --question "..." --metric "rappel top5"
  python hypothesis_engine.py run --id H004 --bench "python bench_latency.py ..."
  python hypothesis_engine.py decide --id H004 --decision merge
"""

import argparse
import json
from pathlib import Path

LEDGER = Path(__file__).parent.parent / "recherches" / "001-memoire-araignee" / "hypotheses" / "ledger.json"


def load():
    if LEDGER.exists():
        return json.loads(LEDGER.read_text(encoding="utf-8"))
    return {"root": "main", "hypotheses": {}}


def save(d):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
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
    args = ap.parse_args()

    db = load()
    if args.cmd == "add":
        db["hypotheses"][args.id] = {
            "question": args.question,
            "metric": args.metric,
            "status": "a-tester",
            "branch": f"hyp/{args.id}",
            "runs": [],
        }
    elif args.cmd == "run":
        h = db["hypotheses"][args.id]
        h["runs"].append({"bench": args.bench, "result": args.result})
        h["status"] = "en-cours"
    elif args.cmd == "decide":
        db["hypotheses"][args.id]["status"] = args.decision
    save(db)
    print(json.dumps(db["hypotheses"].get(args.id, {}), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
