#!/usr/bin/env python3
"""Assemble only browser assets into the GitHub Pages artifact."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dist"
ALLOWED_SUFFIXES = {".html", ".css", ".js", ".png", ".svg", ".webmanifest"}

if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
OUTPUT.mkdir()

for source in ROOT.rglob("*"):
    if not source.is_file():
        continue
    relative = source.relative_to(ROOT)
    if any(part in {".git", ".github", "scripts", "dist"} for part in relative.parts):
        continue
    if source.suffix.lower() not in ALLOWED_SUFFIXES:
        continue
    target = OUTPUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)

# Preserve the third-party license next to the vendored browser distribution.
license_source = ROOT / "vendor/chart.js/LICENSE.md"
license_target = OUTPUT / "vendor/chart.js/LICENSE.md"
license_target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(license_source, license_target)

print(f"Prepared GitHub Pages artifact in {OUTPUT}.")
