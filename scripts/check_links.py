#!/usr/bin/env python3
"""Produce an informational report of unresolved local HTML and CSS references."""

from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data", "blob", "ftp"}
URL_ATTRS = {"href", "src", "action", "poster", "data", "cite", "formaction", "manifest"}
SRCSET_ATTRS = {"srcset"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[int, str]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("name"):
            self.ids.add(values["name"] or "")
        for name, value in attrs:
            if not value:
                continue
            if name.lower() in URL_ATTRS:
                self.references.append((self.getpos()[0], value.strip()))
            elif name.lower() in SRCSET_ATTRS:
                for item in value.split(","):
                    candidate = item.strip().split()
                    if candidate:
                        self.references.append((self.getpos()[0], candidate[0]))


def is_external(url: str) -> bool:
    return urlsplit(url).scheme.lower() in SKIP_SCHEMES or url.startswith("//")


def resolve_target(root: Path, source: Path, url: str) -> tuple[Path | None, str]:
    parsed = urlsplit(url.strip())
    if parsed.scheme or url.startswith("//"):
        return None, unquote(parsed.fragment)
    raw_path = unquote(parsed.path)
    if not raw_path:
        target = source
    elif raw_path.startswith("/"):
        target = root / raw_path.lstrip("/")
    else:
        target = source.parent / raw_path
    try:
        target = target.resolve()
        target.relative_to(root.resolve())
    except (ValueError, OSError):
        return None, unquote(parsed.fragment)
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def main() -> int:
    root = Path(".").resolve()
    unresolved: list[str] = []
    checked = 0
    html_files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in {".html", ".htm"} and ".git" not in p.parts
    )
    parsed_pages: dict[Path, PageParser] = {}

    for page in html_files:
        document = PageParser()
        try:
            document.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            unresolved.append(f"{page.relative_to(root)}: lecture impossible ({exc})")
            continue
        parsed_pages[page.resolve()] = document

    for page, document in parsed_pages.items():
        source_name = page.relative_to(root).as_posix()
        for line, raw_url in document.references:
            if is_external(raw_url):
                continue
            checked += 1
            target, fragment = resolve_target(root, page, raw_url)
            label = f"{source_name}:{line} -> {raw_url}"
            if target is None:
                unresolved.append(f"{label} (chemin invalide ou hors du dépôt)")
                continue
            if not target.is_file():
                unresolved.append(f"{label} (cible absente : {target.relative_to(root)})")
                continue
            if fragment and target.suffix.lower() in {".html", ".htm"}:
                target_page = parsed_pages.get(target.resolve())
                if target_page is None:
                    target_page = PageParser()
                    try:
                        target_page.feed(target.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError) as exc:
                        unresolved.append(f"{label} (lecture de la cible impossible : {exc})")
                        continue
                if fragment not in target_page.ids:
                    unresolved.append(f"{label} (ancre #{fragment} absente)")

    css_files = sorted(p for p in root.rglob("*.css") if p.is_file() and ".git" not in p.parts)
    for css in css_files:
        try:
            content = css.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            unresolved.append(f"{css.relative_to(root)}: lecture impossible ({exc})")
            continue
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", content, re.IGNORECASE):
            raw_url = match.group(2).strip()
            if not raw_url or is_external(raw_url):
                continue
            checked += 1
            target, _ = resolve_target(root, css, raw_url)
            line = content.count("\n", 0, match.start()) + 1
            label = f"{css.relative_to(root)}:{line} -> {raw_url}"
            if target is None or not target.is_file():
                unresolved.append(f"{label} (ressource absente ou chemin invalide)")

    report = [
        "# Rapport des références locales",
        "",
        f"- Références locales examinées : {checked}",
        f"- Pages HTML : {len(html_files)}",
        f"- Feuilles CSS : {len(css_files)}",
        f"- Références non résolues : {len(unresolved)}",
        "",
    ]
    if unresolved:
        report.extend(["## Références non résolues", ""])
        report.extend(f"- {item}" for item in unresolved)
    else:
        report.append("Aucune référence locale non résolue détectée.")

    rendered = "\n".join(report)
    print(rendered)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write(rendered + "\n")

    # This job is deliberately informational: unresolved references never fail CI.
    return 0


if __name__ == "__main__":
    sys.exit(main())
