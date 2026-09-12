#!/usr/bin/env python3
"""Probe the capabilities the subaru-slides skill can use."""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import renderer_locate as R  # noqa: E402


def has_module(name: str) -> bool:
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def detect():
    return {
        "python": sys.version.split()[0],
        "uv": shutil.which("uv"),
        "node": shutil.which("node"),
        "npm": shutil.which("npm"),
        "make": shutil.which("make"),
        "soffice": R.find_soffice(),
        "pdftoppm": R.find_pdftoppm(),
        "chrome": shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser"),
        "python_pptx": has_module("pptx"),
        "pillow": has_module("PIL.Image"),
        "git": shutil.which("git"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Environment capability probe")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    caps = detect()
    if args.json:
        print(json.dumps(caps, ensure_ascii=False, indent=2))
    else:
        print("subaru-skills capability probe")
        for k, v in caps.items():
            mark = "OK " if v else "-- "
            print("  " + mark + k + ": " + (str(v) if v else "not found"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
