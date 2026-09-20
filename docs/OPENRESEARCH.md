# OpenResearch — mode d'emploi concret pour Horcruxe Labs

Tu ne le vois pas car ce n'est pas un site, c'est une app locale + CLI `orx`.

## 1. Installer (Windows beta)

- orx 0.2.6 déjà installé ici (`~/.local/bin/orx.exe`, dans le PATH).
- Dashboard optionnel, JAMAIS ouvert d'office : `orx up --no-browser`.
- Sans web : tout se fait en CLI (`orx projects / runs / logs / exp`) + fichiers (`papers/SCOREBOARD.md`) + ping Discord.

## 2. Créer le projet Spider

Dans le dashboard : New Project → Existing repo → `C:\Users\Utilisateur\Documents\Horcruxe Labs` → branche `main` comme root.

## 3. Tester tes hypothèses en parallèle sans perdre la root

- Baseline node : `bench main` (ton bench V2).
- Exp 1 : `hyp/H001-math-notation` (worktree isolé auto).
- Exp 2 : `hyp/H003-graph-weaver`.
- Chaque run archive le commit exact → tu sais quel chiffre vient de quel code.

CLI équivalent :
```
orx projects
orx exp run H001-math-notation
orx logs <run-id>
orx paper <arxiv-id>   # lit un papier pour R81
```

## 4. Tes recherches restent privées

OpenResearch est local-first : projets, runs, logs restent sur ta machine (`127.0.0.1` + SQLite local). Rien n'est publié sauf si tu pousses vers GitHub ou soumets un papier. Compte openresearch.sh optionnel (que pour compute managé).

Prochaine action : dis-moi quand `orx` est installé, je crée le projet + les 3 expériences H001/H002/H003 dedans.
