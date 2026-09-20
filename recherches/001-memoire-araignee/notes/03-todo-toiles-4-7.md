# TODO Toiles 4-7 — pistes de recherche

## Toile 4 — Weaver (prioritaire recherche)
- Graphe RAM des liens entre principes inter-domaines.
- Détection : cosine inter-domaines > seuil + overlap triples (s,p,o) ?
- Livrable : `code/weaver.py` + bench : rappel cross-domain avant/après.

## Toile 5 — Hot Cache 2.0 LRU
- Garder N plus utilisés (compteur use + decay).
- Question : LRU bat-il full-RAM en qualité/latence passé 100k principes ?

## Toile 6 — Mmap Layer
- `numpy.memmap` pour embeddings, RAM constante.
- Bench RSS vs latence.

## Toile 7 — Spider cron
- Refresh planifié 10-30 min, même sans event FS.
- Utile pour papier ops / déploiement.

Mets tes idées datées ici, une section par date.
