#!/usr/bin/env python3
"""Prépare l'artefact GitHub Pages avec l'intégralité des fichiers du dépôt."""
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"


def build_identifier():
    """Use the published commit SHA, with safe local fallbacks for previews."""
    identifier = os.environ.get("GITHUB_SHA")
    if not identifier:
        try:
            identifier = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            identifier = f"local-{time.time_ns()}"
    identifier = re.sub(r"[^a-zA-Z0-9_-]", "-", identifier)[:64]
    if not identifier:
        raise SystemExit("Impossible de déterminer un identifiant de build.")
    return identifier


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

# A unique cache name makes every deployed worker a new worker, even when the
# source sw.js itself did not change between content-only commits.
worker_path = OUTPUT / "sw.js"
worker = worker_path.read_text(encoding="utf-8")
if worker.count("__BUILD_ID__") != 1:
    raise SystemExit("Le marqueur __BUILD_ID__ doit apparaître exactement une fois dans sw.js.")
worker_path.write_text(
    worker.replace("__BUILD_ID__", build_identifier()), encoding="utf-8"
)

print(f"Artefact GitHub Pages complet préparé dans {OUTPUT}.")
