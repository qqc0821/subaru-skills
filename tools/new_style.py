#!/usr/bin/env python3
"""Scaffold a style preset and optionally register it in styles/index.json."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TEMPLATE = """---
id: {id}
name: {name}
name_en: {name_en}
tier: {tier}
themes: [{themes}]
formality: {formality}
path: {path}
sample: null
proven: false
palette:
  background: "#FFFFFF"
  text: "#1A1A1A"
  accent: ["#D4480B"]
typography:
  heading: "bold"
  body: "regular"
  ratio: "3:1"
  cjk_font: "PingFang SC"
---

# {name} ({name_en})

**一句话：** TODO

## Base Style Prompt

```
TODO: describe mood and world-view in <=5 lines. Do not micro-manage composition, hex ratios, or character poses.
```

## 版式组件
- cover
- section divider

## 注意事项
- TODO

## 样例

（待补）
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a style preset")
    parser.add_argument("id")
    parser.add_argument("--name", required=True)
    parser.add_argument("--name-en", default="")
    parser.add_argument("--tier", type=int, default=3)
    parser.add_argument("--themes", default="")
    parser.add_argument("--formality", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--path", default="B_or_B2")
    parser.add_argument("--skill", default="subaru-slides")
    parser.add_argument("--register", action="store_true", help="also append the entry to styles/index.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not ID_RE.match(args.id):
        print("new_style: id must be lowercase hyphenated", file=sys.stderr)
        return 2
    skill = C.ROOT / "skills" / args.skill
    styles = skill / "styles"
    if not styles.is_dir():
        print("new_style: no styles/ dir in " + str(skill), file=sys.stderr)
        return 2
    preset = styles / (args.id + ".md")
    if preset.exists():
        print("new_style: preset already exists: " + str(preset), file=sys.stderr)
        return 2
    content = TEMPLATE.format(id=args.id, name=args.name, name_en=args.name_en or args.name,
                              tier=args.tier, themes=args.themes, formality=args.formality, path=args.path)
    if args.dry_run:
        print("would create " + str(preset))
        if args.register:
            print("would register " + args.id + " in " + str(styles / "index.json"))
        return 0
    preset.write_text(content, encoding="utf-8")
    print("created " + str(preset))
    if args.register:
        index_path = styles / "index.json"
        data = json.loads(C.read_text(index_path))
        if any(s.get("id") == args.id for s in data["styles"]):
            print("new_style: id already in index", file=sys.stderr)
            return 1
        data["styles"].append({
            "id": args.id, "name": args.name, "name_en": args.name_en or args.name,
            "tier": args.tier, "themes": [t for t in args.themes.split(",") if t],
            "formality": args.formality, "path": args.path, "sample": None,
            "preset": "styles/" + args.id + ".md", "proven": False,
        })
        data["count"] = len(data["styles"])
        index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("registered " + args.id + " (count=" + str(data["count"]) + ")")
    else:
        print("next: add an entry to styles/index.json (or rerun with --register)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
