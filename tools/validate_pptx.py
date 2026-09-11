#!/usr/bin/env python3
"""Validate a .pptx with the standard library.

Structural issues (blank slide, out-of-bounds shape, placeholder text) are errors.
Heuristic layout estimates (text overflow, mixed fonts) are warnings.

Read-only and zero-dependency. Not a substitute for opening the file in PowerPoint.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

CHECK = "validate_pptx"
EMU_PER_PT = 12700
PLACEHOLDER_PATTERNS = ["lorem", "ipsum", "chart title", "xxxx", "todo", "placeholder", "占位", "单击此处添加"]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _read(zf, name):
    try:
        return ET.fromstring(zf.read(name))
    except (KeyError, ET.ParseError):
        return None


def _slide_key(name: str):
    m = re.search(r"slide(\d+)\.xml$", name)
    return int(m.group(1)) if m else 0


def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or 0xFF00 <= o <= 0xFFEF


def _slide_size(zf):
    root = _read(zf, "ppt/presentation.xml")
    if root is not None:
        for el in root.iter():
            if _local(el.tag) == "sldSz":
                return int(el.get("cx", 12192000)), int(el.get("cy", 6858000))
    return 12192000, 6858000


def _bbox(el):
    x = y = cx = cy = None
    for node in el.iter():
        t = _local(node.tag)
        if t == "off":
            x = int(node.get("x", 0))
            y = int(node.get("y", 0))
        elif t == "ext":
            cx = int(node.get("cx", 0))
            cy = int(node.get("cy", 0))
    if x is None or cx is None or cy is None:
        return None
    return x, y, cx, cy


def _text_fonts(el):
    texts = []
    fonts = set()
    max_sz = None
    for node in el.iter():
        t = _local(node.tag)
        if t == "t" and node.text:
            texts.append(node.text)
        elif t in ("latin", "ea", "cs"):
            tf = node.get("typeface")
            if tf:
                fonts.add(tf)
        elif t == "rPr" and node.get("sz"):
            try:
                sz = int(node.get("sz")) / 100.0
                max_sz = sz if max_sz is None else max(max_sz, sz)
            except ValueError:
                pass
    return " ".join(texts), fonts, (max_sz or 18.0)


def _objects(root):
    objs = []
    for el in root.iter():
        if _local(el.tag) not in ("sp", "pic", "graphicFrame"):
            continue
        text, fonts, sz = _text_fonts(el)
        objs.append({"bbox": _bbox(el), "text": text, "fonts": fonts, "sz": sz})
    return objs


def check_slide(idx, objs, slide_cx, slide_cy):
    out = []
    if not objs:
        out.append(("error", "blank-slide:" + str(idx), "slide " + str(idx) + " has no content"))
        return out
    fonts_all = set()
    for i, o in enumerate(objs):
        bbox = o["bbox"]
        if bbox:
            x, y, cx, cy = bbox
            if x < 0 or y < 0 or x + cx > slide_cx or y + cy > slide_cy:
                out.append(("error", "out-of-bounds:" + str(idx) + ":" + str(i),
                            "shape " + str(i) + " on slide " + str(idx) + " exceeds slide bounds"))
            if o["text"].strip() and cx > 0 and cy > 0:
                sz = o["sz"]
                cjk_ratio = sum(1 for ch in o["text"] if _is_cjk(ch)) / max(1, len(o["text"]))
                factor = 1.0 if cjk_ratio > 0.5 else 0.55
                cpl = max(1, int(cx / (sz * EMU_PER_PT * factor)))
                lines = max(1, math.ceil(len(o["text"]) / cpl))
                needed = lines * sz * 1.25 * EMU_PER_PT
                if needed > cy * 1.25:
                    out.append(("warning", "text-overflow:" + str(idx) + ":" + str(i),
                                "shape " + str(i) + " on slide " + str(idx) + " may overflow"))
        fonts_all |= o["fonts"]
        low = o["text"].lower()
        for p in PLACEHOLDER_PATTERNS:
            if p in low:
                out.append(("error", "placeholder:" + str(idx) + ":" + str(i),
                            "placeholder text '" + p + "' on slide " + str(idx)))
                break
    if len(fonts_all) > 1:
        out.append(("warning", "mixed-fonts:" + str(idx),
                    "slide " + str(idx) + " uses font families: " + str(sorted(fonts_all))))
    return out


def validate(path: str):
    findings = []
    with zipfile.ZipFile(path) as zf:
        slide_cx, slide_cy = _slide_size(zf)
        names = sorted((n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=_slide_key)
        findings.append(C.Finding(CHECK, "file:slide-count",
                                  "slides=" + str(len(names)) + " size=" + str(slide_cx) + "x" + str(slide_cy),
                                  path, 0, "info") if False else None)
        for idx, name in enumerate(names, start=1):
            root = _read(zf, name)
            if root is None:
                findings.append(C.Finding(CHECK, "unreadable:" + str(idx), "slide " + str(idx) + " is not parseable", path))
                continue
            for severity, key, message in check_slide(idx, _objects(root), slide_cx, slide_cy):
                findings.append(C.Finding(CHECK, key, message, path, 0, severity))
    return [f for f in findings if f is not None]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a .pptx (structural errors + heuristic warnings)")
    parser.add_argument("pptx")
    C.add_common_args(parser)
    args = parser.parse_args()
    if not Path(args.pptx).is_file():
        print("validate_pptx: file not found: " + args.pptx, file=sys.stderr)
        return 2
    findings = validate(args.pptx)
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]
    print("validate_pptx: " + args.pptx + " (" + str(len(errors)) + " error(s), " + str(len(warnings)) + " warning(s))")
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
