#!/usr/bin/env python3
"""Asset hygiene: size budgets, forbidden files and image format."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "check_assets"
FORBIDDEN_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
FORBIDDEN_SUFFIX = {".pyc", ".pem", ".key"}
FORBIDDEN_DIRS = {"__pycache__", "node_modules", ".venv", ".git"}
RASTER_SUFFIX = {".png", ".jpg", ".jpeg", ".gif"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Asset hygiene checks")
    C.add_common_args(parser)
    args = parser.parse_args()
    findings = []
    largest = []
    skills = C.iter_skill_dirs()
    for skill in skills:
        total = 0
        non_webp = 0
        for f in skill.rglob("*"):
            if not f.is_file():
                continue
            if set(f.parts) & FORBIDDEN_DIRS:
                continue
            rel = C.rel(f)
            size = f.stat().st_size
            total += size
            largest.append((size, rel))
            if f.name in FORBIDDEN_NAMES or f.suffix.lower() in FORBIDDEN_SUFFIX:
                findings.append(C.Finding(CHECK, "forbidden-file:" + rel, "forbidden file in skill tree", rel))
            if size > C.MAX_ASSET_BYTES:
                findings.append(C.Finding(CHECK, "large-file:" + rel,
                                          format(size / 1048576, ".1f") + " MB exceeds the 1 MB per-file budget", rel))
            if "assets" in f.parts and f.suffix.lower() in RASTER_SUFFIX:
                non_webp += 1
        if total > C.MAX_SKILL_BYTES:
            findings.append(C.Finding(CHECK, "skill-size:" + skill.name,
                                      "skill is " + format(total / 1048576, ".1f") + " MB (max 5 MB)", C.rel(skill)))
        if non_webp:
            findings.append(C.Finding(CHECK, "non-webp-assets:" + skill.name,
                                      str(non_webp) + " raster asset(s) under assets/ are not WebP",
                                      C.rel(skill / "assets")))
    largest.sort(reverse=True)
    print("check_assets: " + str(len(skills)) + " skill package(s)")
    for size, rel in largest[:5]:
        print("  largest: " + rel + " (" + format(size / 1024, ".0f") + " KB)")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
