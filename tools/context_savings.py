#!/usr/bin/env python3
"""Reproducible before/after accounting for the subaru-slides context work.

The optimizations changed what an agent has to read, so the interesting number
is a *difference*, which is easy to mis-state and hard to re-verify by hand.
This script recomputes both sides from two trustworthy sources:

  before = `git show HEAD:<path>` for every file that existed before the work;
  after  = the working tree.

It reports the two layers separately, because they reduce different things:

  required path   -- paid on every run (entry, router, foundation, one path
                     reference, one preset, QA pair). Lowering this is what the
                     "(token)" complaint was about.
  optional design -- paid only when the agent also pulls design guidance
                     (prompt templates, design principles/movements). Lowering
                     this trims the ceiling and removes stale content.

Usage:
    python3 tools/context_savings.py [--baseline HEAD]

It is a reporting tool, not a gate: `check_context_budget.py` is what fails
`make check`. Counts are the same heuristic estimate used there.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402
from check_context_budget import (  # noqa: E402
    OPTIONAL_PATH,
    REQUIRED_PATH,
    SKILL_NAME,
    estimate,
)

# The two design references an agent most plausibly opens when it wants guidance.
DESIGN_READS = (
    "references/design-principles.md",
    "references/design-movements.md",
)


def committed(skill: Path, rel: str, baseline: str) -> int:
    """Cost of a file as of `baseline`; 0 when it did not exist yet.

    `git show` needs a repository-relative path, so rebuild it instead of passing
    the absolute skill path.
    """
    repo_rel = (Path("skills") / skill.name / rel).as_posix()
    result = subprocess.run(
        ["git", "show", baseline + ":" + repo_rel],
        capture_output=True, text=True, cwd=str(C.ROOT))
    return estimate(result.stdout) if result.returncode == 0 else 0


def current(skill: Path, rel: str) -> int:
    path = skill / rel
    return estimate(C.read_text(path)) if path.is_file() else 0


def pct(before: int, after: int) -> str:
    if before <= 0:
        return "n/a"
    return f"{(after - before) / before * 100:+.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description="Report context savings vs a git baseline")
    parser.add_argument("--baseline", default="HEAD", help="git revision to compare against")
    args = parser.parse_args()

    skill = C.ROOT / "skills" / SKILL_NAME
    if not (skill / "SKILL.md").is_file():
        print("context_savings: no skill at " + str(skill), file=sys.stderr)
        return 2

    print("subaru-slides context accounting (estimated tokens), baseline = " + args.baseline)
    print("")
    print(f"{'file':46s} {'before':>7} {'after':>7} {'delta':>8} {'%':>8}")

    required_before = required_after = 0
    # The registry read was replaced by the generated router, so compare them.
    pairs = [("styles/index.json -> styles/router.md", "styles/index.json", "styles/router.md")]
    pairs += [(rel, rel, rel) for rel in REQUIRED_PATH if rel != "styles/router.md"]
    for label, before_rel, after_rel in pairs:
        before, after = committed(skill, before_rel, args.baseline), current(skill, after_rel)
        required_before += before
        required_after += after
        print(f"{label:46s} {before:7d} {after:7d} {after - before:+8d} {pct(before, after):>8}")

    optional_before = optional_after = 0
    for rel in OPTIONAL_PATH:
        before, after = committed(skill, rel, args.baseline), current(skill, rel)
        optional_before += before
        optional_after += after
        print(f"{rel:46s} {before:7d} {after:7d} {after - before:+8d} {pct(before, after):>8}")

    print("")
    print(f"{'required path (every run)':46s} {required_before:7d} {required_after:7d} "
          f"{required_after - required_before:+8d} {pct(required_before, required_after):>8}")
    design_before = required_before + sum(committed(skill, r, args.baseline) for r in DESIGN_READS)
    design_after = required_after + sum(current(skill, r) for r in DESIGN_READS)
    print(f"{'+ 2 design references':46s} {design_before:7d} {design_after:7d} "
          f"{design_after - design_before:+8d} {pct(design_before, design_after):>8}")
    all_before = required_before + optional_before
    all_after = required_after + optional_after
    print(f"{'+ every optional read':46s} {all_before:7d} {all_after:7d} "
          f"{all_after - all_before:+8d} {pct(all_before, all_after):>8}")
    print("")
    print("scope: skill text only (entry, references, styles, one preset).")
    print("       excludes tool outputs, script bodies and generated slide content.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
