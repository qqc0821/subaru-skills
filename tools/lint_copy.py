#!/usr/bin/env python3
"""Lint copy for common AI-isms. Scans .md/.txt files or a .pptx's slide text.

Warnings only: this is a first-pass filter, not a verdict.
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "lint_copy"
PATTERNS = [
    ("not-x-but-y", r"不是.{0,24}而是", "avoid '不是X而是Y' constructions"),
    ("buzzword", r"赋能|抓手|闭环|颠覆|重塑|生态位|护城河|多维度立体化", "buzzword; prefer plain wording"),
    ("vague", r"一定程度上|某种意义上", "vague qualifier; delete or quantify"),
    ("imperative", r"让我们|开始之前", "avoid imperative/narration"),
    ("redundant-verb", r"进行.{0,4}(优化|讨论|分析|梳理)", "redundant '进行'; use the verb directly"),
]


def extract_pptx(path: str):
    texts = []
    with zipfile.ZipFile(path) as zf:
        names = sorted(n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n))
        for n in names:
            try:
                root = ET.fromstring(zf.read(n))
            except ET.ParseError:
                continue
            for el in root.iter():
                if el.tag.rsplit("}", 1)[-1] == "t" and el.text:
                    texts.append(el.text)
    return texts


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint copy for AI-isms")
    parser.add_argument("source")
    C.add_common_args(parser)
    args = parser.parse_args()
    p = Path(args.source)
    if not p.is_file():
        print("lint_copy: file not found: " + args.source, file=sys.stderr)
        return 2
    chunks = extract_pptx(str(p)) if p.suffix.lower() == ".pptx" else [C.read_text(p)]
    findings = []
    for ci, chunk in enumerate(chunks):
        for pid, rx, msg in PATTERNS:
            for m in re.finditer(rx, chunk):
                findings.append(C.Finding(CHECK, pid + ":" + str(ci) + ":" + str(m.start()),
                                          msg + " -> " + m.group(0), C.rel(p), 0, "warning"))
    print("lint_copy: " + str(len(findings)) + " hit(s) in " + str(p))
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
