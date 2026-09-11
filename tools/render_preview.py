#!/usr/bin/env python3
"""Render a .pptx to per-slide PNG (or PDF) using LibreOffice + pdftoppm.

If no renderer is available, this exits 0 with a clear message: visual QA was skipped,
and the caller must not claim it was performed.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SOFFICE_CANDIDATES = [
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
]


def find_soffice():
    for name in ("soffice", "libreoffice"):
        p = shutil.which(name)
        if p:
            return p
    for c in SOFFICE_CANDIDATES:
        if Path(c).is_file():
            return c
    return None


def find_pdftoppm():
    return shutil.which("pdftoppm")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a PPTX to per-slide PNG/PDF")
    parser.add_argument("pptx", nargs="?")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--check", action="store_true", help="only report renderer availability")
    args = parser.parse_args()

    soffice = find_soffice()
    pdftoppm = find_pdftoppm()
    if args.check:
        print("render_preview: soffice=" + str(soffice) + "  pdftoppm=" + str(pdftoppm))
        return 0
    if not args.pptx:
        print("render_preview: pptx path required", file=sys.stderr)
        return 2
    if not soffice:
        print("render_preview: no renderer (soffice/libreoffice) found; visual QA skipped")
        return 0
    src = Path(args.pptx).resolve()
    if not src.is_file():
        print("render_preview: file not found: " + str(src), file=sys.stderr)
        return 2
    out_dir = Path(args.out_dir).resolve() if args.out_dir else src.parent / (src.stem + "_preview")
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(src)], check=False)
        pdfs = list(Path(tmp).glob("*.pdf"))
        if not pdfs:
            print("render_preview: LibreOffice failed to produce a PDF", file=sys.stderr)
            return 1
        target_pdf = out_dir / (src.stem + ".pdf")
        shutil.copyfile(pdfs[0], target_pdf)
    print("render_preview: pdf -> " + str(target_pdf))
    if not pdftoppm:
        print("render_preview: pdftoppm not found; PDF only (PNG step skipped)")
        return 0
    prefix = out_dir / "slide"
    subprocess.run([pdftoppm, "-png", "-r", str(args.dpi), str(target_pdf), str(prefix)], check=False)
    pngs = sorted(out_dir.glob("slide*.png"))
    print("render_preview: " + str(len(pngs)) + " PNG(s) -> " + str(out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
