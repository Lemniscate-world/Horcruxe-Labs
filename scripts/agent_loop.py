"""Agent autonome Horcruxe LABO — tourne sur TOUTES les recherches, pas que la 001.

Boucle : pour chaque recherches/*/ → bench + démos + scoreboard labo.
orx = miroir optionnel, jamais prérequis.

Usage :
  python agent_loop.py --once
  python agent_loop.py --loop 3600
  double-clic run_all.bat (sans terminal à taper)
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return (p.stdout.strip() + p.stderr.strip())[:800]


def tour_recherche(rdir: Path):
    code = rdir / "code"
    print(f"--- {rdir.name} ---")
    for bench in sorted(code.glob("bench_*.py")):
        if bench.name == "bench_latency.py":
            continue  # V1 historique, V2 fait foi
        out = bench.parent.parent / "papers"
        outs = list(out.glob("*/bench-*.json"))
        dest = str(outs[0]) if outs else ""
        cmd = [sys.executable, str(bench), "--n", "2000", "--queries", "30", "--seed", "42"]
        if dest:
            cmd += ["--out", dest]
        print(bench.name, ":", run(cmd)[:300])
    weaver = code / "weaver.py"
    if weaver.exists():
        print("weaver:", run([sys.executable, str(weaver)])[:200])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--loop", type=int, default=0)
    args = ap.parse_args()

    def tour():
        print("== tour agent LABO ==")
        for rdir in sorted((REPO / "recherches").glob("*")):
            if rdir.is_dir() and (rdir / "code").exists():
                tour_recherche(rdir)
        print(run([sys.executable, str(REPO / "scripts" / "scoreboard.py")])[:600])
        print("== fin tour ==")

    import time
    if args.once or args.loop == 0:
        tour()
    else:
        while True:
            tour()
            time.sleep(args.loop)


if __name__ == "__main__":
    main()
