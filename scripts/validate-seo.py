#!/usr/bin/env python3
"""
Validates SEO fundamentals and internal links across the built Ziduri site.
Pure standard library, no dependencies. Run from the repo root:

    python3 scripts/validate-seo.py

Checks, per indexable HTML page:
  - exactly one <title>, non-empty
  - a meta description
  - a canonical link
  - exactly one <h1>
  - every internal href/src resolves to a real file
  - every canonical URL matches a URL actually listed in sitemap.xml
    (unless the page opts out via <meta name="robots" content="noindex">)

Exits non-zero if any check fails.
"""
from __future__ import annotations

import html.parser
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_ORIGIN = "https://ziduri.in"

EXCLUDE_DIRS = {".git", ".github", "node_modules", "ziduri-handbook", "scripts", ".claude"}


class PageParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_count = 0
        self.title_text = ""
        self._in_title = False
        self.has_description = False
        self.canonical = None
        self.h1_count = 0
        self.robots_noindex = False
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_d = dict(attrs)
        if tag == "title":
            self.title_count += 1
            self._in_title = True
        elif tag == "meta":
            name = (attrs_d.get("name") or "").lower()
            if name == "description" and (attrs_d.get("content") or "").strip():
                self.has_description = True
            if name == "robots" and "noindex" in (attrs_d.get("content") or "").lower():
                self.robots_noindex = True
        elif tag == "link":
            rel = (attrs_d.get("rel") or "").lower()
            href = attrs_d.get("href")
            if rel == "canonical" and href:
                self.canonical = href
            if href:
                self.links.append(href)
        elif tag == "h1":
            self.h1_count += 1
        elif tag in ("a", "img", "script"):
            for key in ("href", "src"):
                if attrs_d.get(key):
                    self.links.append(attrs_d[key])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_text += data


def resolve_internal_link(link: str, page_path: pathlib.Path) -> pathlib.Path | None:
    if link.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
        return None
    link = link.split("#")[0].split("?")[0]
    if not link:
        return None
    if link.startswith("/"):
        target = ROOT / link.lstrip("/")
    else:
        target = (page_path.parent / link).resolve()
    if target.is_dir() or str(target).endswith("/"):
        target = target / "index.html"
    return target


def load_sitemap_urls() -> set[str]:
    sitemap = ROOT / "sitemap.xml"
    urls: set[str] = set()
    if not sitemap.exists():
        return urls
    tree = ET.parse(sitemap)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in tree.getroot().findall(".//sm:url/sm:loc", ns):
        if loc.text:
            urls.add(loc.text.strip())
    return urls


def main() -> int:
    errors: list[str] = []
    html_files = sorted(
        p for p in ROOT.rglob("*.html")
        if not any(part in EXCLUDE_DIRS for part in p.relative_to(ROOT).parts)
    )
    sitemap_urls = load_sitemap_urls()

    for page in html_files:
        rel = page.relative_to(ROOT)
        text = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)

        is_error_page = rel.name == "404.html"

        if parser.title_count != 1:
            errors.append(f"{rel}: expected exactly one <title>, found {parser.title_count}")
        elif not parser.title_text.strip():
            errors.append(f"{rel}: <title> is empty")

        if not is_error_page:
            if not parser.has_description:
                errors.append(f"{rel}: missing meta description")
            if not parser.canonical:
                errors.append(f"{rel}: missing canonical link")
            elif sitemap_urls and not parser.robots_noindex and parser.canonical not in sitemap_urls:
                errors.append(f"{rel}: canonical {parser.canonical} is not listed in sitemap.xml")

        if parser.h1_count != 1:
            errors.append(f"{rel}: expected exactly one <h1>, found {parser.h1_count}")

        for link in parser.links:
            target = resolve_internal_link(link, page)
            if target is None:
                continue
            if not target.exists():
                errors.append(f"{rel}: broken internal link -> {link}")

    if errors:
        print(f"SEO/link validation failed with {len(errors)} issue(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"SEO/link validation passed for {len(html_files)} page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
