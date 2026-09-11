#!/usr/bin/env python3
"""Inspect a deck-stage HTML file with the Python standard library."""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PLACEHOLDER_PATTERNS = ["lorem", "ipsum", "xxxx", "todo", "placeholder", "占位"]


class DeckParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.stage_count = 0
        self.stage_width = None
        self.stage_height = None
        self.slide_count = 0
        self.labels = []
        self.scripts = []
        self.styles = []
        self.texts = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else None
        if tag == "deck-stage":
            self.stage_count += 1
            self.stage_width = attrs.get("width")
            self.stage_height = attrs.get("height")
        elif tag == "section" and parent == "deck-stage":
            self.slide_count += 1
            if attrs.get("data-label"):
                self.labels.append(attrs["data-label"])
        elif tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        elif tag == "style":
            self.in_style = True
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag in self.stack:
            idx = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[idx:]

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
        elif self.stack and self.stack[-1] not in ("script", "style"):
            self.texts.append(data)


def _is_cjk(ch: str) -> bool:
    value = ord(ch)
    return 0x3400 <= value <= 0x4DBF or 0x4E00 <= value <= 0x9FFF


def inspect(path: str) -> dict:
    source = Path(path).read_text(encoding="utf-8")
    parser = DeckParser()
    parser.feed(source)
    text = " ".join(part.strip() for part in parser.texts if part.strip())
    style = "\n".join(parser.styles)
    low = text.lower()
    font_sizes = [int(value) for value in re.findall(r"(?:font-size|--type-[\w-]+)\s*:\s*(\d+)px", style)]
    duplicate_labels = sorted({label for label in parser.labels if parser.labels.count(label) > 1})
    errors = []
    if parser.stage_count != 1:
        errors.append("expected exactly one deck-stage")
    if parser.stage_width != "1920" or parser.stage_height != "1080":
        errors.append("deck-stage must be 1920x1080")
    if parser.slide_count == 0:
        errors.append("no direct section slides")
    if len(parser.labels) != parser.slide_count:
        errors.append("every slide needs data-label")
    if duplicate_labels:
        errors.append("duplicate slide labels: " + ", ".join(duplicate_labels))
    if not any(src.endswith("deck-stage.js") for src in parser.scripts):
        errors.append("deck-stage.js script is missing")
    wrapper_fill = bool(re.search(r"section\[data-label\]\s*>\s*\*", style)) and "height: 100%" in style
    if not wrapper_fill:
        errors.append("slide wrapper fill rule is missing")
    explicit_slide_text_color = bool(
        re.search(r"\.slide\s*\{[^}]*\bcolor\s*:\s*var\(--ink\)", style, flags=re.DOTALL)
    )
    if not explicit_slide_text_color:
        errors.append("slide text color must be explicit to avoid deck-stage host-style inheritance")
    return {
        "file": path,
        "html_slide_count": parser.slide_count,
        "deck_stage_count": parser.stage_count,
        "stage_width": parser.stage_width,
        "stage_height": parser.stage_height,
        "section_label_count": len(parser.labels),
        "duplicate_labels": duplicate_labels,
        "deck_stage_script_count": sum(1 for src in parser.scripts if src.endswith("deck-stage.js")),
        "wrapper_fill_rule_count": 1 if wrapper_fill else 0,
        "explicit_slide_text_color_rule_count": 1 if explicit_slide_text_color else 0,
        "text_chars": len(text),
        "cjk_chars": sum(1 for ch in text if _is_cjk(ch)),
        "font_size_min_px": min(font_sizes) if font_sizes else None,
        "placeholders": sorted({value for value in PLACEHOLDER_PATTERNS if value in low}),
        "html_validation_errors": errors,
        "html_validation_error_count": len(errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a deck-stage HTML artifact")
    parser.add_argument("html")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    metrics = inspect(args.html)
    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    else:
        for key, value in metrics.items():
            print(key + ": " + str(value))
    return 1 if metrics["html_validation_error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
