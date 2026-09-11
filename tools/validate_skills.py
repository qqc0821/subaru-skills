#!/usr/bin/env python3
"""Validate skill packages: frontmatter, agents/openai.yaml and budgets.

Mirrors schemas/skill.frontmatter.schema.json and schemas/openai-agent.schema.json.
Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "validate_skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def check_skill(skill: Path):
    findings = []
    name = skill.name
    skill_md = skill / "SKILL.md"
    text = C.read_text(skill_md)

    lines = text.count("\n") + 1
    if lines > C.MAX_SKILL_MD_LINES:
        findings.append(C.Finding(
            CHECK, name + ":skill-md-lines",
            "SKILL.md is " + str(lines) + " lines (max " + str(C.MAX_SKILL_MD_LINES) + "); move detail to references/",
            C.rel(skill_md)))

    fm, _ = C.parse_frontmatter(text)
    fm_name = str(fm.get("name", "")).strip()
    if not fm_name:
        findings.append(C.Finding(CHECK, name + ":missing-name", "frontmatter is missing name", C.rel(skill_md), 1))
    elif fm_name != name:
        findings.append(C.Finding(CHECK, name + ":name-mismatch",
                                  "frontmatter name '" + fm_name + "' != directory '" + name + "'", C.rel(skill_md), 1))
    elif not NAME_RE.match(fm_name):
        findings.append(C.Finding(CHECK, name + ":name-format",
                                  "name '" + fm_name + "' must be lowercase hyphenated", C.rel(skill_md), 1))

    desc = str(fm.get("description", "")).strip()
    if not desc:
        findings.append(C.Finding(CHECK, name + ":missing-description", "frontmatter is missing description", C.rel(skill_md), 1))
    else:
        if len(desc) < 10:
            findings.append(C.Finding(CHECK, name + ":description-short",
                                      "description is " + str(len(desc)) + " chars (min 10)", C.rel(skill_md), 1))
        if len(desc) > 1024:
            findings.append(C.Finding(CHECK, name + ":description-long",
                                      "description is " + str(len(desc)) + " chars (max 1024)", C.rel(skill_md), 1))
        if not re.search(r"使用|当|when|use|Use", desc):
            findings.append(C.Finding(CHECK, name + ":description-no-trigger",
                                      "description does not state when to use the skill", C.rel(skill_md), 1, "warning"))

    oy = skill / "agents" / "openai.yaml"
    if not oy.is_file():
        findings.append(C.Finding(CHECK, name + ":missing-openai", "agents/openai.yaml is missing", C.rel(skill)))
    else:
        data = C.parse_simple_yaml(C.read_text(oy))
        iface = data.get("interface") or {}
        policy = data.get("policy") or {}
        for field in ("display_name", "short_description", "brand_color", "default_prompt"):
            if not str(iface.get(field, "")).strip():
                findings.append(C.Finding(CHECK, name + ":openai-missing-" + field,
                                          "agents/openai.yaml interface." + field + " is missing", C.rel(oy)))
        bc = str(iface.get("brand_color", "")).strip()
        if bc and not re.match(r"^#[0-9A-Fa-f]{6}$", bc):
            findings.append(C.Finding(CHECK, name + ":openai-bad-brand-color",
                                      "brand_color '" + bc + "' is not #RRGGBB", C.rel(oy)))
        if "allow_implicit_invocation" not in policy:
            findings.append(C.Finding(CHECK, name + ":openai-missing-policy",
                                      "policy.allow_implicit_invocation is missing", C.rel(oy)))

    refs_dir = skill / "references"
    if refs_dir.is_dir():
        for ref in sorted(refs_dir.glob("**/*.md")):
            rlines = C.read_text(ref).count("\n") + 1
            if rlines > C.MAX_REFERENCE_LINES:
                findings.append(C.Finding(CHECK, name + ":reference-lines:" + ref.name,
                                          ref.name + " is " + str(rlines) + " lines (max " + str(C.MAX_REFERENCE_LINES) + ")",
                                          C.rel(ref), 0, "warning"))

    total = sum(f.stat().st_size for f in skill.rglob("*") if f.is_file())
    if total > C.MAX_SKILL_BYTES:
        findings.append(C.Finding(CHECK, name + ":package-size",
                                  "skill package is " + format(total / 1048576, ".1f") + " MB (max " + str(C.MAX_SKILL_BYTES // 1048576) + " MB)",
                                  C.rel(skill)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill packages")
    C.add_common_args(parser)
    args = parser.parse_args()
    findings = []
    skills = C.iter_skill_dirs()
    for skill in skills:
        findings.extend(check_skill(skill))
    print("validate_skills: " + str(len(skills)) + " skill package(s)")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
