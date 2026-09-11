#!/usr/bin/env python3
"""Consistency checks: stale external deps, contradictions, single-value rules."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "check_consistency"
FENCE = chr(96) * 3
FORBIDDEN = [
    ("external-skill-presentations", "$presentations"),
    ("external-skill-imagegen", "$imagegen"),
    ("external-skill-nano-banana", "nano-banana"),
    ("user-home-claude", "~/.claude"),
    ("absolute-user-path", "/Users/"),
    ("user-home-agents", "$HOME/.agents"),
    ("vendored-agents-skills", ".agents/skills"),
    ("upstream-identity-huashu", "huashu"),
    ("upstream-identity-alchaincyf", "alchaincyf"),
]


def skill_markdown_files():
    skills = C.ROOT / "skills"
    return sorted(skills.rglob("*.md")) if skills.is_dir() else []


def iter_lines(path, include_fences=False):
    in_fence = False
    for lineno, line in enumerate(C.read_text(path).splitlines(), start=1):
        s = line.lstrip()
        if s.startswith(FENCE) or s.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence and not include_fences:
            continue
        yield lineno, line


def main() -> int:
    parser = argparse.ArgumentParser(description="Consistency checks")
    C.add_common_args(parser)
    args = parser.parse_args()
    findings = []
    files = skill_markdown_files()

    for f in files:
        seen = set()
        for lineno, line in iter_lines(f):
            for rule_id, needle in FORBIDDEN:
                if needle in line and rule_id not in seen:
                    seen.add(rule_id)
                    findings.append(C.Finding(CHECK, "forbidden:" + C.rel(f) + ":" + rule_id,
                                              "hard dependency / stale reference: " + needle,
                                              C.rel(f), lineno))

    rules_path = Path(__file__).resolve().parent / "consistency-rules.json"
    rules = json.loads(C.read_text(rules_path))

    for rule in rules.get("single_value", []):
        rx = re.compile(rule["pattern"])
        values = {}
        for f in files:
            for lineno, line in iter_lines(f, include_fences=True):
                for m in rx.finditer(line):
                    values.setdefault(m.group(0), []).append(C.rel(f) + ":" + str(lineno))
        if len(values) > 1:
            detail = "; ".join(k + " (" + str(len(v)) + "x)" for k, v in sorted(values.items()))
            findings.append(C.Finding(CHECK, "rule:" + rule["id"], rule["message"] + ": " + detail,
                                      C.rel(rules_path)))

    for rule in rules.get("contradiction", []):
        rx_a = re.compile(rule["a"])
        rx_b = re.compile(rule["b"])
        hits_a, hits_b = [], []
        for f in files:
            for lineno, line in iter_lines(f):
                if rx_a.search(line):
                    hits_a.append(C.rel(f) + ":" + str(lineno))
                if rx_b.search(line):
                    hits_b.append(C.rel(f) + ":" + str(lineno))
        if hits_a and hits_b:
            findings.append(C.Finding(CHECK, "rule:" + rule["id"],
                                      rule["message"] + ": a@" + ",".join(hits_a) + " vs b@" + ",".join(hits_b)))

    print("check_consistency: scanned " + str(len(files)) + " skill Markdown file(s)")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
