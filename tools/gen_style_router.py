#!/usr/bin/env python3
"""Generate skills/<name>/styles/router.md from the machine-readable registry.

Why this exists
---------------
`styles/index.json` is the single source of truth for style data, but most of it
(`tier`, `proven`, `preset`, `sample`, `name_en`) only matters to the harness.
Reading the whole registry at selection time costs the agent far more context
than the router actually needs.

`styles/router.md` is a DERIVED, context-optimized digest of the registry: one
line per style, carrying only what style selection needs. The agent reads the
router; verifiers read `index.json`.

`make check` fails when the digest and the registry disagree, so `index.json`
stays the only file anyone edits by hand.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

CHECK = "check_style_router"
ROUTER_NAME = "router.md"
ONELINER_RE = re.compile(r"\*\*一句话：\*\*\s*(.+)")
FORMALITY_ZH = {"low": "低", "medium": "中", "high": "高"}

HEADER = """# Style Router

> **自动生成的派生产物，请勿手改。** 唯一事实源是 `index.json`；开发仓库会自动校验两者一致。
>
> 选风格只需要这一张表：先按主题推荐定位，再用 `formality` 与 `path` 过滤，
> 最后**只读选中的那 1 个** `styles/<id>.md` 取 Base Style Prompt 与版式组件。
"""


def one_liner(preset_path: Path) -> str:
    """Extract the preset's `**一句话：**` summary; empty when absent."""
    if not preset_path.is_file():
        return ""
    match = ONELINER_RE.search(C.read_text(preset_path))
    return match.group(1).strip().rstrip("。") if match else ""


def render(skill: Path) -> str:
    registry = skill / "styles" / "index.json"
    data = json.loads(C.read_text(registry))
    styles = data.get("styles") or []
    by_id = {s.get("id"): s for s in styles if s.get("id")}

    out = [HEADER]

    out.append("## 主题 → 推荐")
    out.append("")
    out.append("| 主题 | 首选 | 次选 | 第三 |")
    out.append("|---|---|---|---|")
    for rec in data.get("theme_recommendations") or []:
        slots = [rec.get(k) or "—" for k in ("first", "second", "third")]
        out.append("| " + " | ".join([str(rec.get("theme") or "—")] + slots) + " |")
    out.append("")

    unproven = []
    buckets: dict[str, list] = {}
    for style in styles:
        sid = style.get("id")
        if not sid:
            continue
        buckets.setdefault(str(style.get("path") or "—"), []).append(style)
        if not style.get("proven"):
            unproven.append(str(sid))

    out.append("## 风格")
    out.append("")
    out.append("样例图：`assets/style-samples/<id>.webp`；完整元数据：`index.json`。")
    out.append("")
    for path_key in sorted(buckets):
        out.append(f"### path: {path_key}")
        out.append("")
        out.append("| id | 名称 | 主题 | 正式度 | 一句话 |")
        out.append("|---|---|---|---|---|")
        for style in buckets[path_key]:
            sid = str(style["id"])
            row = [
                sid,
                str(style.get("name") or ""),
                "/".join(style.get("themes") or []) or "—",
                FORMALITY_ZH.get(str(style.get("formality") or ""), str(style.get("formality") or "—")),
                one_liner(skill / "styles" / (sid + ".md")) or "—",
            ]
            out.append("| " + " | ".join(row) + " |")
        out.append("")

    if unproven:
        out.append("无样例图 / 未验证：" + "、".join(unproven) + "。")
        out.append("")

    return "\n".join(out).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate or verify styles/router.md from styles/index.json")
    parser.add_argument("--skill", default="subaru-slides", help="skill directory name")
    parser.add_argument("--write", action="store_true", help="write router.md instead of verifying")
    C.add_common_args(parser)
    args = parser.parse_args()

    skill = C.ROOT / "skills" / args.skill
    if not (skill / "SKILL.md").is_file():
        print("gen_style_router: no skill at " + str(skill), file=sys.stderr)
        return 2
    registry = skill / "styles" / "index.json"
    if not registry.is_file():
        print("gen_style_router: no registry at " + str(registry), file=sys.stderr)
        return 2

    router = skill / "styles" / ROUTER_NAME
    try:
        expected = render(skill)
    except json.JSONDecodeError as exc:
        print("gen_style_router: invalid JSON in " + C.rel(registry) + ": " + str(exc), file=sys.stderr)
        return 2

    if args.write:
        if router.is_file() and C.read_text(router) == expected:
            print("gen_style_router: unchanged " + C.rel(router))
            return 0
        router.write_text(expected, encoding="utf-8")
        print("gen_style_router: wrote " + C.rel(router))
        return 0

    findings = []
    if not router.is_file():
        findings.append(C.Finding(
            CHECK, "missing-router:" + skill.name,
            "styles/" + ROUTER_NAME + " is missing; run 'make style-router'", C.rel(registry)))
    elif C.read_text(router) != expected:
        findings.append(C.Finding(
            CHECK, "stale-router:" + skill.name,
            "styles/" + ROUTER_NAME + " is stale; run 'make style-router' to regenerate it",
            C.rel(router)))

    print("gen_style_router: checked " + C.rel(router))
    return C.report(CHECK, findings, args)


if __name__ == "__main__":
    sys.exit(main())
