#!/usr/bin/env python3
"""Check local HTML/CSS references and HTML fragment identifiers."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data", "blob", "ftp"}
URL_ATTRS = {"href", "src", "action", "poster", "data", "cite", "formaction", "manifest"}
SRCSET_ATTRS = {"srcset"}
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[int, str]] = []
        self.ids: set[str] = set()
        self.base_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("name"):
            self.ids.add(values["name"] or "")
        if tag == "base" and values.get("href"):
            self.base_href = values["href"]
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
        return None, ""
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
        return None, parsed.fragment
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    checked = 0

    html_files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".htm"} and ".git" not in p.parts)
    parsed_pages: dict[Path, PageParser] = {}
    for page in html_files:
        document = PageParser()
        try:
            document.feed(page.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"{page.relative_to(root)}: impossible de lire la page ({exc})")
            continue
        parsed_pages[page.resolve()] = document

    for page, document in parsed_pages.items():
        for line, raw_url in document.references:
            checked += 1
            if is_external(raw_url):
                continue
            target, fragment = resolve_target(root, page, raw_url)
            label = f"{page.relative_to(root)}:{line}: {raw_url}"
            if target is None:
                errors.append(f"{label}: chemin sortant du dépôt ou URL invalide")
                continue
            if not target.is_file():
                errors.append(f"{label}: fichier cible introuvable ({target.relative_to(root)})")
                continue
            if fragment and target.suffix.lower() in {".html", ".htm"}:
                target_page = parsed_pages.get(target.resolve())
                if target_page is None:
                    target_page = PageParser()
                    try:
                        target_page.feed(target.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError) as exc:
                        errors.append(f"{label}: impossible de lire la cible ({exc})")
                        continue
                if fragment not in target_page.ids:
                    errors.append(f"{label}: ancre #{fragment} absente de {target.relative_to(root)}")

    css_files = sorted(p for p in root.rglob("*.css") if p.is_file() and ".git" not in p.parts)
    for css in css_files:
        try:
            content = css.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{css.relative_to(root)}: impossible de lire la feuille CSS ({exc})")
            continue
        for match in CSS_URL.finditer(content):
            raw_url = match.group(2).strip()
            if not raw_url or is_external(raw_url):
                continue
            checked += 1
            target, _ = resolve_target(root, css, raw_url)
            line = content.count("\n", 0, match.start()) + 1
            label = f"{css.relative_to(root)}:{line}: {raw_url}"
            if target is None or not target.is_file():
                errors.append(f"{label}: ressource CSS introuvable ou hors du dépôt")

    print(f"Contrôle des liens locaux : {checked} références examinées dans {len(html_files)} pages HTML et {len(css_files)} feuilles CSS.")
    if errors:
        print(f"\n{len(errors)} problème(s) détecté(s) :")
        for error in errors:
            print(f" - {error}")
        return 1
    print("OK : toutes les cibles locales et ancres HTML vérifiées existent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
