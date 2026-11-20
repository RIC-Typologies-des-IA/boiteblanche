#!/usr/bin/env python3
"""Prépare l'artefact GitHub Pages avec l'intégralité des fichiers du dépôt."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"

if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
OUTPUT.mkdir()

# Publier tous les fichiers du dépôt : contenus pédagogiques, PDF, présentations,
# scripts, sources, médias, dépendances et fichiers de documentation.
# Seuls les métadonnées Git et le répertoire de sortie sont exclus.
for source in ROOT.rglob("*"):
    if not source.is_file():
        continue
    relative = source.relative_to(ROOT)
    if relative.parts[0] in {".git", "dist"}:
        continue
    target = OUTPUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

print(f"Artefact GitHub Pages complet préparé dans {OUTPUT}.")
