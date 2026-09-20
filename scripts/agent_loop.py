"""Agent autonome Horcruxe — pas besoin de lancer orx à la main.

Boucle : propose (ledger) -> teste (bench harness) -> décide (scoreboard).
orx devient un simple miroir optionnel (dashboard), pas un prérequis.

Usage :
  python agent_loop.py --once        # 1 tour : baseline + weaver démo + scoreboard
  python agent_loop.py --loop 3600   # toutes les heures (laisse tourner)
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
CODE = REPO / "recherches" / "001-memoire-araignee" / "code"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return p.stdout.strip() + p.stderr.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", type=int, default=0)
    args = ap.parse_args()

    def tour():
        print("== tour agent ==")
        # 1. Baseline V2
        out = run([sys.executable, str(CODE / "bench_v2.py"), "--n", "2000", "--queries", "30", "--seed", "42",
                   "--out", str(CODE.parent / "papers" / "draft-001-spider-hot-cache" / "bench-v2.json")])
        print(out[:500])
        # 2. Weaver démo (preuve qu'il tourne)
        out2 = run([sys.executable, str(CODE / "weaver.py")])
        print("weaver:", out2[:300])
        # 3. Scoreboard
        print(run([sys.executable, str(REPO / "scripts" / "scoreboard.py")])[:400])
        print("== fin tour ==")

    if args.once or args.loop == 0:
        tour()
    else:
        while True:
            tour()
            time.sleep(args.loop)


if __name__ == "__main__":
    main()
