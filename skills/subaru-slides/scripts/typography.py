"""Shared typography configuration and optional font-file inspection.

No fonts are downloaded or installed. fontTools is optional; metadata and glyph
coverage remain unverified when unavailable. Rendering is a separate check.
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("cannot read " + str(path) + ": " + str(exc)) from exc
    if not isinstance(data, dict):
        raise ValueError(str(path) + " must contain an object")
    return data


def normalize(value: str) -> str:
    return "".join(value.casefold().split())


def is_east_asian(ch: str) -> bool:
    cp = ord(ch)
    return (0x3400 <= cp <= 0x9FFF or 0x3000 <= cp <= 0x303F
            or 0xF900 <= cp <= 0xFAFF or 0xFF00 <= cp <= 0xFFEF
            or 0x20000 <= cp <= 0x323AF)


def script_text(text: str, script: str) -> str:
    return "".join(ch for ch in text if not ch.isspace()
                   and unicodedata.category(ch)[0] != "C"
                   and is_east_asian(ch) == (script == "ea"))


def resolve_viewing_profile(foundation: dict, name: str | None = None) -> dict:
    name = name or foundation["default_profile"]
    profiles = foundation["profiles"]
    active = set()

    def visit(current):
        if current in active or current not in profiles:
            raise ValueError("unknown or cyclic viewing profile: " + str(current))
        active.add(current)
        p = profiles[current]
        parent = p.get("inherits")
        # Legacy profiles inherited the default implicitly.
        if parent is None and current != foundation["default_profile"]:
            parent = foundation["default_profile"]
        roles = visit(parent) if parent else {}
        roles.update({key: dict(value) for key, value in p["text_roles"].items()})
        active.remove(current)
        return roles

    roles = visit(name)
    aliases = foundation.get("role_aliases", {})
    for alias in aliases:
        current, seen = alias, set()
        while current in aliases:
            if current in seen:
                raise ValueError("cyclic role alias: " + alias)
            seen.add(current)
            current = aliases[current]
        if current not in roles:
            raise ValueError("unknown role alias target: " + str(current))
        roles[alias] = dict(roles[current])
    return roles


def validate_configuration(foundation: dict, config: dict) -> None:
    if config.get("schema_version") != 1 or not isinstance(config.get("profiles"), dict):
        raise ValueError("typography config requires schema_version=1 and profiles")
    if config.get("default_profile") not in config["profiles"]:
        raise ValueError("unknown default typography profile")
    for name in foundation["profiles"]:
        roles = resolve_viewing_profile(foundation, name)
        for role, limits in roles.items():
            low, high = limits.get("min_pt"), limits.get("max_pt")
            if not isinstance(low, (int, float)) or not isinstance(high, (int, float)) or not 0 < low <= high:
                raise ValueError("invalid size range: " + name + "/" + role)
    role_styles = config.get("role_styles", {})
    if not isinstance(role_styles, dict):
        raise ValueError("role_styles must be an object")
    styles = [config.get("default_style"), *role_styles.values()]
    if any(not isinstance(style, str) or not style.strip() for style in styles):
        raise ValueError("font styles must be non-empty face names")
    roles = resolve_viewing_profile(foundation)
    for role in role_styles:
        if role not in roles:
            raise ValueError("unknown typography role: " + role)
    for name, profile in config["profiles"].items():
        if not isinstance(profile, dict):
            raise ValueError("font profile must be an object: " + name)
        style_fallbacks = profile.get("style_fallbacks", {})
        if not isinstance(style_fallbacks, dict):
            raise ValueError("style_fallbacks must be an object: " + name)
        for script in ("ea", "latin"):
            slot = profile.get(script)
            if not isinstance(slot, dict) or not any(k in slot for k in ("families", "foundation", "same_as")):
                raise ValueError("missing font candidates: " + name + "/" + script)
            for flag in ("include_ea", "platform_fallback"):
                if flag in slot and not isinstance(slot[flag], bool):
                    raise ValueError("invalid font slot flag: " + name + "/" + flag)
            families = slot.get("families", [])
            if not isinstance(families, list) or ("families" in slot and not families) or any(not isinstance(f, str) or not f.strip() for f in families):
                raise ValueError("invalid family list: " + name)
            if "foundation" in slot and slot["foundation"] not in foundation["cjk"]["font_resolution"]:
                raise ValueError("unknown foundation font list: " + name)
            if "same_as" in slot and slot["same_as"] not in ("ea", "latin"):
                raise ValueError("unknown script reference: " + name)
        for primary, fallbacks in style_fallbacks.items():
            if not isinstance(primary, str) or not isinstance(fallbacks, list) or not fallbacks or any(not isinstance(f, str) or not f.strip() for f in fallbacks):
                raise ValueError("invalid style fallback: " + name)
        # Reject cycles even when a preferred family might resolve first.
        for script in ("ea", "latin"):
            current, seen = script, set()
            while "same_as" in profile[current]:
                if current in seen:
                    raise ValueError("cyclic script reference: " + name)
                seen.add(current)
                current = profile[current]["same_as"]


def fonttools_available() -> bool:
    try:
        import fontTools.ttLib  # noqa: F401
        return True
    except ImportError:
        return False


def inspect_font_file(path: Path) -> list[dict]:
    from fontTools.ttLib import TTCollection, TTFont
    collection = None
    if path.suffix.lower() in (".ttc", ".otc"):
        collection = TTCollection(str(path), lazy=True)
        fonts = collection.fonts
    else:
        fonts = [TTFont(str(path), lazy=True)]
    rows = []
    try:
        for index, font in enumerate(fonts):
            names = font["name"]
            aliases = sorted({record.toUnicode() for record in names.names
                              if record.nameID in (1, 16)})
            os2 = font.get("OS/2")
            rows.append({
                "family": names.getDebugName(16) or names.getDebugName(1),
                "aliases": aliases,
                "style": names.getDebugName(17) or names.getDebugName(2),
                "postscript_name": names.getDebugName(6),
                "version": names.getDebugName(5),
                "weight": os2.usWeightClass if os2 else None,
                "width": os2.usWidthClass if os2 else None,
                "italic": bool(os2.fsSelection & 1) if os2 else None,
                "embedding_flags": os2.fsType if os2 else None,
                "axes": {axis.axisTag: [axis.minValue, axis.defaultValue, axis.maxValue]
                         for axis in font["fvar"].axes} if "fvar" in font else {},
                "file": str(path.resolve()), "face_index": index,
            })
    finally:
        if collection:
            collection.close()
        else:
            fonts[0].close()
    return rows


def font_coverage(face: dict, text: str) -> dict:
    from fontTools.ttLib import TTFont
    font = TTFont(face["file"], fontNumber=face["face_index"], lazy=True)
    try:
        cmap = font.getBestCmap() or {}
        missing = sorted({ch for ch in text if ord(ch) not in cmap or cmap[ord(ch)] == ".notdef"})
        return {"status": "failed" if missing else "verified", "missing": missing,
                "tested_characters": len(set(text))}
    finally:
        font.close()


def discover_font_files(font_files=(), font_dirs=(), include_system=True) -> list[Path]:
    directories = [Path(p) for p in font_dirs]
    if include_system:
        if sys.platform == "darwin":
            # macOS may activate CJK collections from downloadable system assets.
            directories += list(Path("/System/Library/AssetsV2").glob("com_apple_MobileAsset_Font*/*/AssetData"))
            directories += [Path("/System/Library/Fonts"), Path("/Library/Fonts"), Path.home() / "Library/Fonts"]
        elif sys.platform.startswith("win"):
            import os
            directories += [Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
                            Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Microsoft/Windows/Fonts"]
        else:
            directories += [Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
                            Path.home() / ".local/share/fonts", Path.home() / ".fonts"]
    paths = {Path(p).resolve() for p in font_files}
    for directory in directories:
        if directory.is_dir():
            paths.update(p.resolve() for p in directory.rglob("*") if p.is_file()
                         and p.suffix.lower() in (".ttf", ".otf", ".ttc", ".otc"))
    return sorted(paths)


def choose_face(families: list[str], style: str, inventory: list[dict], text: str,
                coverage_reader=font_coverage, style_fallbacks=()) -> dict:
    attempts = []
    for actual_style in (style, *style_fallbacks):
        for family in families:
            faces = [f for f in inventory if normalize(family) in {normalize(a) for a in f["aliases"]}]
            matching = [f for f in faces if normalize(f["style"] or "") == normalize(actual_style)
                        and not f["axes"] and f["italic"] is not True and f["width"] in (None, 5)]
            if not matching:
                attempts.append({"family": family, "style": actual_style,
                                 "reason": "missing-static-face" if faces else "missing-family"})
                continue
            for face in matching:
                coverage = coverage_reader(face, text) if text else {"status": "unverified", "missing": [], "tested_characters": 0}
                if coverage["status"] == "failed":
                    attempts.append({"family": family, "style": actual_style, "reason": "missing-glyphs", "missing": coverage["missing"]})
                    continue
                return {"requested": {"family": families[0], "style": style}, "resolved": face,
                        "coverage": coverage, "fallback": {"used": family != families[0] or actual_style != style, "attempts": attempts},
                        "status": "verified"}
    return {"requested": {"family": families[0], "style": style}, "resolved": None,
            "coverage": {"status": "failed" if any(a["reason"] == "missing-glyphs" for a in attempts) else "unverified"},
            "fallback": {"used": False, "attempts": attempts}, "status": "failed"}
