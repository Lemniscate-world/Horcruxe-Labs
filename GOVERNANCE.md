# Gouvernance — lien kuro-rules (pas de copie)

Tes règles IA sont dans `C:\Users\Utilisateur\Documents\kuro-rules\rules/`, pas ici. On les référence pour éviter la divergence.

Règles qui s'appliquent à Horcruxe Labs :

- **R105 multi-repo/monorepo** (`rule_105_multirepo_governance.md:1`) : Horcruxe Labs est un monorepo hub (`ECOSYSTEM_MAP` = `RESEARCH_MAP.md`). Chaque `recherches/NNN/` est un membre. Avant split en repos séparés : impact + matrice compatibilité.
- **R81 research protocol** (`rule_81_research.md:1`) : terminology scan → landmark papers → frontier 2022-2026 → synthèse dans `notes/`. À appliquer avant chaque Toile.
- **R102 test coverage** (`rule_102_test_coverage.md:1`) : ≥80% total, fallback paths 100%, pas de module à 0% commité.
- **R108 validation pipeline** : gates progressifs avant papier (bench → ablation → review).
- **R75 desk research** : revue bib avant de clamer nouveauté.

Ne pas copier les règles ici. Lire le master dans kuro-rules.
