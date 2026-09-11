#!/usr/bin/env python3
"""Build deterministic eval artifacts for a clean checkout.

This helper intentionally prepares only the repository-owned fixed-input PPTX
cases. Optional host capabilities such as image generation, deck-stage,
html2pptx, and office rendering remain outside the CI claim boundary.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CREATE_SLIDES = ROOT / "skills" / "subaru-slides" / "scripts" / "create_slides.py"
SAMPLES = ROOT / "skills" / "subaru-slides" / "assets" / "style-samples"
DEFAULT_ARTIFACTS = ROOT / "evals" / "artifacts"

CASES = {
    "fallback-image-pptx": {
        "path": "fallback",
        "images": [
            "slide04-01-苏联构成主义-constructivism.webp",
            "slide04-03-包豪斯-bauhaus.webp",
            "slide04-06-工程蓝图-blueprint.webp",
        ],
        "model": "deterministic-image-assembler",
        "prompt_version": "fallback-image-pptx/v1",
    },
    "full-ai-visual": {
        "path": "B",
        "images": [
            "slide04-01-苏联构成主义-constructivism.webp",
            "slide04-02-浮世绘-ukiyo-e.webp",
            "slide04-03-包豪斯-bauhaus.webp",
            "slide04-06-工程蓝图-blueprint.webp",
            "slide04-10-敦煌壁画-dunhuang.webp",
        ],
        "model": "fixed-ai-visual-fixture",
        "prompt_version": "full-ai-visual/v1",
    },
}


def doctor() -> list[str]:
    problems = []
    if not shutil.which("uv"):
        problems.append("uv is not available")
    if not CREATE_SLIDES.is_file():
        problems.append("missing " + str(CREATE_SLIDES.relative_to(ROOT)))
    for spec in CASES.values():
        for name in spec["images"]:
            path = SAMPLES / name
            if not path.is_file():
                problems.append("missing " + str(path.relative_to(ROOT)))
    return problems


def build_case(case_id: str, spec: dict, artifacts_dir: Path) -> None:
    output = artifacts_dir / (case_id + ".pptx")
    command = [
        "uv",
        "run",
        "--quiet",
        str(CREATE_SLIDES),
        *[str(SAMPLES / name) for name in spec["images"]],
        "--layout",
        "fullscreen",
        "--output",
        str(output),
    ]
    env = os.environ.copy()
    env.setdefault("UV_CACHE_DIR", str(ROOT / ".uv-cache"))
    completed = subprocess.run(command, cwd=ROOT, env=env, text=True)
    if completed.returncode:
        raise RuntimeError("artifact build failed for " + case_id)
    metadata = {
        "model": spec["model"],
        "prompt_version": spec["prompt_version"],
        "parameters": {
            "layout": "fullscreen",
            "fixed_input_count": len(spec["images"]),
        },
        "execution_path": spec["path"],
    }
    output.with_suffix(".run.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build deterministic fixed-input eval artifacts")
    parser.add_argument("--doctor", action="store_true", help="check prerequisites without building")
    parser.add_argument("--artifacts-dir", default=str(DEFAULT_ARTIFACTS), help="output directory")
    args = parser.parse_args(argv)
    problems = doctor()
    if problems:
        for problem in problems:
            print("prepare_eval_artifacts: " + problem, file=sys.stderr)
        return 1
    if args.doctor:
        print("prepare_eval_artifacts: OK")
        return 0
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    try:
        for case_id, spec in CASES.items():
            build_case(case_id, spec, artifacts_dir)
    except RuntimeError as exc:
        print("prepare_eval_artifacts: " + str(exc), file=sys.stderr)
        return 1
    print("prepare_eval_artifacts: built " + str(len(CASES)) + " fixed-input artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
