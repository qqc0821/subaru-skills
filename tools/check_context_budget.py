#!/usr/bin/env python3
"""Keep the skill's context cost from creeping back up.

`make check` already proves the package is *correct*; it says nothing about how
much context an agent must load to use it. That is how the earlier bloat
happened: `styles/index.json` was the required style read (2 947 tokens, mostly
verifier-only metadata) and two large references were advertised as required.

This check makes the cost visible and regresses on it:

  1. the declared required path stays inside a fixed token budget;
  2. no single required file is large enough to dominate that budget;
  3. the host-only design references never move back into the required path;
  4. the generated style router stays smaller than the registry it summarizes.

Token counts are estimates (CJK needs ~1.6 chars/token, ASCII ~3.6), which is
precise enough for a budget: it is a regression tripwire, not a meter.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

CHECK = "check_context_budget"
PROFILES = json.loads((Path(__file__).with_name("context-budgets.json")).read_text(encoding="utf-8"))
SKILL_NAME = "subaru-slides"
SLIDES = PROFILES[SKILL_NAME]
# Compatibility aliases for callers measuring the existing slides path.
REQUIRED_PATH = tuple(SLIDES["paths"]["default"])
REQUIRED_BUDGET = SLIDES["budgets"]["default"]
MAX_ENTRY_TOKENS = SLIDES["entry_limit"]
MAX_REQUIRED_FILE = SLIDES["file_limit"]
PRESET_GLOB = SLIDES["preset_glob"]
PRESET_EXCLUDE = set(SLIDES["preset_exclude"])
CONDITIONAL_TAG = "按需"
CONDITIONAL_ONLY = tuple(SLIDES["conditional"])
ROUTER_PAIR = tuple(SLIDES["router_pair"])
OPTIONAL_PATH = tuple(SLIDES["optional"])


def estimate(text: str) -> int:
    """Estimate tokens: CJK ~1.6 chars/token, everything else ~3.6."""
    cjk = len(re.findall(r"[\u3000-\u9fff\uff00-\uffef]", text))
    return int(cjk / 1.6 + (len(text) - cjk) / 3.6)


def cost(skill: Path, rel: str) -> int:
    path = skill / rel
    if not path.is_file():
        return -1
    return estimate(C.read_text(path))


def check_slides_skill(skill: Path, verbose: bool = True):
    """Return (findings, total, costs) for one skill directory."""
    findings = []
    if not (skill / "SKILL.md").is_file():
        return ([C.Finding(CHECK, "missing-entry",
                           "SKILL.md is missing; nothing to budget", C.rel(skill))], 0, {})

    costs = {}
    for rel in REQUIRED_PATH:
        value = cost(skill, rel)
        if value < 0:
            findings.append(C.Finding(CHECK, "missing-required:" + rel,
                                      "required path file is missing: " + rel, C.rel(skill / rel)))
        else:
            costs[rel] = value

    total = sum(costs.values())
    preset_costs = []
    for path in sorted(skill.glob(PRESET_GLOB)):
        rel = str(path.relative_to(skill))
        if rel in PRESET_EXCLUDE:
            continue
        value = cost(skill, rel)
        if value > 0:
            preset_costs.append((value, rel))
    worst_preset, worst_rel = max(preset_costs) if preset_costs else (0, "")
    if verbose:
        print("context budget: required path ~" + str(total) + " tokens / budget " + str(REQUIRED_BUDGET))
        for rel in sorted(costs, key=lambda r: -costs[r]):
            print("  " + str(costs[rel]).rjust(5) + "  " + rel)
        print("worst-case preset: " + worst_rel + " (~" + str(worst_preset) + "), worst total ~"
              + str(total - costs.get(SLIDES["preset_sample"], 0) + worst_preset))

    worst_total = total - costs.get(SLIDES["preset_sample"], 0) + worst_preset
    if worst_total > REQUIRED_BUDGET:
        findings.append(C.Finding(CHECK, "worst-preset-over-budget",
                                  "worst preset path costs ~" + str(worst_total)
                                  + " tokens, budget " + str(REQUIRED_BUDGET), C.rel(skill)))
    if total > REQUIRED_BUDGET:
        findings.append(C.Finding(
            CHECK, "required-path-over-budget",
            "declared required path costs ~" + str(total) + " tokens, budget is " + str(REQUIRED_BUDGET)
            + "; move detail into a reference that is read on demand",
            C.rel(skill / "SKILL.md")))

    for rel, value in costs.items():
        limit = MAX_ENTRY_TOKENS if rel == "SKILL.md" else MAX_REQUIRED_FILE
        if value > limit:
            findings.append(C.Finding(
                CHECK, "required-file-too-large:" + rel,
                rel + " costs ~" + str(value) + " tokens (> " + str(limit)
                + "); move detail into a reference that is read on demand", C.rel(skill / rel)))

    entry = C.read_text(skill / "SKILL.md")
    for rel in CONDITIONAL_ONLY:
        base = Path(rel).name
        tagged = any((rel in line or base in line) and CONDITIONAL_TAG in line
                     for line in entry.splitlines())
        if not tagged:
            findings.append(C.Finding(
                CHECK, "conditional-file-not-tagged:" + base,
                base + " is a conditional read but the entry does not mark it '" + CONDITIONAL_TAG + "'",
                C.rel(skill / "SKILL.md")))
    for lineno, line in enumerate(entry.splitlines(), start=1):
        if CONDITIONAL_TAG not in line or not line.lstrip().startswith("|"):
            continue
        base = ""
        match = re.match(r"\|\s*`?([^`|]+?)`?\s*\|", line)
        if match:
            base = Path(match.group(1).strip()).name
        if base and base.endswith(".md") and not any(
                Path(r).name == base for r in CONDITIONAL_ONLY):
            findings.append(C.Finding(
                CHECK, "required-file-mistagged:" + base,
                base + " is tagged '" + CONDITIONAL_TAG + "' but is not a known conditional read",
                C.rel(skill / "SKILL.md"), lineno))

    router_rel, registry_rel = ROUTER_PAIR
    router, registry = cost(skill, router_rel), cost(skill, registry_rel)
    if router > 0 and registry > 0 and router >= registry:
        findings.append(C.Finding(
            CHECK, "router-not-smaller:" + router_rel,
            router_rel + " (~" + str(router) + ") must stay smaller than " + registry_rel
            + " (~" + str(registry) + "); it exists to replace that read",
            C.rel(skill / router_rel)))

    return findings, total, costs


def check_profile(skill: Path, profile: dict, verbose: bool = True):
    """Check every declared route, with shared files counted once per route."""
    findings, costs, totals = [], {}, {}
    paths = profile["paths"]
    for route, files in paths.items():
        totals[route] = 0
        for rel in files:
            if rel not in costs:
                costs[rel] = cost(skill, rel)
                value = costs[rel]
                if value < 0:
                    findings.append(C.Finding(CHECK, skill.name + ":missing-required:" + rel,
                                              "declared route file is missing: " + rel, C.rel(skill / rel)))
                elif value > profile["entry_limit" if rel == "SKILL.md" else "file_limit"]:
                    findings.append(C.Finding(CHECK, skill.name + ":required-file-too-large:" + rel,
                                              "route file exceeds its token limit: " + rel, C.rel(skill / rel)))
            totals[route] += max(costs[rel], 0)
        limit = profile["budgets"][route]
        if totals[route] > limit:
            findings.append(C.Finding(CHECK, skill.name + ":route-over-budget:" + route,
                                      route + " costs ~" + str(totals[route]) + " tokens, budget " + str(limit),
                                      C.rel(skill / "SKILL.md")))
        if verbose:
            print(skill.name + " / " + route + ": ~" + str(totals[route]) + " tokens / " + str(limit))
    entry = C.read_text(skill / "SKILL.md") if (skill / "SKILL.md").is_file() else ""
    for rel in profile.get("conditional", []):
        # Require an actual linked reference, not a bare filename somewhere in the entry.
        target = re.escape(rel)
        if not any(CONDITIONAL_TAG in line and re.search(r"\]\(" + target + r"\)", line)
                   for line in entry.splitlines()):
            findings.append(C.Finding(CHECK, skill.name + ":conditional-file-not-tagged:" + rel,
                                      "conditional reference must be linked and tagged 按需: " + rel,
                                      C.rel(skill / "SKILL.md")))
    return findings, max(totals.values(), default=0), costs


def check_skill(skill: Path, verbose: bool = True):
    # Preserve the existing slides helper contract, including temporary test packages.
    if skill.name in PROFILES and skill.name != SKILL_NAME:
        return check_profile(skill, PROFILES[skill.name], verbose)
    return check_slides_skill(skill, verbose)


def optional_total(skill: Path) -> int:
    """Cost of the optional design reads an agent plausibly loads on top."""
    return sum(max(cost(skill, rel), 0) for rel in OPTIONAL_PATH)


def report(args) -> int:
    """Print the reproducible context accounting: required, optional and total."""
    skill = C.ROOT / "skills" / args.skill
    if args.skill != SKILL_NAME:
        _, _, costs = check_skill(skill)
        print("unique declared files: ~" + str(sum(max(v, 0) for v in costs.values())) + " tokens")
        return 0
    _, required, _ = check_skill(skill, verbose=False)
    optional = optional_total(skill)
    total = required + optional
    print("context accounting (estimated tokens)")
    print("  required path (entry + router + foundation + 1 path + 1 preset + QA): " + str(required))
    for rel in OPTIONAL_PATH:
        print("    optional " + str(max(cost(skill, rel), 0)).rjust(5) + "  " + rel)
    print("  optional design reads: " + str(optional))
    print("  total if all of the above load: " + str(total))
    print("  budget for the required path: " + str(REQUIRED_BUDGET))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce the skill's context budget")
    parser.add_argument("--report", action="store_true",
                        help="print the required/optional/total accounting and exit")
    parser.add_argument("--skill", choices=sorted(PROFILES), default=SKILL_NAME,
                        help="skill to inspect with --report (default: subaru-slides)")
    C.add_common_args(parser)
    args = parser.parse_args()

    if args.report:
        return report(args)
    findings = []
    for name in PROFILES:
        skill = C.ROOT / "skills" / name
        if not (skill / "SKILL.md").is_file():
            findings.append(C.Finding(CHECK, name + ":missing-entry", "configured skill entry is missing", C.rel(skill)))
            continue
        current, _, _ = check_skill(skill)
        findings.extend(current)
    for skill in C.iter_skill_dirs():
        if skill.name not in PROFILES:
            findings.append(C.Finding(CHECK, skill.name + ":missing-profile",
                                      "declare this skill's context paths in context-budgets.json", C.rel(skill)))
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
