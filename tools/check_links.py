#!/usr/bin/env python3
"""Check that relative Markdown links resolve. Skips fenced code and external URLs."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "check_links"
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "data:")
FENCE = chr(96) * 3


def scan_file(path: Path):
    findings = []
    in_fence = False
    for lineno, line in enumerate(C.read_text(path).splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith(FENCE) or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in LINK_RE.finditer(line):
            target = m.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if not target or target.startswith("#") or target.startswith(SKIP_PREFIX):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0].strip()
            if not target or target.startswith(SKIP_PREFIX):
                continue
            if not (path.parent / target).resolve().exists():
                findings.append(C.Finding(CHECK, C.rel(path) + ":" + target,
                                          "broken link -> " + target, C.rel(path), lineno))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Markdown relative links")
    C.add_common_args(parser)
    args = parser.parse_args()
    files = C.iter_markdown_files()
    findings = []
    for f in files:
        findings.extend(scan_file(f))
    print("check_links: scanned " + str(len(files)) + " Markdown file(s)")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
