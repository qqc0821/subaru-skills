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
SAMPLE_DIR = Path("assets/style-samples")
FOUNDATION_PATH = Path("styles/foundation.json")


def validate_foundation(skill: Path, foundation_path: Path):
    findings = []
    rel = C.rel(foundation_path)
    try:
        data = json.loads(C.read_text(foundation_path))
    except json.JSONDecodeError as exc:
        return [C.Finding(CHECK, "bad-foundation-json:" + skill.name,
                          "styles/foundation.json is invalid JSON: " + str(exc), rel)]
    for key in ("schema_version", "default_profile", "profiles", "cjk", "layout", "accessibility", "autofit"):
        if key not in data:
            findings.append(C.Finding(CHECK, "foundation-missing:" + skill.name + ":" + key,
                                      "styles/foundation.json is missing " + key, rel))
    profiles = data.get("profiles")
    default = data.get("default_profile")
    if isinstance(profiles, dict) and default and default not in profiles:
        findings.append(C.Finding(CHECK, "foundation-default-profile:" + skill.name,
                                  "default_profile is not declared in profiles", rel))
    if isinstance(profiles, dict):
        for name, profile in profiles.items():
            roles = profile.get("text_roles", {}) if isinstance(profile, dict) else {}
            for role in ("slide-title", "body", "diagram-node", "footnote"):
                if role not in roles:
                    findings.append(C.Finding(CHECK, "foundation-role:" + skill.name + ":" + name + ":" + role,
                                              "profile " + name + " is missing text role " + role, rel))
    return findings


def validate_index(skill: Path, index_path: Path):
    findings = []
    rel = C.rel(index_path)
    try:
        data = json.loads(C.read_text(index_path))
    except json.JSONDecodeError as exc:
        findings.append(C.Finding(CHECK, "bad-json:" + skill.name,
                                  "styles/index.json is invalid JSON: " + str(exc), C.rel(index_path)))
        return findings
    foundation = data.get("foundation")
    if foundation != FOUNDATION_PATH.as_posix():
        findings.append(C.Finding(CHECK, "foundation-path:" + skill.name,
                                  "foundation must be " + FOUNDATION_PATH.as_posix(), rel))
    else:
        foundation_path = skill / foundation
        if not foundation_path.is_file():
            findings.append(C.Finding(CHECK, "missing-foundation:" + skill.name,
                                      "foundation not found: " + foundation, rel))
        else:
            findings.extend(validate_foundation(skill, foundation_path))
    styles = data.get("styles")
    if not isinstance(styles, list):
        findings.append(C.Finding(CHECK, "styles-not-list:" + skill.name, "styles must be an array", rel))
        return findings
    count = data.get("count")
    if count != len(styles):
        findings.append(C.Finding(CHECK, "count-mismatch:" + skill.name,
                                  "count=" + str(count) + " but styles has " + str(len(styles)) + " entries", rel))
    ids = []
    expected_samples = set()
    for i, style in enumerate(styles):
        sid = style.get("id")
        if not sid:
            findings.append(C.Finding(CHECK, "missing-id:" + skill.name + ":" + str(i), "style entry missing id", rel))
            continue
        ids.append(sid)
        sample = style.get("sample")
        expected_sample = (SAMPLE_DIR / (sid + ".webp")).as_posix()
        if sample:
            if sample != expected_sample:
                findings.append(C.Finding(
                    CHECK,
                    "noncanonical-sample:" + skill.name + ":" + sid,
                    "sample must be " + expected_sample + ", got " + str(sample),
                    rel,
                ))
            else:
                expected_samples.add(Path(sample).name)
            if not (skill / sample).resolve().exists():
                findings.append(C.Finding(CHECK, "missing-sample:" + skill.name + ":" + sid,
                                          "sample not found: " + sample, rel))

        preset = style.get("preset")
        if not preset:
            continue
        preset_path = skill / preset
        if not preset_path.is_file():
            findings.append(C.Finding(CHECK, "missing-preset:" + skill.name + ":" + sid,
                                      "preset not found: " + str(preset), rel))
            continue
        frontmatter, _ = C.parse_frontmatter(C.read_text(preset_path))
        preset_sample = frontmatter.get("sample")
        if preset_sample == "null":
            preset_sample = None
        if preset_sample != sample:
            findings.append(C.Finding(
                CHECK,
                "preset-sample-mismatch:" + skill.name + ":" + sid,
                "preset sample must match styles/index.json",
                C.rel(preset_path),
            ))
    dupes = {x for x in ids if ids.count(x) > 1}
    for d in sorted(dupes):
        findings.append(C.Finding(CHECK, "duplicate-id:" + skill.name + ":" + d, "duplicate style id: " + d, rel))
    for rec in data.get("theme_recommendations", []):
        for slot in ("first", "second", "third"):
            ref = rec.get(slot)
            if ref and ref not in ids:
                findings.append(C.Finding(CHECK, "unknown-recommendation:" + skill.name + ":" + str(rec.get("theme")) + ":" + slot,
                                      "theme recommendation references unknown id: " + ref, rel))
    sample_dir = skill / SAMPLE_DIR
    if sample_dir.is_dir():
        actual_samples = {f.name for f in sample_dir.iterdir() if f.is_file()}
        for name in sorted(actual_samples - expected_samples):
            findings.append(C.Finding(
                CHECK,
                "unexpected-sample:" + skill.name + ":" + name,
                "style sample is not registered as a canonical <style-id>.webp path",
                C.rel(sample_dir / name),
            ))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the machine-readable style system")
    C.add_common_args(parser)
    args = parser.parse_args()
    findings = []
    count = 0
    for skill in C.iter_skill_dirs():
        samples = skill / SAMPLE_DIR
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
