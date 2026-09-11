#!/usr/bin/env python3
"""Validate styles/index.json and verify sample files exist."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "check_style_system"


def validate_index(skill: Path, index_path: Path):
    findings = []
    try:
        data = json.loads(C.read_text(index_path))
    except json.JSONDecodeError as exc:
        findings.append(C.Finding(CHECK, "bad-json:" + skill.name,
                                  "styles/index.json is invalid JSON: " + str(exc), C.rel(index_path)))
        return findings
    rel = C.rel(index_path)
    styles = data.get("styles")
    if not isinstance(styles, list):
        findings.append(C.Finding(CHECK, "styles-not-list:" + skill.name, "styles must be an array", rel))
        return findings
    count = data.get("count")
    if count != len(styles):
        findings.append(C.Finding(CHECK, "count-mismatch:" + skill.name,
                                  "count=" + str(count) + " but styles has " + str(len(styles)) + " entries", rel))
    ids = []
    for i, style in enumerate(styles):
        sid = style.get("id")
        if not sid:
            findings.append(C.Finding(CHECK, "missing-id:" + skill.name + ":" + str(i), "style entry missing id", rel))
            continue
        ids.append(sid)
        sample = style.get("sample")
        if sample and not (skill / sample).resolve().exists():
            findings.append(C.Finding(CHECK, "missing-sample:" + skill.name + ":" + sid,
                                      "sample not found: " + sample, rel))
    dupes = {x for x in ids if ids.count(x) > 1}
    for d in sorted(dupes):
        findings.append(C.Finding(CHECK, "duplicate-id:" + skill.name + ":" + d, "duplicate style id: " + d, rel))
    for rec in data.get("theme_recommendations", []):
        for slot in ("first", "second", "third"):
            ref = rec.get(slot)
            if ref and ref not in ids:
                findings.append(C.Finding(CHECK, "unknown-recommendation:" + skill.name + ":" + str(rec.get("theme")) + ":" + slot,
                                          "theme recommendation references unknown id: " + ref, rel))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the machine-readable style system")
    C.add_common_args(parser)
    args = parser.parse_args()
    findings = []
    count = 0
    for skill in C.iter_skill_dirs():
        samples = skill / "assets" / "style-samples"
        index = skill / "styles" / "index.json"
        if samples.is_dir() and not index.is_file():
            findings.append(C.Finding(CHECK, "missing-index:" + skill.name,
                                      "assets/style-samples/ exists but styles/index.json is missing (AGENTS.md section 4)",
                                      C.rel(skill)))
        if index.is_file():
            count += 1
            findings.extend(validate_index(skill, index))
    print("check_style_system: " + str(count) + " styles/index.json file(s) found")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
