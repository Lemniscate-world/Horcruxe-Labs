"""Visualisation construction progressive des embeddings.

But : montrer d'où vient un vecteur, étape par étape, sans magie.
Pipeline réel all-MiniLM-L6-v2 :
  texte -> tokens -> 6 couches Transformer -> pooling moyenne -> normalisation -> 384 nombres

Ce script fait une version lisible sans télécharger le modèle :
  principes démo -> TF-IDF (poids mots) -> PCA 2D -> PNG

Usage :
  python visualize_embeddings.py --out ../papers/draft-001-spider-hot-cache/figures/embeddings-pca.png
"""

import argparse
from pathlib import Path

PRINCIPES = [
    "slippage impact analysis pool tvl",
    "yield farming caution protocol age",
    "cache routing signal consolidation memory",
    "tvl growth signal routing cache",
    "distillation trajectory policy retrieval",
    "pool fee prioritization tvl growth age",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="embeddings-pca.png")
    args = ap.parse_args()

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import PCA
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Étape 1-2 : texte -> poids (TF-IDF = BM25 simplifié, montre quels mots comptent)
    vec = TfidfVectorizer()
    X = vec.fit_transform(PRINCIPES).toarray()
    print(f"Étape TF-IDF : {X.shape[0]} principes x {X.shape[1]} mots")

    # Étape 3 : compression en 2D pour voir (vrai modèle : 384 dims, ici PCA démo)
    pts = PCA(n_components=2, random_state=42).fit_transform(X)

    plt.figure(figsize=(8, 6))
    for i, (x, y) in enumerate(pts):
        plt.scatter(x, y)
        plt.text(x + 0.02, y + 0.02, f"P{i+1}", fontsize=10)
    plt.title("Principes en 2D (démo TF-IDF+PCA)\nVrai modèle : même idée en 384 dims normalisées")
    plt.xlabel("axe 1 (sens dominant)")
    plt.ylabel("axe 2")
    plt.grid(True, alpha=0.3)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"PNG sauvé : {out}")


if __name__ == "__main__":
    main()
