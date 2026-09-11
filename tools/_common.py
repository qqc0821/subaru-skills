"""Shared helpers for the subaru-skills harness.

Standard library only. Python 3.10+.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

MAX_SKILL_MD_LINES = 200
MAX_REFERENCE_LINES = 600
MAX_SKILL_BYTES = 5 * 1024 * 1024
MAX_ASSET_BYTES = 1024 * 1024


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    if here.is_file():
        here = here.parent
    for cand in [here, *here.parents]:
        if (cand / "AGENTS.md").is_file():
            return cand
    return here


ROOT = find_repo_root()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def iter_skill_dirs():
    skills = ROOT / "skills"
    if not skills.is_dir():
        return []
    return sorted(d for d in skills.iterdir() if (d / "SKILL.md").is_file())


def iter_markdown_files(include_root: bool = True):
    files = []
    if include_root:
        files.extend(sorted(ROOT.glob("*.md")))
    skills = ROOT / "skills"
    if skills.is_dir():
        files.extend(sorted(skills.rglob("*.md")))
    docs = ROOT / "docs"
    if docs.is_dir():
        files.extend(sorted(docs.rglob("*.md")))
    seen = set()
    out = []
    for f in files:
        rp = f.resolve()
        if rp not in seen and rp.is_file():
            seen.add(rp)
            out.append(f)
    return out


def parse_frontmatter(text: str):
    """Return (dict, closing_index). Scalar values plus | and > block scalars."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, 0
    data = {}
    i = 1
    current_key = None
    block_lines = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            break
        if re.match(r"^[A-Za-z0-9_-]+:", line):
            if current_key is not None:
                data[current_key] = _coerce("\n".join(block_lines).strip())
                block_lines = []
            key, _, value = line.partition(":")
            current_key = key.strip()
            value = value.strip()
            if value in (">", ">-", "|", "|-", ">+", "|+"):
                data[current_key] = ""
            else:
                data[current_key] = _coerce(value)
                current_key = None
        elif current_key is not None:
            block_lines.append(line.strip())
        i += 1
    if current_key is not None:
        data[current_key] = _coerce("\n".join(block_lines).strip())
    return data, i


def _coerce(value: str):
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def parse_simple_yaml(text: str):
    """Parse the nested-2-level YAML used by agents/openai.yaml (no lists)."""
    data = {}
    stack = [(0, data)]
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, sep, value = line.strip().partition(":")
        if not sep:
            continue
        value = value.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            node = {}
            parent[key.strip()] = node
            stack.append((indent, node))
        else:
            parent[key.strip()] = _coerce(value)
    return data


@dataclass
class Finding:
    check: str
    key: str
    message: str
    path: str = ""
    line: int = 0
    severity: str = "error"

    def full_key(self) -> str:
        return self.check + ":" + self.key

    def render(self) -> str:
        loc = self.path
        if self.line:
            loc = loc + ":" + str(self.line)
        prefix = "ERROR" if self.severity == "error" else "WARN "
        return "  [" + prefix + "] " + loc + "  " + self.message


def load_baseline(path: Path):
    if not path.is_file():
        return set()
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return set()
    return set(data.get("known", []))


def save_baseline(path: Path, keys):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "note": "Known findings recorded by the harness. New findings fail make check.",
        "known": sorted(keys),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_common_args(parser):
    parser.add_argument("--baseline", default=str(ROOT / "tools" / "baseline.json"))
    parser.add_argument("--update-baseline", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")


def report(check_name: str, findings, args) -> int:
    baseline_path = Path(args.baseline)
    prefix = check_name + ":"
    current_keys = {f.full_key() for f in findings}
    if args.update_baseline:
        known = load_baseline(baseline_path)
        kept = {k for k in known if not k.startswith(prefix)}
        removed = {k for k in known if k.startswith(prefix)} - current_keys
        added = current_keys - known
        save_baseline(baseline_path, kept | current_keys)
        print(check_name + ": baseline updated (+" + str(len(added)) + " new, -" + str(len(removed)) + " stale, " + str(len(kept | current_keys)) + " total)")
        return 0
    known = load_baseline(baseline_path)
    suppressed = [f for f in findings if f.full_key() in known]
    fresh = [f for f in findings if f.full_key() not in known]
    stale = sorted(k for k in known if k.startswith(prefix) and k not in current_keys)
    errors = [f for f in fresh if f.severity == "error"]
    warnings = [f for f in fresh if f.severity == "warning"]
    if args.json:
        print(json.dumps({
            "check": check_name,
            "suppressed": len(suppressed),
            "stale": stale,
            "errors": [f.render().strip() for f in errors],
            "warnings": [f.render().strip() for f in warnings],
        }, ensure_ascii=False))
    else:
        for f in fresh:
            print(f.render())
        if suppressed:
            print("  (" + str(len(suppressed)) + " known finding(s) suppressed by baseline)")
        if stale:
            print("  (" + str(len(stale)) + " stale baseline entry(ies) no longer apply; run make baseline to clean)")
        if not fresh:
            print("  OK - no new findings")
    if errors or (args.strict and warnings):
        return 1
    return 0
