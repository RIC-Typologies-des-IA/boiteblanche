#!/usr/bin/env python3
"""Validate the static Boîte Blanche site before publishing it."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
assert manifest["start_url"] == "./"
assert manifest["scope"] == "./"
for icon in manifest["icons"]:
    assert (ROOT / icon["src"].removeprefix("./")).is_file(), icon["src"]

service_worker = (ROOT / "sw.js").read_text(encoding="utf-8")
match = re.search(r"const PRECACHE_URLS = \[(.*?)\];", service_worker, re.S)
assert match, "PRECACHE_URLS not found in sw.js"
paths = re.findall(r'"([^"]+)"', match.group(1))
missing = [path for path in paths if not (ROOT / path.removeprefix("./")).is_file()
           and path not in ("./",)]
if missing:
    raise SystemExit("Missing precache resources: " + ", ".join(missing))

for required in ("index.html", "css/style.css", "sw.js", "manifest.webmanifest",
                "feux_tricolores/index.html", "feux_tricolores/indexFeux.html", "vendor/chart.js/chart.umd.min.js",
                "vendor/chart.js/LICENSE.md"):
    assert (ROOT / required).is_file(), required

traffic_lights = (ROOT / "feux_tricolores/indexFeux.html").read_text(encoding="utf-8")
assert '../vendor/chart.js/chart.umd.min.js' in traffic_lights
assert 'cdn.jsdelivr.net/npm/chart.js' not in traffic_lights
assert './vendor/chart.js/chart.umd.min.js' in service_worker

print(f"Validated manifest, icon and {len(paths)} offline resources in {ROOT}.")
