#!/usr/bin/env python3
"""Inspect a .pptx with the standard library and return structural metrics.

Used by the eval harness and (later) by a deck validator.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

PLACEHOLDER_PATTERNS = [
    "lorem", "ipsum", "chart title", "xxxx", "todo", "placeholder", "占位", "单击此处添加",
]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _read_xml(zf, name):
    try:
        return ET.fromstring(zf.read(name))
    except (KeyError, ET.ParseError):
        return None


def _slide_key(name: str):
    m = re.search(r"slide(\d+)\.xml$", name)
    return int(m.group(1)) if m else 0


def _is_cjk(ch: str) -> bool:
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF) or (0x3400 <= o <= 0x4DBF) or (0x3000 <= o <= 0x303F) or (0xFF00 <= o <= 0xFFEF)


def inspect(path: str) -> dict:
    metrics = {
        "file": path,
        "slide_count": 0,
        "chart_count": 0,
        "table_count": 0,
        "image_count": 0,
        "text_chars": 0,
        "cjk_chars": 0,
        "font_families": [],
        "placeholders": [],
        "notes_slide_count": 0,
    }
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        presentation = _read_xml(zf, "ppt/presentation.xml")
        if presentation is not None:
            metrics["slide_count"] = sum(1 for el in presentation.iter() if _local(el.tag) == "sldId")
        slide_names = sorted((n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)), key=_slide_key)
        fonts = set()
        texts = []
        for name in slide_names:
            root = _read_xml(zf, name)
            if root is None:
                continue
            for el in root.iter():
                tag = _local(el.tag)
                if tag == "tbl":
                    metrics["table_count"] += 1
                elif tag == "t" and el.text:
                    texts.append(el.text)
                elif tag in ("latin", "ea", "cs"):
                    tf = el.get("typeface")
                    if tf:
                        fonts.add(tf)
        full_text = "\n".join(texts)
        metrics["text_chars"] = len(full_text)
        metrics["cjk_chars"] = sum(1 for ch in full_text if _is_cjk(ch))
        metrics["font_families"] = sorted(fonts)
        low = full_text.lower()
        metrics["placeholders"] = sorted({p for p in PLACEHOLDER_PATTERNS if p in low})
        metrics["chart_count"] = sum(1 for n in names if re.search(r"charts?/chart\d+\.xml$", n))
        metrics["image_count"] = sum(1 for n in names if n.startswith("ppt/media/"))
        metrics["notes_slide_count"] = sum(1 for n in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n))
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a .pptx and print structural metrics")
    parser.add_argument("pptx")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    metrics = inspect(args.pptx)
    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    else:
        for k, v in metrics.items():
            print(k + ": " + str(v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
