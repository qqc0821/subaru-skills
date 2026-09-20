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
SKILL_NAME = "subaru-slides"

# The path an agent actually walks on a normal run: the entry, one style-routing
# read, one path file, one preset and the QA pair. Everything else is conditional
# and must not be counted here -- cold assets keep their selection value.
REQUIRED_PATH = (
    "SKILL.md",
    "styles/router.md",
    "styles/foundation.json",
    "styles/warm-comic-strip.md",
    "references/content-structure.md",
    "references/paths/path-b2-hybrid.md",
    "references/qa/render-and-validate.md",
    "references/qa/checklist.md",
)
# A style preset is always loaded; measure the worst case, not a lucky pick.
PRESET_GLOB = "styles/*.md"
PRESET_EXCLUDE = {"styles/router.md"}
REQUIRED_BUDGET = 6400
# The entry is allowed to be a real router, but not a dumping ground.
MAX_ENTRY_TOKENS = 2000
# Any other required read this large belongs in a conditional file.
MAX_REQUIRED_FILE = 1200
# Conditional reads: valuable on demand, must never be advertised as required.
# The entry marks them with this tag so the distinction is machine-checkable.
CONDITIONAL_TAG = "按需"
CONDITIONAL_ONLY = (
    "references/design-principles.md",
    "references/design-movements.md",
    "references/prompt-templates.md",
)
ROUTER_PAIR = ("styles/router.md", "styles/index.json")
# Optional-but-plausible reads: what an agent loads when it also wants design
# guidance. Tracked so the before/after accounting stays reproducible.
OPTIONAL_PATH = (
    "references/prompt-templates.md",
    "references/design-principles.md",
    "references/design-movements.md",
    "references/paths/path-a-native.md",
)


def estimate(text: str) -> int:
    """Estimate tokens: CJK ~1.6 chars/token, everything else ~3.6."""
    cjk = len(re.findall(r"[\u3000-\u9fff\uff00-\uffef]", text))
    return int(cjk / 1.6 + (len(text) - cjk) / 3.6)


def cost(skill: Path, rel: str) -> int:
    path = skill / rel
    if not path.is_file():
        return -1
    return estimate(C.read_text(path))


def check_skill(skill: Path, verbose: bool = True):
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
              + str(total - costs.get("styles/warm-comic-strip.md", 0) + worst_preset))

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


def optional_total(skill: Path) -> int:
    """Cost of the optional design reads an agent plausibly loads on top."""
    return sum(max(cost(skill, rel), 0) for rel in OPTIONAL_PATH)


def report(args) -> int:
    """Print the reproducible context accounting: required, optional and total."""
    skill = C.ROOT / "skills" / SKILL_NAME
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
    C.add_common_args(parser)
    args = parser.parse_args()

    skill = C.ROOT / "skills" / SKILL_NAME
    if not (skill / "SKILL.md").is_file():
        print("check_context_budget: no skill at " + str(skill), file=sys.stderr)
        return 2
    if args.report:
        return report(args)
    findings, total, costs = check_skill(skill)
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
