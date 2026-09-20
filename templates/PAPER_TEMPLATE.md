# Template — Papier

Dossier `papers/draft-XXX-slug/` :

```
draft-XXX-slug/
  outline.md   # 1 page : contribution, méthode, résultats, figures prévues
  paper.md     # draft complet
  figures/     # scripts + png (générés, pas à la main)
  refs.bib     # bibtex
  NOTES.md     # journal de soumission : où, quand, retours reviewers
```

Règles :
- 1 papier = 1 contribution vérifiable (bench, preuve, ablation).
- Toujours un bench reproductible : `pytest` ou script avec seed.
- Ne jamais écrire les résultats à la main : générer depuis le code.
