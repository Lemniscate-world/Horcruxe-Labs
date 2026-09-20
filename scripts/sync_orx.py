"""Sync labo <-> OpenResearch, 100% CLI, sans navigateur.

Pour chaque recherche du labo avec ledger :
  1. baseline (si absente) : orx create-experiment <proj> --baseline --title ... --run-command ...
  2. 1 enfant par hypothèse a-tester/en-cours : --parent <baseline>
  3. run des enfants sans run gagnant : orx exp run <id>
  4. logs -> ledger runs + scoreboard (infos utilisées avec nous)

Usage : python scripts/sync_orx.py --project <projectId> [--wait 120]
Sans --project : affiche l'aide (import dashboard d'abord, une fois).
"""

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent


def sh(*cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return (p.returncode, (p.stdout.strip() + p.stderr.strip())[:2000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="")
    ap.add_argument("--wait", type=int, default=0)
    args = ap.parse_args()

    if not args.project:
        print("Usage : python scripts/sync_orx.py --project <id>  (voir `orx projects`)")
        print("Import une fois dans le dashboard : Add project -> Existing repo -> ce dossier.")
        return

    for rdir in sorted((REPO / "recherches").glob("*")):
        if not rdir.is_dir():
            continue
        lp = rdir / "hypotheses" / "ledger.json"
        if not lp.exists():
            continue
        db = json.loads(lp.read_text(encoding="utf-8"))
        print(f"== {rdir.name} : {len(db.get('hypotheses', {}))} hypothèses ==")
        # baseline : taggée dans le ledger pour ne la créer qu'une fois
        if not db.get("orx_baseline"):
            rc, out = sh("orx", "create-experiment", args.project,
                         "--baseline", "--title", f"{rdir.name} baseline",
                         "--run-command", f"python scripts/agent_loop.py --once")
            print("baseline:", rc, out[:200])
            if rc == 0:
                db["orx_baseline"] = out.strip().split()[-1]
                lp.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")
        for hid, h in db.get("hypotheses", {}).items():
            if h.get("status") not in ("a-tester", "en-cours") or h.get("orx_exp"):
                continue
            rc, out = sh("orx", "create-experiment", args.project,
                         "--title", hid, "--parent", db.get("orx_baseline", ""),
                         "--description", h.get("question", ""))
            print(hid, ":", rc, out[:200])
            if rc == 0:
                h["orx_exp"] = out.strip().split()[-1]
        lp.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")

    print("OK. Runs : `orx exp run <expId>` puis `orx exp wait <expId>` (voir openresearch.yaml).")


if __name__ == "__main__":
    main()
