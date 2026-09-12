#!/usr/bin/env python3
"""Validate what actually gets published to skill consumers.

`make check` validates the skill as part of this repository. Consumers instead
receive only `skills/<name>/` and run it standalone, so this check guards that
boundary:

  1. the package has the files a consumer needs to load it (SKILL.md + frontmatter)
     and its directory name matches the frontmatter name;
  2. no skill file depends on repository-only paths (tools/, schemas/, evals/,
     tests/), which would break once the package is installed on its own.

File-size and asset budgets are intentionally left to check_assets.py.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

CHECK = "check_installability"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# A published skill must not reach into the repository it was cut from.
REPO_ONLY_PATTERNS = (
    (re.compile(r"\.\./\.\./(tools|schemas|evals|tests)/"), "references repository-only ../{0}/"),
    (re.compile(r"(?<![\w/])tools/[a-z_]+\.py"), "references repository-only tools/ script"),
    (re.compile(r"(?<![\w/])schemas/[a-z._]+\.json"), "references repository-only schemas/ file"),
)
SCAN_SUFFIXES = {".md", ".py", ".json", ".sh", ".mjs", ".yaml", ".yml"}

# Documentation legitimately mentions repository-only tooling for developers working
# inside this repository. Such passages are wrapped in these markers and skipped.
REPO_ONLY_OPEN = "<!-- repo-only -->"
REPO_ONLY_CLOSE = "<!-- /repo-only -->"


def _strip_repo_only(text: str) -> str:
    out, keep = [], True
    for line in text.splitlines():
        if REPO_ONLY_OPEN in line:
            keep = False
            continue
        if REPO_ONLY_CLOSE in line:
            keep = True
            continue
        if keep:
            out.append(line)
    return "\n".join(out)


def _package_files(pkg: Path) -> list:
    return [p for p in pkg.rglob("*") if p.is_file() and "__pycache__" not in p.parts]


def check_skill(pkg: Path) -> list:
    findings = []
    name = pkg.name

    if not NAME_RE.match(name):
        findings.append(C.Finding(CHECK, name + ":bad-name",
                                  "skill directory name is not installable (" + name + ")", C.rel(pkg)))

    skill_md = pkg / "SKILL.md"
    if not skill_md.is_file():
        findings.append(C.Finding(CHECK, name + ":missing-skill-md",
                                  "SKILL.md is required for a consumer to load the skill", C.rel(pkg)))
    else:
        fm, _ = C.parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        fm_name = (fm or {}).get("name")
        if fm_name != name:
            findings.append(C.Finding(CHECK, name + ":frontmatter-name-mismatch",
                                      "frontmatter name '" + str(fm_name) + "' != directory '" + name + "'",
                                      C.rel(skill_md)))

    for path in _package_files(pkg):
        if path.suffix not in SCAN_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if REPO_ONLY_OPEN in text:
            text = _strip_repo_only(text)
        for pattern, message in REPO_ONLY_PATTERNS:
            match = pattern.search(text)
            if match:
                detail = message.format(*match.groups()) if "{0}" in message else message
                findings.append(C.Finding(CHECK, name + ":repo-only-dependency:" + path.name,
                                          path.name + " " + detail, C.rel(path)))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Installability checks for published skill packages")
    C.add_common_args(parser)
    args = parser.parse_args()

    skills = C.iter_skill_dirs()
    if not skills:
        print("check_installability: no skill packages found under skills/", file=sys.stderr)
        return 1

    findings = []
    for pkg in skills:
        findings.extend(check_skill(pkg))

    print("check_installability: " + str(len(skills)) + " skill package(s) checked for standalone install")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
