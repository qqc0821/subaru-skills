#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow>=10.0.0"]
# ///
"""Convert bitmap assets to WebP and report the size change.

Example:
    UV_CACHE_DIR=.uv-cache uv run tools/compress_assets.py \
        --dir skills/subaru-slides/assets/style-samples --quality 80 --remove-originals
"""
from __future__ import annotations

import argparse
from pathlib import Path

RASTER = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert bitmap assets to WebP")
    parser.add_argument("--dir", required=True)
    parser.add_argument("--quality", type=int, default=80)
    parser.add_argument("--max-width", type=int, default=0, help="downscale if wider than this (0 = keep)")
    parser.add_argument("--remove-originals", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    from PIL import Image

    root = Path(args.dir)
    if not root.is_dir():
        print("compress_assets: not a directory: " + str(root))
        return 2
    files = sorted(p for p in root.iterdir() if p.is_file() and p.suffix.lower() in RASTER)
    before = sum(p.stat().st_size for p in files)
    converted = []
    for p in files:
        out = p.with_suffix(".webp")
        if args.dry_run:
            print("would convert " + p.name + " -> " + out.name)
            continue
        img = Image.open(p).convert("RGB")
        if args.max_width and img.width > args.max_width:
            h = round(img.height * args.max_width / img.width)
            img = img.resize((args.max_width, h), Image.LANCZOS)
        img.save(out, "WEBP", quality=args.quality, method=6)
        converted.append(out)
        if args.remove_originals:
            p.unlink()
    after = sum(p.stat().st_size for p in root.iterdir() if p.is_file())
    print("compress_assets: " + str(len(converted)) + " converted, " + str(len(files)) + " source(s)")
    print("  before: " + str(round(before / 1048576, 2)) + " MB")
    print("  after:  " + str(round(after / 1048576, 2)) + " MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
