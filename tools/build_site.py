#!/usr/bin/env python3
"""Build the public static docs with Python's standard library, no network access."""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, SubElement, tostring

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = '''<!-- THESIS: A reading desk for choosing and trying two agent skills.
OWN-WORLD: White reading surface, slate rail, blue links, native system typography.
STORY: Understand the job, inspect original cases, install, verify a first result.
FIRST VIEWPORT: Navigation rail, question-led heading, copyable command and real deck preview.
FORM: Reference desk, grounded candidate 6; seed key subaru-docs (degraded, no catalog).
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, and DESIGN.md -->'''


def versions():
    result = {}
    for name in ("subaru-slides", "subaru-brainstorm"):
        source = (ROOT / "skills" / name / "SKILL.md").read_text()
        match = re.search(r'^  version: "([^"]+)"$', source, re.M)
        if not match:
            raise ValueError(f"Missing version: {name}")
        result[name] = match.group(1)
    return result


def build(destination: Path, base_url: str | None = None):
    config = json.loads((ROOT / "site/config.json").read_text())
    base = (base_url or config["base_url"]).rstrip("/") + "/"
    if not base.startswith("https://"):
        raise ValueError("base_url must use https")
    destination = destination.resolve()
    # Never replace or delete a user-supplied directory. Only overwrite our known files.
    destination.mkdir(parents=True, exist_ok=True)
    pages = json.loads((ROOT / "site/content.json").read_text())
    current_versions = versions()
    paths = [page["path"] for page in pages]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate page path")
    for page in pages:
        path = Path(page["path"])
        if path.is_absolute() or ".." in path.parts or path.suffix != ".html":
            raise ValueError(f"Invalid page path: {path}")
        lang = page["lang"]
        is_en = lang == "en"
        prefix = "../" if is_en else ""
        e = html.escape
        same_lang = [p for p in pages if p["lang"] == lang and p.get("nav")]
        nav_links = []
        for item in same_lang:
            active = ' aria-current="page"' if item['path'] == page['path'] else ''
            nav_links.append('<a href="' + e(Path(item['path']).name) + '"' + active + '>' + e(item['nav']) + '</a>')
        nav = "".join(nav_links)
        counterpart = next(p for p in pages if p["id"] == page["id"] and p["lang"] != lang)
        alternate = prefix + counterpart["path"]
        if not is_en:
            alternate = counterpart["path"]
        canonical = urljoin(base, page["path"])
        schema = {"@context":"https://schema.org", "@type":"WebPage", "name":page["title"],
                  "description":page["description"], "inLanguage":lang, "url":canonical}
        heading = e(page['title'])
        if page['id'] == 'index' and not is_en:
            heading = '<span class="title-part">用 AI 做演示文稿</span><span class="title-part">打开创意思路</span>'
        schema_json = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c')
        version_text = " · ".join(f'{name}: {value}' for name, value in current_versions.items())
        body = page["body"].replace("{{assets}}", prefix + "examples/").replace("{{repo}}", config["repository"])
        # Root-relative external assets and network scripts are unnecessary for these docs.
        doc = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(page['title'])} · subaru-skills</title><meta name="description" content="{e(page['description'])}">
<link rel="canonical" href="{e(canonical)}"><link rel="alternate" hreflang="{lang}" href="{e(canonical)}">
<link rel="alternate" hreflang="{counterpart['lang']}" href="{e(urljoin(base,counterpart['path']))}">
<meta property="og:type" content="website"><meta property="og:title" content="{e(page['title'])}">
<meta property="og:description" content="{e(page['description'])}"><meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(urljoin(base,'examples/management-report/preview.webp'))}">
<link rel="stylesheet" href="{prefix}style.css"><script src="{prefix}app.js" defer></script>
<script type="application/ld+json">{schema_json}</script></head>
<body>{CONTRACT}<a class="skip" href="#main">{'Skip to content' if is_en else '跳到正文'}</a>
<header><a class="brand" href="index.html">subaru-skills<span>{'Agent skills, with examples' if is_en else '有案例可检查的 Agent Skills'}</span></a>
<div class="header-links"><a href="{e(alternate)}" lang="{counterpart['lang']}">{'中文' if is_en else 'English'}</a><a href="{config['repository']}">GitHub</a></div></header>
<div class="layout"><nav aria-label="{'Documentation' if is_en else '文档导航'}">{nav}</nav>
<main id="main" tabindex="-1"><h1>{heading}</h1>{body}
<footer><p>{'Unpublished development packages. Versions are read from SKILL.md.' if is_en else '当前为未发布开发包；版本从 SKILL.md 读取。'}</p><p class="versions">{e(version_text)}</p>
<p><a href="license.html">{'License and release status' if is_en else '许可与发布状态'}</a> · <a href="{config['repository']}/issues">{'Report an installation problem' if is_en else '反馈安装或使用问题'}</a></p></footer></main></div></body></html>'''
        output = destination / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(doc)
    for name in ("style.css", "app.js"):
        shutil.copyfile(ROOT / "site" / name, destination / name)
    target_examples = destination / "examples"
    for folder in ("management-report", "rag-sharing", "knowledge-library"):
        for source in (ROOT / "examples" / folder).iterdir():
            if source.is_file() and source.suffix in {".json", ".md", ".pptx", ".webp"}:
                target = target_examples / folder / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    sitemap = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for page in pages:
        SubElement(SubElement(sitemap, "url"), "loc").text = urljoin(base, page["path"])
    (destination / "sitemap.xml").write_bytes(tostring(sitemap, encoding="utf-8", xml_declaration=True))
    # A project site's robots.txt is below the host root and is not a host-wide crawl policy.
    (destination / ".nojekyll").write_text("")
    print(f"build_site: {len(pages)} pages -> {destination}")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "output/site")
    parser.add_argument("--base-url", help="Override canonical URLs for a different deployment")
    args = parser.parse_args()
    build(args.out, args.base_url)


if __name__ == "__main__":
    main()
