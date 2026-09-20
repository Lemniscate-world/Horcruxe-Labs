# Template — Nouvelle recherche (labo-wide, même système que la 001)

Créer `recherches/NNN-slug/` avec :

```
NNN-slug/
  README.md            # question, hypothèse, état
  ROADMAP.md
  notes/               # 00-vision.md + YYYY-MM-DD-sujet.md
  code/
    README.md          # provenance
    requirements.txt
    bench_v1.py        # bench fair avec common/bench_harness.py
  tests/
  hypotheses/
    README.md          # arbre (copier celui de la 001)
    _TEMPLATE.md
    ledger.json        # via common/hypothesis_engine.py --recherche NNN-slug
  benchmarks/
    README.md + baselines.json + runs/
  papers/
    draft-001-slug/outline.md + paper.md + figures/ + refs.bib + VERSIONS.md
  references/README.md
```

Ensuite :
```
python common/hypothesis_engine.py add --recherche NNN-slug --id H001 --question "..." --metric "..."
python scripts/agent_loop.py --once   # teste TOUT le labo, pas que la 001
python scripts/scoreboard.py          # classe tout le labo
```
