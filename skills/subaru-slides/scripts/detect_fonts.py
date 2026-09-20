#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Probe CJK font candidates declared by the subaru-slides foundation.

The probe reports only what the current host can verify. It does not claim that a
recipient machine, PowerPoint Online or Google Slides will resolve the same font.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FOUNDATION = SKILL_DIR / "styles" / "foundation.json"


def host_platform() -> str:
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def load_foundation() -> dict:
    try:
        return json.loads(FOUNDATION.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("cannot read styles/foundation.json: " + str(exc)) from exc


def fontconfig_match(family: str) -> str | None:
    executable = shutil.which("fc-match")
    if not executable:
        return None
    try:
        proc = subprocess.run(
            [executable, "-f", "%{family}\\n", family],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else None


def same_family(requested: str, resolved: str | None) -> bool:
    if not resolved:
        return False
    wanted = requested.casefold().replace(" ", "")
    actual = resolved.casefold().replace(" ", "")
    return wanted == actual or wanted in actual or actual in wanted


def probe(locale: str, target_platform: str | None = None) -> dict:
    data = load_foundation()
    target = target_platform or host_platform()
    resolution = data.get("cjk", {}).get("font_resolution", {})
    candidates = []
    for source in ("portable", target):
        for family in resolution.get(source, []):
            if family not in candidates:
                candidates.append(family)
    rows = []
    for family in candidates:
        resolved = fontconfig_match(family)
        rows.append({"requested": family, "resolved": resolved, "available": same_family(family, resolved)})
    chosen = next((row["requested"] for row in rows if row["available"]), None)
    has_fontconfig = bool(shutil.which("fc-match"))
    return {
        "locale": locale,
        "host_platform": host_platform(),
        "target_platform": target,
        "foundation": str(FOUNDATION.relative_to(SKILL_DIR)),
        "fontconfig_available": has_fontconfig,
        "candidates": rows,
        "resolved_font": chosen,
        "status": "resolved" if chosen else ("unverified" if not has_fontconfig else "not-found"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe CJK font candidates for subaru-slides")
    parser.add_argument("--locale", default="zh-CN", help="BCP 47 text locale (default: zh-CN)")
    parser.add_argument("--target-platform", choices=["windows", "macos", "linux"],
                        help="resolve candidates for this recipient platform")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    parser.add_argument("--doctor", action="store_true", help="report probe availability and exit")
    args = parser.parse_args()
    try:
        result = probe(args.locale, args.target_platform)
    except RuntimeError as exc:
        print("detect_fonts: " + str(exc), file=sys.stderr)
        return 2
    if args.doctor:
        print("detect_fonts doctor")
        print("  foundation: " + result["foundation"])
        print("  fc-match: " + ("available" if result["fontconfig_available"] else "not found; results are unverified"))
        print("  host platform: " + result["host_platform"])
        return 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print("subaru-slides CJK font probe")
    print("  locale: " + result["locale"])
    print("  target platform: " + result["target_platform"])
    for row in result["candidates"]:
        mark = "OK " if row["available"] else "-- "
        print("  " + mark + row["requested"] + " -> " + (row["resolved"] or "unverified"))
    print("  resolved font: " + (result["resolved_font"] or result["status"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
