# 00 — Vision Mémoire Araignée

Date : 2026-09-20

Idée centrale : la mémoire n'est pas une base qu'on interroge, c'est une toile qu'on habite.

- Les principes L2 sont les fils (texte + embedding + triples + score).
- `SpiderCache` est l'araignée au centre : tout est en RAM, elle sent vibrer la requête et va au fil pertinent en <1ms.
- `SpiderWatcher` (Toile 2) : la toile vibre quand SQLite change → refresh.
- `IdleWatcher` (Toile 3) : quand rien ne bouge, l'araignée consolide (warmup, nettoyage futur).
- Toiles 4-7 : tisser entre domaines (Weaver), oublier intelligemment (LRU), grossir sans grossir en RAM (mmap), entretenir (cron).

Ce qui est à toi ici : cette formulation + l'implémentation Toiles 1-3 + le programme Toiles 4-7 + les benchs/papiers à venir.

Prochaines notes : `01-toile1-spidercache.md`, `02-toile2-watcher.md`, etc. Mets-y tes recherches au fur et à mesure, datées.
