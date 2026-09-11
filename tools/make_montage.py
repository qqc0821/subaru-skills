#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow>=10.0.0"]
# ///
"""Build a contact sheet from slide PNGs. Uses Pillow when available; otherwise reports and exits 0.

Run with `uv run tools/make_montage.py ...` to get Pillow automatically, or install Pillow yourself."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def natural_key(p: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a slide contact sheet")
    parser.add_argument("images", nargs="*")
    parser.add_argument("--input-dir")
    parser.add_argument("--out", default="montage.webp")
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument("--cell", type=int, default=640)
    parser.add_argument("--label", choices=["number", "filename", "none"], default="number")
    args = parser.parse_args()

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("make_montage: Pillow not installed; skipping (pip install Pillow)")
        return 0

    paths = [Path(p) for p in args.images]
    if args.input_dir:
        paths += sorted(Path(args.input_dir).glob("*.png"), key=natural_key)
    paths = [p for p in paths if p.is_file()]
    if not paths:
        print("make_montage: no images provided", file=sys.stderr)
        return 2

    cols = max(1, args.cols)
    rows = (len(paths) + cols - 1) // cols
    cell = args.cell
    sheet = Image.new("RGB", (cols * cell, rows * cell), "white")
    draw = ImageDraw.Draw(sheet)

    for i, p in enumerate(paths):
        col, row = i % cols, i // cols
        try:
            img = Image.open(p).convert("RGB")
        except Exception:
            continue
        img.thumbnail((cell - 16, cell - 16))
        x = col * cell + (cell - img.width) // 2
        y = row * cell + (cell - img.height) // 2
        sheet.paste(img, (x, y))
        if args.label == "number":
            draw.text((col * cell + 8, row * cell + 8), str(i + 1), fill="red")
        elif args.label == "filename":
            draw.text((col * cell + 8, row * cell + 8), p.name, fill="red")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print("make_montage: " + str(len(paths)) + " image(s) -> " + str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
