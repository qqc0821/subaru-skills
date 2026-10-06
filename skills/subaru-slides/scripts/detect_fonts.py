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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import typography as T

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
    return any(wanted == alias.casefold().replace(" ", "") for alias in resolved.split(","))


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


def probe_profile(profile_name=None, viewing_profile=None, text="", font_files=(),
                  font_dirs=(), include_system=True, config_path=None, target_platform=None) -> dict:
    foundation = load_foundation()
    config = T.read_json(Path(config_path) if config_path else SKILL_DIR / "typography/profiles.json")
    T.validate_configuration(foundation, config)
    name = profile_name or config["default_profile"]
    if name not in config["profiles"]:
        raise ValueError("unknown typography profile: " + name)
    sizes = T.resolve_viewing_profile(foundation, viewing_profile)
    profile = config["profiles"][name]
    files = T.discover_font_files(font_files, font_dirs, include_system)
    inventory, errors = [], []
    available = T.fonttools_available()
    if available:
        for file in files:
            try:
                inventory.extend(T.inspect_font_file(file))
            except Exception as exc:
                errors.append({"file": str(file), "reason": str(exc)})
    slots, policy, cache = {}, {}, {}

    def coverage(face, sample):
        key = (face["file"], face["face_index"], sample)
        if key not in cache:
            cache[key] = T.font_coverage(face, sample)
        return cache[key]

    for role in sizes:
        style = config.get("role_styles", {}).get(role, config["default_style"])
        slots[role], policy[role] = {}, {}

        def resolve(script):
            if script in slots[role]:
                return slots[role][script]
            setting = profile[script]
            families = list(setting.get("families", []))
            if "foundation" in setting:
                families += foundation["cjk"]["font_resolution"][setting["foundation"]]
            if setting.get("platform_fallback"):
                families += foundation["cjk"]["font_resolution"].get(target_platform or host_platform(), [])
            if "same_as" in setting:
                other = resolve(setting["same_as"])
                if other["resolved"]:
                    families.append(other["resolved"]["family"])
                elif not families:
                    families.append(other["requested"]["family"])
            families = list(dict.fromkeys(families))
            if not families:
                raise ValueError("empty resolved family list: " + name + "/" + script)
            result = T.choose_face(families, style, inventory, T.script_text(text, script), coverage, profile.get("style_fallbacks", {}).get(style, [])) if available else {
                "requested": {"family": families[0], "style": style}, "resolved": None,
                "coverage": {"status": "unverified"}, "fallback": {"used": False, "attempts": []},
                "status": "unverified"}
            slots[role][script] = result
            policy[role][script] = result["resolved"]["aliases"] if result["resolved"] else []
            return result

        resolve("ea")
        resolve("latin")
        if profile["latin"].get("include_ea"):
            policy[role]["latin"] = list(dict.fromkeys(policy[role]["latin"] + policy[role]["ea"]))
    policy["*"] = policy["body"]
    statuses = {slot["status"] for group in slots.values() for slot in group.values()}
    return {
        "schema_version": 1, "typography_profile": name,
        "host_platform": host_platform(), "target_platform": target_platform or host_platform(),
        "viewing_profile": viewing_profile or foundation["default_profile"],
        "status": "failed" if "failed" in statuses else ("unverified" if "unverified" in statuses else "resolved"),
        "fonttools_available": available, "inspected_files": len(files) if available else 0,
        "inspection_errors": errors, "sizes": sizes, "roles": slots,
        "font_policy": {"roles": policy},
        "verification": {"builder": "unverified", "final_pptx_render": "unverified",
                         "recipient_environment": "unverified", "embedding": "unverified"},
        "license": {"sources": config.get("sources", {}), "redistribution": "unverified", "embedding": "unverified"},
        "claim_boundary": "File metadata and supplied text coverage only; no font installation, rendering or remote verification.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe CJK font candidates for subaru-slides")
    parser.add_argument("--locale", default="zh-CN", help="BCP 47 text locale (default: zh-CN)")
    parser.add_argument("--target-platform", choices=["windows", "macos", "linux"],
                        help="resolve candidates for this recipient platform")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    parser.add_argument("--doctor", action="store_true", help="report probe availability and exit")
    parser.add_argument("--profile", help="resolve a typography profile, e.g. v5-reference")
    parser.add_argument("--viewing-profile", choices=["meeting-room", "large-room", "screen-reading"])
    parser.add_argument("--config", help="optional typography profile JSON")
    parser.add_argument("--text-file", help="UTF-8 deck text for glyph coverage")
    parser.add_argument("--font-file", action="append", default=[], help="additional font file (repeatable)")
    parser.add_argument("--font-dir", action="append", default=[], help="additional font directory (repeatable)")
    parser.add_argument("--no-system-fonts", action="store_true", help="inspect only supplied font files/directories")
    parser.add_argument("--output", help="write resolution receipt JSON")
    parser.add_argument("--policy-output", help="write the explicit font policy for PPTX validation")
    args = parser.parse_args()
    if args.profile or args.config or args.font_file or args.font_dir or args.text_file or args.viewing_profile or args.no_system_fonts or args.output or args.policy_output:
        try:
            result = probe_profile(args.profile, args.viewing_profile,
                                   Path(args.text_file).read_text(encoding="utf-8") if args.text_file else "",
                                   args.font_file, args.font_dir, not args.no_system_fonts, args.config, args.target_platform)
            if args.output:
                Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            if args.policy_output:
                Path(args.policy_output).write_text(json.dumps(result["font_policy"], ensure_ascii=False, indent=2), encoding="utf-8")
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("detect_fonts: " + result["typography_profile"] + " -> " + result["status"])
                for role, group in result["roles"].items():
                    for script, slot in group.items():
                        face = slot["resolved"]
                        print("  " + role + "/" + script + ": " + (face["family"] + " " + face["style"]
                              + " (weight=" + str(face["weight"]) + ")" if face else slot["status"])
                              + (" [declared fallback]" if slot["fallback"]["used"] else ""))
            return 1 if result["status"] == "failed" else 0
        except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
            print("detect_fonts: " + str(exc), file=sys.stderr)
            return 2
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
        print("  fontTools (optional): " + ("available" if T.fonttools_available() else "missing; file inspection unverified"))
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
