#!/usr/bin/env python3
"""Run the eval harness and enforce a policy-driven coverage gate.

Cases live in evals/cases/<id>/ (brief.md + expect.json).
Artifacts are looked up in evals/artifacts/. Missing artifacts are classified as
SKIP or BLOCKED from the environment matrix; the coverage policy decides the
process exit code.
Use --pptx PATH --case ID to validate a single file directly.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C
from pptx_inspect import inspect
from validate_pptx import validate
from html_deck_inspect import inspect as inspect_html


DEFAULT_POLICY = {
    "min_pass": 1,
    "max_fail": 0,
    "max_skip": 0,
    "blocked_requires_reason": True,
    "required_run_metadata": ["model", "prompt_version", "parameters", "execution_path"],
}


def current_git_sha(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else None


def load_cases(evals_dir: Path):
    cases_dir = evals_dir / "cases"
    cases = []
    if cases_dir.is_dir():
        for d in sorted(p for p in cases_dir.iterdir() if p.is_dir()):
            expect_path = d / "expect.json"
            if expect_path.is_file():
                cases.append((d.name, json.loads(C.read_text(expect_path))))
    return cases


def load_json(path: Path, default: dict) -> dict:
    if not path.is_file():
        return dict(default)
    data = json.loads(C.read_text(path))
    if not isinstance(data, dict):
        raise ValueError(str(path) + " must contain a JSON object")
    return data


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
        elif key.endswith("_eq"):
            metric = key[:-3]
            actual = metrics.get(metric)
            ok = actual == limit
        elif key.endswith("_in"):
            metric = key[:-3]
            actual = metrics.get(metric)
            ok = isinstance(limit, list) and actual in limit
        else:
            checks.append((key, False, "unsupported assertion"))
            continue
        checks.append((key, bool(ok), str(actual)))
    return checks


def validate_case(case_id, expect, artifact_path: Path):
    if artifact_path.suffix.lower() == ".pptx":
        metrics = inspect(str(artifact_path))
        findings = validate(str(artifact_path))
        metrics["validation_error_count"] = sum(1 for f in findings if f.severity == "error")
        metrics["validation_warning_count"] = sum(1 for f in findings if f.severity == "warning")
    elif artifact_path.suffix.lower() in (".html", ".htm"):
        metrics = inspect_html(str(artifact_path))
    else:
        metrics = {"file": str(artifact_path), "artifact_validation_error_count": 1}
    metadata_path = artifact_path.with_suffix(".run.json")
    try:
        run_metadata = load_json(metadata_path, {})
    except (OSError, ValueError, json.JSONDecodeError):
        run_metadata = {}
    metrics["execution_path"] = run_metadata.get("execution_path")
    checks = evaluate(metrics, expect)
    passed = all(ok for _, ok, _ in checks)
    return {
        "case": case_id,
        "path": str(artifact_path),
        "eval_path": expect.get("path"),
        "status": "PASS" if passed else "FAIL",
        "passed": passed,
        "metrics": metrics,
        "checks": checks,
        "run_metadata": run_metadata,
    }


def coverage_gate(results: list[dict], skipped: list[dict], blocked: list[dict], policy: dict) -> dict:
    merged = dict(DEFAULT_POLICY)
    merged.update(policy)
    pass_count = sum(1 for r in results if r.get("status") == "PASS")
    fail_count = sum(1 for r in results if r.get("status") == "FAIL")
    missing_blocker_reasons = [b.get("case", "unknown") for b in blocked if not str(b.get("reason", "")).strip()]
    required_metadata = merged.get("required_run_metadata", [])
    missing_run_metadata = []
    for result in results:
        missing = [key for key in required_metadata if result.get("run_metadata", {}).get(key) in (None, "", {})]
        if missing:
            missing_run_metadata.append({"case": result.get("case"), "missing": missing})
    checks = [
        {
            "id": "min_pass",
            "ok": pass_count >= int(merged["min_pass"]),
            "actual": pass_count,
            "expected": ">= " + str(merged["min_pass"]),
        },
        {
            "id": "max_fail",
            "ok": fail_count <= int(merged["max_fail"]),
            "actual": fail_count,
            "expected": "<= " + str(merged["max_fail"]),
        },
        {
            "id": "max_skip",
            "ok": len(skipped) <= int(merged["max_skip"]),
            "actual": len(skipped),
            "expected": "<= " + str(merged["max_skip"]),
        },
    ]
    if merged.get("blocked_requires_reason", True):
        checks.append({
            "id": "blocked_requires_reason",
            "ok": not missing_blocker_reasons,
            "actual": missing_blocker_reasons,
            "expected": "all BLOCKED cases have a non-empty reason",
        })
    checks.append({
        "id": "required_run_metadata",
        "ok": not missing_run_metadata,
        "actual": missing_run_metadata,
        "expected": "every executed case records " + ", ".join(required_metadata),
    })
    return {
        "passed": all(c["ok"] for c in checks),
        "policy": merged,
        "counts": {
            "pass": pass_count,
            "fail": fail_count,
            "skip": len(skipped),
            "blocked": len(blocked),
        },
        "checks": checks,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate produced decks against structural expectations")
    parser.add_argument("--evals-dir", default=str(C.ROOT / "evals"))
    parser.add_argument("--artifacts-dir")
    parser.add_argument("--case")
    artifact_group = parser.add_mutually_exclusive_group()
    artifact_group.add_argument("--pptx", help="Backward-compatible alias for --artifact")
    artifact_group.add_argument("--artifact", help="Explicit PPTX or HTML artifact")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compare", action="store_true", help="Diff against the previous latest.json")
    parser.add_argument("--policy", help="Coverage policy JSON (default: evals/policy.json)")
    parser.add_argument("--environment", help="Environment matrix JSON (default: evals/environment.json)")
    args = parser.parse_args(argv)

    evals_dir = Path(args.evals_dir)
    artifacts_dir = Path(args.artifacts_dir) if args.artifacts_dir else evals_dir / "artifacts"
    cases = load_cases(evals_dir)
    if not cases:
        print("run_evals: no eval cases found under " + str(evals_dir / "cases"))
        return 1

    if args.case and args.case not in {cid for cid, _ in cases}:
        print("run_evals: unknown case " + args.case, file=sys.stderr)
        return 2

    try:
        policy_path = Path(args.policy) if args.policy else evals_dir / "policy.json"
        environment_path = Path(args.environment) if args.environment else evals_dir / "environment.json"
        policy = load_json(policy_path, DEFAULT_POLICY)
        environment = load_json(environment_path, {"paths": {}})
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("run_evals: invalid eval configuration: " + str(exc), file=sys.stderr)
        return 2

    results = []
    skipped = []
    blocked = []
    explicit_artifact = args.artifact or args.pptx
    if explicit_artifact:
        if not args.case:
            print("run_evals: --pptx requires --case", file=sys.stderr)
            return 2
        expect = next((e for cid, e in cases if cid == args.case), None)
        if expect is None:
            print("run_evals: unknown case " + args.case, file=sys.stderr)
            return 2
        results.append(validate_case(args.case, expect, Path(explicit_artifact)))
    else:
        for case_id, expect in cases:
            if args.case and case_id != args.case:
                continue
            extension = expect.get("artifact_extension", ".pptx")
            candidate = artifacts_dir / (case_id + extension)
            if not candidate.is_file() and artifacts_dir.is_dir():
                others = sorted(artifacts_dir.glob(case_id + "*" + extension))
                candidate = others[0] if others else candidate
            if not candidate.is_file():
                eval_path = expect.get("path")
                path_state = environment.get("paths", {}).get(eval_path, {})
                if path_state.get("status") == "BLOCKED":
                    blocked.append({
                        "case": case_id,
                        "path": eval_path,
                        "reason": path_state.get("reason", ""),
                    })
                else:
                    skipped.append({
                        "case": case_id,
                        "path": eval_path,
                        "reason": "runnable case has no artifact in " + str(artifacts_dir),
                    })
                continue
            results.append(validate_case(case_id, expect, candidate))

    gate = coverage_gate(results, skipped, blocked, policy)
    if not args.json:
        counts = gate["counts"]
        print("run_evals: " + str(counts["pass"]) + " pass, " + str(counts["fail"]) + " fail, " +
              str(counts["skip"]) + " skip, " + str(counts["blocked"]) + " blocked")
        for r in results:
            mark = r["status"]
            print("")
            print("[" + mark + "] " + r["case"] + "  (" + r["path"] + ")")
            for name, ok, actual in r["checks"]:
                print("  " + ("ok  " if ok else "FAIL") + " " + name + " = " + actual)
            m = r["metrics"]
            if r["path"].lower().endswith(".pptx"):
                print("  metrics: slides=" + str(m["slide_count"]) + " charts=" + str(m["chart_count"]) +
                      " tables=" + str(m["table_count"]) + " images=" + str(m["image_count"]) +
                      " text=" + str(m["text_chars"]) + " cjk=" + str(m["cjk_chars"]) +
                      " fonts=" + str(m["font_families"]))
            else:
                print("  metrics: slides=" + str(m.get("html_slide_count")) +
                      " text=" + str(m.get("text_chars")) + " cjk=" + str(m.get("cjk_chars")) +
                      " html_errors=" + str(m.get("html_validation_error_count")))
        for item in skipped:
            print("SKIP " + item["case"] + " (" + item["reason"] + ")")
        for item in blocked:
            print("BLOCKED " + item["case"] + " [Path " + str(item["path"]) + "]: " +
                  (item["reason"] or "missing reason"))

        print("")
        print("-- coverage gate --")
        for check in gate["checks"]:
            print("  " + ("ok  " if check["ok"] else "FAIL") + " " + check["id"] +
                  ": actual=" + str(check["actual"]) + " expected=" + str(check["expected"]))

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
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%S%fZ")
    payload = {
        "run_id": run_id,
        "generated_at": now.isoformat(),
        "environment": {
            "captured_at": environment.get("captured_at"),
            "baseline_git_sha": environment.get("git_sha"),
            "run_git_sha": current_git_sha(C.ROOT),
        },
        "results": results,
        "skipped": skipped,
        "blocked": blocked,
        "gate": gate,
    }
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    runs_dir = results_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = runs_dir / (run_id + ".json")
    ledger_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("")
        print("run_evals: written to " + str(latest))
        print("run_evals: ledger " + str(ledger_path))
    return 0 if gate["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
