#!/usr/bin/env python3
"""Build and check public pages: local links, anchors, metadata and artifact hashes."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C
from build_site import ROOT, build

CHECK = "check_site"


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.metadata, self.canonical = [], set(), {}, []
        self.lang, self.h1, self.title, self.images = None, 0, False, []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "html": self.lang = attrs.get("lang")
        if tag == "h1": self.h1 += 1
        if tag == "title": self.title = True
        if tag == "meta": self.metadata[attrs.get("name", attrs.get("property"))] = attrs.get("content")
        if tag == "link" and attrs.get("rel") == "canonical": self.canonical.append(attrs.get("href"))
        if tag == "img": self.images.append(attrs)
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def inspect(site):
    site = Path(site).resolve()
    failures = []
    pages = {path.resolve(): Page(path.read_text()) for path in site.rglob("*.html")}
    for path, page in pages.items():
        label = str(path.relative_to(site))
        if page.lang not in {"zh-CN", "en"} or page.h1 != 1 or not page.title:
            failures.append(f"{label}: language/title/h1 missing or invalid")
        if not page.metadata.get("description") or len(page.canonical) != 1 or not page.canonical[0].startswith("https://"):
            failures.append(f"{label}: description/canonical missing or invalid")
        if any(not image.get("alt") for image in page.images):
            failures.append(f"{label}: image missing descriptive alt")
        if "{{" in path.read_text() or "/Users/" in path.read_text():
            failures.append(f"{label}: unresolved variable or machine path")
        for raw in page.links:
            link = urlsplit(raw)
            if link.scheme or link.netloc:
                continue
            target = (path.parent / unquote(link.path)).resolve() if link.path else path
            if not target.is_relative_to(site) or not target.is_file():
                failures.append(f"{label}: broken or escaping link {raw}")
            elif link.fragment and target in pages and unquote(link.fragment) not in pages[target].ids:
                failures.append(f"{label}: missing anchor {raw}")
    sitemap_path = site / "sitemap.xml"
    try:
        urls = [node.text for node in ElementTree.parse(sitemap_path).iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        canonical = {page.canonical[0] for page in pages.values() if len(page.canonical) == 1}
        if len(urls) != len(pages) or set(urls) != canonical:
            failures.append("sitemap: does not match page canonicals")
    except (OSError, ElementTree.ParseError):
        failures.append("sitemap: missing or invalid")
    for receipt_path in (site / "examples").rglob("receipt.json"):
        receipt = json.loads(receipt_path.read_text())
        for artifact in receipt.get("artifacts", [receipt]):
            file = receipt_path.parent / artifact["file"]
            if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != artifact["sha256"]:
                failures.append(f"{receipt_path.relative_to(site)}: artifact hash mismatch")
    for file in site.rglob("*"):
        if file.is_file() and file.stat().st_size > 1048576:
            failures.append(f"{file.relative_to(site)}: exceeds 1 MB publishing budget")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    C.add_common_args(parser)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as directory:
        destination = build(Path(directory))
        failures = inspect(destination)
    findings = [C.Finding(CHECK, problem, problem, "site/content.json") for problem in failures]
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
