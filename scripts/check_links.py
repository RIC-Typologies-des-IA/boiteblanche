#!/usr/bin/env python3
"""Check local HTML/CSS references; known planned content is reported as a warning."""

from __future__ import annotations

import argparse
import json
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
        return None, unquote(parsed.fragment)
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def load_exceptions(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    exceptions: dict[tuple[str, str], dict[str, str]] = {}
    for item in payload.get("references", []):
        if item.get("severity") != "warning":
            raise ValueError("Les exceptions doivent utiliser severity=warning.")
        key = (item["source"], item["target"])
        if key in exceptions:
            raise ValueError(f"Exception dupliquée : {key}")
        exceptions[key] = item
    return exceptions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--exceptions",
        type=Path,
        default=Path("scripts/link_check_exceptions.json"),
        help="Registre explicite des références anticipées non bloquantes.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    exceptions_path = args.exceptions if args.exceptions.is_absolute() else root / args.exceptions
    exceptions = load_exceptions(exceptions_path)

    errors: list[str] = []
    warnings: list[tuple[str, int, str]] = []
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
            errors.append(f"{page.relative_to(root)}: impossible de lire la page ({exc})")
            continue
        parsed_pages[page.resolve()] = document

    for page, document in parsed_pages.items():
        source_name = page.relative_to(root).as_posix()
        for line, raw_url in document.references:
            checked += 1
            if is_external(raw_url):
                continue
            target, fragment = resolve_target(root, page, raw_url)
            label = f"{source_name}:{line}: {raw_url}"
            if target is None:
                errors.append(f"{label}: chemin sortant du dépôt ou URL invalide")
                continue
            if not target.is_file():
                exception = exceptions.get((source_name, raw_url))
                if exception:
                    reason = exception.get("reason", "Contenu planifié, non encore publié.")
                    warnings.append((source_name, line, f"{raw_url}: {reason}"))
                else:
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
        # Keep CSS URL parsing deliberately narrow: url(...) references only.
        import re
        for match in re.finditer(r"url\(\s*(['\"]?)(.*?)\1\s*\)", content, re.IGNORECASE):
            raw_url = match.group(2).strip()
            if not raw_url or is_external(raw_url):
                continue
            checked += 1
            target, _ = resolve_target(root, css, raw_url)
            line = content.count("\n", 0, match.start()) + 1
            label = f"{css.relative_to(root)}:{line}: {raw_url}"
            if target is None or not target.is_file():
                errors.append(f"{label}: ressource CSS introuvable ou hors du dépôt")

    print(
        f"Contrôle des liens locaux : {checked} références examinées dans "
        f"{len(html_files)} pages HTML et {len(css_files)} feuilles CSS."
    )
    for source, line, message in warnings:
        print(f"::warning file={source},line={line}::Référence vers un contenu planifié : {message}")
    if warnings:
        print(f"{len(warnings)} avertissement(s) non bloquant(s) :")
        for source, line, message in warnings:
            print(f" - {source}:{line}: {message}")
    if errors:
        print(f"\n{len(errors)} erreur(s) bloquante(s) :")
        for error in errors:
            print(f"::error::{error}")
        return 1
    print("OK : aucune erreur bloquante de référence locale.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Erreur de configuration du contrôle des liens : {exc}", file=sys.stderr)
        sys.exit(2)
