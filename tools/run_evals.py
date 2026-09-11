#!/usr/bin/env python3
"""Run the eval harness: validate produced decks against per-case structural expectations.

Cases live in evals/cases/<id>/ (brief.md + expect.json).
Artifacts are looked up in evals/artifacts/. Missing artifacts are SKIPPED, not failed.
Use --pptx PATH --case ID to validate a single file directly.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C
from pptx_inspect import inspect


def load_cases(evals_dir: Path):
    cases_dir = evals_dir / "cases"
    cases = []
    if cases_dir.is_dir():
        for d in sorted(p for p in cases_dir.iterdir() if p.is_dir()):
            expect_path = d / "expect.json"
            if expect_path.is_file():
                cases.append((d.name, json.loads(C.read_text(expect_path))))
    return cases


def evaluate(metrics: dict, expect: dict):
    checks = []
    for key, limit in expect.get("assert", {}).items():
        if key.endswith("_min"):
            metric = key[:-4]
            actual = metrics.get(metric)
            ok = isinstance(actual, (int, float)) and actual >= limit
        elif key.endswith("_max"):
            metric = key[:-4]
            actual = metrics.get(metric)
            if isinstance(actual, list):
                actual = len(actual)
            ok = isinstance(actual, (int, float)) and actual <= limit
        else:
            continue
        checks.append((key, bool(ok), str(actual)))
    return checks


def validate_case(case_id, expect, pptx_path: Path):
    metrics = inspect(str(pptx_path))
    checks = evaluate(metrics, expect)
    passed = all(ok for _, ok, _ in checks)
    return {"case": case_id, "path": str(pptx_path), "passed": passed, "metrics": metrics, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate produced decks against structural expectations")
    parser.add_argument("--evals-dir", default=str(C.ROOT / "evals"))
    parser.add_argument("--artifacts-dir")
    parser.add_argument("--case")
    parser.add_argument("--pptx")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compare", action="store_true", help="Diff against the previous latest.json")
    args = parser.parse_args()

    evals_dir = Path(args.evals_dir)
    artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else evals_dir / "artifacts"
    cases = load_cases(evals_dir)
    if not cases:
        print("run_evals: no eval cases found under " + str(evals_dir / "cases"))
        return 0

    results = []
    skipped = []
    if args.pptx:
        if not args.case:
            print("run_evals: --pptx requires --case", file=sys.stderr)
            return 2
        expect = next((e for cid, e in cases if cid == args.case), None)
        if expect is None:
            print("run_evals: unknown case " + args.case, file=sys.stderr)
            return 2
        results.append(validate_case(args.case, expect, Path(args.pptx)))
    else:
        for case_id, expect in cases:
            if args.case and case_id != args.case:
                continue
            candidate = artifacts_dir / (case_id + ".pptx")
            if not candidate.is_file() and artifacts_dir.is_dir():
                others = sorted(artifacts_dir.glob(case_id + "*.pptx"))
                candidate = others[0] if others else candidate
            if not candidate.is_file():
                skipped.append(case_id)
                continue
            results.append(validate_case(case_id, expect, candidate))

    failures = [r for r in results if not r["passed"]]
    if args.json:
        print(json.dumps({"results": results, "skipped": skipped}, ensure_ascii=False, indent=2))
    else:
        print("run_evals: " + str(len(results)) + " validated, " + str(len(skipped)) + " skipped")
        for r in results:
            mark = "PASS" if r["passed"] else "FAIL"
            print("")
            print("[" + mark + "] " + r["case"] + "  (" + r["path"] + ")")
            for name, ok, actual in r["checks"]:
                print("  " + ("ok  " if ok else "FAIL") + " " + name + " = " + actual)
            m = r["metrics"]
            print("  metrics: slides=" + str(m["slide_count"]) + " charts=" + str(m["chart_count"]) +
                  " tables=" + str(m["table_count"]) + " images=" + str(m["image_count"]) +
                  " text=" + str(m["text_chars"]) + " cjk=" + str(m["cjk_chars"]) +
                  " fonts=" + str(m["font_families"]))
        for cid in skipped:
            print("SKIP " + cid + " (no artifact in " + str(artifacts_dir) + ")")

    results_dir = evals_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    latest = results_dir / "latest.json"
    previous = None
    if latest.is_file():
        try:
            previous = json.loads(C.read_text(latest))
        except json.JSONDecodeError:
            previous = None
    if args.compare and previous is not None:
        prev_by_case = {r["case"]: r for r in previous.get("results", [])}
        print("")
        print("-- compare vs previous run --")
        for r in results:
            old = prev_by_case.get(r["case"])
            if not old:
                print("  " + r["case"] + ": new")
                continue
            if old.get("passed") != r["passed"]:
                print("  " + r["case"] + ": " + ("PASS -> FAIL" if old.get("passed") else "FAIL -> PASS"))
            for name, ok, actual in r["checks"]:
                old_check = next((c for c in old.get("checks", []) if c[0] == name), None)
                if old_check and old_check[2] != actual:
                    print("  " + r["case"] + "." + name + ": " + old_check[2] + " -> " + actual)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "results": results, "skipped": skipped}
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("")
    print("run_evals: written to " + str(latest))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
