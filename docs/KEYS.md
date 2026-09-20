# Clés API — sans terminal

Tu ne tapes rien. Tu remplis 1 fichier, double-clic, ça tourne.

1. Copie `.env.example` vers `.env` (clic droit → copier/coller).
2. Ouvre `.env` avec Notepad, colle tes clés :
```
DEEPSEEK_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...
```
3. Double-clique `run_all.bat`. C'est tout.

À quoi servent les clés :
- Bench V2 actuel : AUCUNE clé nécessaire (BM25 pur, local, gratuit).
- Après : distillation L1→L2 par LLM (DeepSeek pas cher) + embeddings distants via OpenRouter si tu ne veux pas installer `sentence-transformers` (2 Go).
- L'agent lit `.env` tout seul, jamais de clé dans git (`.gitignore` déjà : `.env`).

Sécurité (R101) : `.env` ne sera jamais commité. Ne colle jamais tes clés dans le chat.
