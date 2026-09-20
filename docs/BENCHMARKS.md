# Benchmarks & données — comment prouver du nouveau

Tu as raison : sans données + benchmarks par domaine, on ne sait pas si c'est nouveau ou mieux.

## 1. Nouveauté = 3 preuves (R81)

1. **Bib** : 2-3 papiers fondateurs + 3-5 récents 2022-2026. Si personne ne fait X → angle nouveau.
   Réutilise `Neural-Research/research/evidence-matrix.csv`, `open-questions.md`, `scorecard.md`.
2. **Bench** : même données, même seed, baseline `main` re-mesurée. Chiffres JSON, pas d'avis.
3. **Ablation** : on enlève un morceau (cosine, decay, triples). Si ça chute → le morceau compte.

## 2. Registre par recherche (obligatoire)

Chaque `recherches/NNN/` aura :
```
benchmarks/
  README.md        # quelles données, quelles métriques, quel SOTA
  datasets/        # petits jeux seedés, ou liens (pas de gros fichiers en git)
  baselines.json   # chiffres main : p50/p95, rappel, tokens
  runs/            # JSON de chaque run hyp/* (vient du harness)
```

Métriques Spider : latence p50/p95, RAM, rappel top-5, tokens prompt, parité vs SQLite.
Autres domaines plus tard : même harness `common/bench_harness.py`, autres métriques.

## 3. Moteur d'hypothèses

`common/hypothesis_engine.py` = ledger qui empêche de perdre la root :
- `add` → idée + métrique + branche `hyp/XXX`
- `run` → bench + résultat JSON
- `decide` → merge / abandon / reformuler

Root `main` intacte. OpenResearch lit ce ledger pour créer ses expériences en miroir.
