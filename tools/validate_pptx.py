#!/usr/bin/env python3
"""Validate a .pptx with the standard library.

Structural issues (blank slide, out-of-bounds shape, placeholder text) are errors.
Heuristic layout estimates (text overflow, mixed fonts, CJK font metadata and
diagram geometry) are warnings.  They are intentionally conservative: the
validator flags a likely defect for visual review, rather than claiming to be a
PowerPoint renderer.

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


def parse_shape_metadata(name: str | None) -> dict[str, str]:
    """Parse optional semantic metadata from a PowerPoint shape name.

    Example: ``role=node;group=journey;index=01``.  Ordinary shape names are
    ignored, so decks not authored with subaru-slides stay compatible.
    """
    if not name or "=" not in name or not name.strip().startswith("role="):
        return {}
    metadata = {}
    for part in name.split(";"):
        key, sep, value = part.partition("=")
        if sep and key.strip() and value.strip():
            metadata[key.strip()] = value.strip()
    return metadata


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
    sizes = []
    has_east_asian = False
    has_language = False
    for node in el.iter():
        t = _local(node.tag)
        if t == "t" and node.text:
            texts.append(node.text)
        elif t in ("latin", "ea", "cs"):
            tf = node.get("typeface")
            if tf:
                fonts.add(tf)
            if t == "ea" and tf:
                has_east_asian = True
        elif t == "rPr" and node.get("sz"):
            try:
                sizes.append(int(node.get("sz")) / 100.0)
            except ValueError:
                pass
        if t == "rPr" and node.get("lang"):
            has_language = True
    return " ".join(texts), fonts, sizes, has_east_asian, has_language


def _shape_name(el):
    for node in el.iter():
        if _local(node.tag) == "cNvPr":
            return node.get("name", "")
    return ""


def _shape_kind(el):
    for node in el.iter():
        if _local(node.tag) == "prstGeom":
            return node.get("prst", "")
    return _local(el.tag)


def _objects(root):
    objs = []
    for el in root.iter():
        if _local(el.tag) not in ("sp", "pic", "graphicFrame"):
            continue
        text, fonts, sizes, has_ea, has_lang = _text_fonts(el)
        objs.append({
            "bbox": _bbox(el), "text": text, "fonts": fonts,
            "sizes": sizes, "has_ea": has_ea, "has_lang": has_lang,
            "autofit": any(_local(node.tag) == "normAutofit" for node in el.iter()),
            "metadata": parse_shape_metadata(_shape_name(el)),
            "kind": _shape_kind(el),
        })
    return objs


def check_slide(idx, objs, slide_cx, slide_cy):
    out = []
    if not objs:
        out.append(("error", "blank-slide:" + str(idx), "slide " + str(idx) + " has no content"))
        return out
    fonts_all = set()
    node_groups = {}
    geometry_seen = {}
    for i, o in enumerate(objs):
        bbox = o["bbox"]
        if bbox:
            x, y, cx, cy = bbox
            if x < 0 or y < 0 or x + cx > slide_cx or y + cy > slide_cy:
                out.append(("error", "out-of-bounds:" + str(idx) + ":" + str(i),
                            "shape " + str(i) + " on slide " + str(idx) + " exceeds slide bounds"))
            if o["text"].strip() and cx > 0 and cy > 0:
                # Explicit runs are authoritative.  18pt is a conservative
                # estimate when inherited text formatting is not in slide XML.
                sz = max(o["sizes"], default=18.0)
                cjk_ratio = sum(1 for ch in o["text"] if _is_cjk(ch)) / max(1, len(o["text"]))
                factor = 1.0 if cjk_ratio > 0.5 else 0.55
                cpl = max(1, int(cx / (sz * EMU_PER_PT * factor)))
                lines = max(1, math.ceil(len(o["text"]) / cpl))
                needed = lines * sz * 1.25 * EMU_PER_PT
                if needed > cy * 1.25:
                    out.append(("warning", "text-overflow:" + str(idx) + ":" + str(i),
                                "shape " + str(i) + " on slide " + str(idx) + " may overflow"))
        fonts_all |= o["fonts"]
        if any(_is_cjk(ch) for ch in o["text"]):
            if not o["has_ea"]:
                out.append(("warning", "cjk-missing-ea-font:" + str(idx) + ":" + str(i),
                            "CJK text on shape " + str(i) + " on slide " + str(idx)
                            + " has no East Asian font (a:ea)"))
            if not o["has_lang"]:
                out.append(("warning", "cjk-missing-language:" + str(idx) + ":" + str(i),
                            "CJK text on shape " + str(i) + " on slide " + str(idx)
                            + " has no language tag"))
        role = o["metadata"].get("role")
        group = o["metadata"].get("group")
        if o["sizes"] and role not in {"footnote", "source", "page-number"}:
            smallest = min(o["sizes"])
            minimum = 16.0 if role == "data-label" else 18.0
            if smallest < minimum:
                out.append(("warning", "font-below-minimum:" + str(idx) + ":" + str(i),
                            "shape " + str(i) + " on slide " + str(idx) + " uses "
                            + str(smallest) + "pt text below the " + str(minimum) + "pt "
                            + ("data-label" if role == "data-label" else "content") + " minimum"))
        if role == "node" and group:
            node_groups.setdefault(group, []).append((i, o))
        if role == "connector" and o["bbox"]:
            _x, _y, cx, cy = o["bbox"]
            diagonal_ok = o["metadata"].get("allowDiagonal", "").lower() == "true"
            if cx > 0 and cy > 0 and not diagonal_ok:
                out.append(("warning", "diagonal-connector:" + str(idx) + ":" + str(i),
                            "connector " + str(i) + " on slide " + str(idx)
                            + " is diagonal; use orthogonal routing or allowDiagonal=true"))
        if o["autofit"] and role not in {"footnote", "source", "page-number"}:
            out.append(("warning", "autofit-shrink:" + str(idx) + ":" + str(i),
                        "shape " + str(i) + " on slide " + str(idx)
                        + " uses normAutofit outside an allowed utility role"))
        if o["bbox"] and not o["text"].strip():
            geo_key = (o["kind"], o["bbox"])
            if geo_key in geometry_seen:
                prior = geometry_seen[geo_key]
                out.append(("warning", "duplicate-geometry:" + str(idx) + ":" + str(prior) + ":" + str(i),
                            "shapes " + str(prior) + " and " + str(i) + " on slide " + str(idx)
                            + " share the same empty " + o["kind"] + " geometry"))
            else:
                geometry_seen[geo_key] = i
        low = o["text"].lower()
        for p in PLACEHOLDER_PATTERNS:
            if p in low:
                out.append(("error", "placeholder:" + str(idx) + ":" + str(i),
                            "placeholder text '" + p + "' on slide " + str(idx)))
                break
    if len(fonts_all) > 1:
        out.append(("warning", "mixed-fonts:" + str(idx),
                    "slide " + str(idx) + " uses font families: " + str(sorted(fonts_all))))
    for group, nodes in node_groups.items():
        if len(nodes) < 2:
            continue
        bboxes = [node[1]["bbox"] for node in nodes]
        if not all(bboxes):
            continue
        sizes = {(box[2], box[3]) for box in bboxes}
        if len(sizes) > 1:
            out.append(("warning", "node-size-mismatch:" + str(idx) + ":" + group,
                        "node group '" + group + "' on slide " + str(idx)
                        + " contains inconsistent box sizes"))
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
