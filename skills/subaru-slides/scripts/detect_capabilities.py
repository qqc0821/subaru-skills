#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Probe runtime capabilities for the subaru-slides skill.

Prints what is available and recommends an execution path:
  A         native editable builder (artifact-tool / python-pptx)
  B2        hybrid: image generation + native editable text
  C         HTML deck runtime or HTML->PPTX converter
  B         full AI visual (image generation only)
  fallback  image-only assembly via scripts/create_slides.py

Standard library only. No network.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

DECK_STAGE_HINTS = [
    HOME / ".agents" / "skills" / "baoyu-design" / "starter-components" / "deck-stage.js",
    HOME / ".claude" / "skills" / "baoyu-design" / "starter-components" / "deck-stage.js",
]
IMAGEGEN_HINTS = [
    HOME / ".codex" / "skills" / ".system" / "imagegen",
    HOME / ".claude" / "skills" / "imagegen",
]
# Renderer binaries bundled by host runtimes into a bin/override directory.
# Globs are home-relative and resolved at runtime; nothing is hard-coded to a user.
SOFFICE_HOME_GLOBS = [
    ".cache/codex-runtimes/*/dependencies/bin/override/soffice",
    ".cache/codex-runtimes/*/dependencies/bin/soffice",
]
PDFTOPPM_HOME_GLOBS = [
    ".cache/codex-runtimes/*/dependencies/bin/override/pdftoppm",
    ".cache/codex-runtimes/*/dependencies/bin/pdftoppm",
]


def which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def locate_binary(names, home_globs=()):
    """PATH first, then runtime-probed home cache overrides."""
    found = which(*names)
    if found:
        return found
    for pattern in home_globs:
        for candidate in sorted(HOME.glob(pattern)):
            if candidate.is_file():
                return str(candidate)
    return None


def has_module(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def find_first(paths):
    for p in paths:
        if p.exists():
            return str(p)
    return None


def search_for(filename: str, roots, limit: int = 20):
    for root in roots:
        if not Path(root).is_dir():
            continue
        try:
            for i, child in enumerate(Path(root).rglob(filename)):
                if i >= limit:
                    break
                return str(child)
        except OSError:
            continue
    return None


def node_has(module: str) -> bool:
    node = which("node")
    if not node:
        return False
    code = "try{require.resolve('" + module + "');process.stdout.write('yes')}catch(e){process.stdout.write('no')}"
    try:
        p = subprocess.run([node, "-e", code], capture_output=True, text=True, timeout=10)
        return p.stdout.strip() == "yes"
    except Exception:
        return False


def node_modules_have(module: str) -> bool:
    roots = []
    for var in ("RUNTIME_NODE_MODULES", "NODE_PATH"):
        val = os.environ.get(var)
        if val:
            roots.extend(val.split(os.pathsep))
    for root in roots:
        if (Path(root) / module / "package.json").is_file():
            return True
    return False


def detect():
    node = which("node")
    return {
        "python": sys.version.split()[0],
        "uv": which("uv"),
        "node": node,
        "npm": which("npm"),
        "soffice": locate_binary(("soffice", "libreoffice"), SOFFICE_HOME_GLOBS),
        "pdftoppm": locate_binary(("pdftoppm",), PDFTOPPM_HOME_GLOBS),
        "chrome": which("google-chrome", "chromium", "chromium-browser"),
        "python_pptx": has_module("pptx"),
        "pillow": has_module("PIL.Image"),
        "artifact_tool": (node_has("@oai/artifact-tool") if node else False) or node_modules_have("@oai/artifact-tool"),
        "deck_stage": find_first(DECK_STAGE_HINTS) or search_for("deck-stage.js", [HOME / ".agents" / "skills", HOME / ".claude" / "skills"]),
        "html2pptx": search_for("html2pptx.js", [HOME / ".agents" / "skills", HOME / ".claude" / "skills"]),
        "imagegen": find_first(IMAGEGEN_HINTS),
        "create_slides_py": str(SCRIPT_DIR / "create_slides.py") if (SCRIPT_DIR / "create_slides.py").is_file() else None,
    }


def recommend(caps):
    native = bool(caps.get("artifact_tool") or caps.get("python_pptx"))
    image = bool(caps.get("imagegen"))
    html = bool(caps.get("deck_stage") or caps.get("html2pptx"))
    if native:
        return "A", "native editable builder; add image generation only when the selected design needs it"
    if html:
        return "C", "HTML deck runtime or converter"
    if image:
        return "B", "image generation only; text will be baked into images"
    return "fallback", "image-only assembly via scripts/create_slides.py"


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe runtime capabilities and recommend a path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    caps = detect()
    path, reason = recommend(caps)
    if args.json:
        print(json.dumps({"capabilities": caps, "recommended_path": path, "reason": reason}, ensure_ascii=False, indent=2))
        return 0
    print("subaru-slides capability probe")
    for k, v in caps.items():
        mark = "OK " if v else "-- "
        print("  " + mark + k + ": " + (str(v) if v else "not found"))
    print("")
    print("recommended path: " + path)
    print("reason: " + reason)
    print("")
    print("order: A -> B2 -> C -> B -> fallback")
    return 0


if __name__ == "__main__":
    sys.exit(main())
