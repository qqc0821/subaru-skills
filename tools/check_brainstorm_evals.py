#!/usr/bin/env python3
"""Validate recorded conversations and semantic reviews; never generate model evidence.

Standard library only. Exit 0: complete passing skill coverage; 1: failed,
missing, or blocked evidence; 2: invalid configuration or invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARMS = ("baseline", "skill")


def digest_skill(skill: Path) -> str:
    """Fingerprint runtime instructions, independent of local absolute paths."""
    paths = [skill / "SKILL.md", *sorted((skill / "references").glob("*.md"))]
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(skill)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_cases(directory: Path) -> dict:
    cases = {}
    for path in sorted(directory.glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(case, dict) or case.get("id") != path.stem or not isinstance(case.get("turns"), list) or not case["turns"]:
            raise ValueError("invalid case identity or turns: " + path.name)
        if not all(isinstance(turn, str) and turn.strip() for turn in case["turns"]):
            raise ValueError("case turns must be non-empty strings: " + path.name)
        criteria = case.get("criteria")
        if not isinstance(criteria, dict) or not criteria or not all(
                isinstance(key, str) and isinstance(value, str) and value.strip()
                for key, value in criteria.items()):
            raise ValueError("invalid semantic criteria: " + path.name)
        cases[case["id"]] = case
    if not cases:
        raise ValueError("no conversation cases found")
    return cases


def validate_run(run: dict, case: dict, fingerprint: str) -> list[str]:
    errors = []
    if run.get("case") != case["id"] or run.get("arm") not in ARMS:
        errors.append("invalid case or arm")
    if type(run.get("repeat")) is not int or run["repeat"] < 1:
        errors.append("repeat must be a positive integer")
    if run.get("status") == "BLOCKED":
        if not isinstance(run.get("reason"), str) or not run["reason"].strip():
            errors.append("BLOCKED requires a reason")
        return errors
    if run.get("status") != "executed":
        errors.append("status must be executed or BLOCKED")
    for key in ("model", "prompt_version", "common_prompt", "execution_path", "recorded_at", "generator"):
        if not isinstance(run.get(key), str) or not run[key].strip():
            errors.append("missing metadata: " + key)
    if not isinstance(run.get("parameters"), dict) or not run["parameters"]:
        errors.append("parameters must record the actual generation controls")
    if not isinstance(run.get("host_capabilities"), list) or not all(
            isinstance(value, str) and value.strip() for value in run["host_capabilities"]):
        errors.append("host_capabilities must be a list of capability names")
    if run.get("arm") == "skill" and run.get("skill_digest") != fingerprint:
        errors.append("skill_digest does not match current runtime instructions")
    transcript = run.get("transcript")
    if not isinstance(transcript, list):
        transcript = []
        errors.append("transcript must contain the actual conversation")
    expected_roles = [role for _ in case["turns"] for role in ("user", "assistant")]
    valid_messages = all(isinstance(message, dict)
                         and isinstance(message.get("content"), str) and message["content"].strip()
                         for message in transcript)
    if not valid_messages or [m.get("role") for m in transcript if isinstance(m, dict)] != expected_roles:
        errors.append("transcript must alternate user/assistant for every case turn")
    if [m.get("content") for m in transcript if isinstance(m, dict) and m.get("role") == "user"] != case["turns"]:
        errors.append("user turns differ from the fixed case")
    review = run.get("review")
    if not isinstance(review, dict):
        review = {}
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        errors.append("reviewer must identify the semantic reviewer")
    if review.get("kind") not in ("human", "model", "self"):
        errors.append("review kind must be human, model, or self")
    judgments = review.get("criteria")
    if not isinstance(judgments, dict):
        judgments = {}
    if set(judgments) != set(case["criteria"]):
        errors.append("review must cover exactly the case criteria")
    for name in case["criteria"]:
        judgment = judgments.get(name)
        if not isinstance(judgment, dict):
            errors.append("missing judgment: " + name)
            continue
        if type(judgment.get("passed")) is not bool:
            errors.append("judgment must be boolean: " + name)
        if not isinstance(judgment.get("reason"), str) or not judgment["reason"].strip():
            errors.append("judgment needs semantic reasoning: " + name)
        evidence = judgment.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append("judgment needs quoted transcript evidence: " + name)
            continue
        for item in evidence:
            if not isinstance(item, dict):
                errors.append("invalid evidence: " + name)
                continue
            turn, quote = item.get("turn"), item.get("quote")
            if (type(turn) is not int or not 0 <= turn < len(transcript)
                    or not isinstance(transcript[turn], dict)
                    or transcript[turn].get("role") != "assistant"
                    or not isinstance(quote, str) or not quote.strip()
                    or not isinstance(transcript[turn].get("content"), str)
                    or quote not in transcript[turn]["content"]):
                errors.append("evidence must quote an actual assistant turn: " + name)
    return errors


def assess(cases: dict, runs: list[dict], fingerprint: str, repeats: int = 3) -> dict:
    indexed, errors, results = {}, [], []
    if not cases or repeats < 1:
        errors.append("non-empty cases and positive repeat coverage are required")
    for run in runs:
        if not isinstance(run, dict) or run.get("case") not in cases:
            errors.append("unknown case or malformed run")
            continue
        current = validate_run(run, cases[run["case"]], fingerprint)
        if current:
            errors.extend(str(run.get("case")) + ": " + error for error in current)
            continue
        if run["repeat"] > repeats:
            errors.append(run["case"] + ": repeat exceeds requested coverage; use a run directory for this experiment")
            continue
        key = (run["case"], run["arm"], run["repeat"])
        if key in indexed:
            errors.append("duplicate run: " + str(key))
        else:
            indexed[key] = run
    for name, case in cases.items():
        for repeat in range(1, repeats + 1):
            pair = {}
            for arm in ARMS:
                run = indexed.get((name, arm, repeat))
                if run is None:
                    result = {"case": name, "arm": arm, "repeat": repeat, "status": "SKIP",
                              "reason": "no valid recorded conversation and review"}
                elif run["status"] == "BLOCKED":
                    result = {"case": name, "arm": arm, "repeat": repeat, "status": "BLOCKED",
                              "reason": run["reason"]}
                else:
                    pair[arm] = run
                    failed = [key for key in case["criteria"] if not run["review"]["criteria"][key]["passed"]]
                    result = {"case": name, "arm": arm, "repeat": repeat,
                              "status": "FAIL" if failed else "PASS", "failed_criteria": failed,
                              "review_kind": run["review"]["kind"],
                              "reviewer": run["review"]["reviewer"]}
                results.append(result)
            if len(pair) == 2:
                for field in ("model", "parameters", "common_prompt", "host_capabilities", "execution_path"):
                    if pair["baseline"][field] != pair["skill"][field]:
                        errors.append(name + ": comparison controls differ: " + field + " (repeat " + str(repeat) + ")")
    # Baseline behavior may fail criteria; incomplete baseline evidence may not.
    passed = not errors and all(
        r["status"] == "PASS" if r["arm"] == "skill" else r["status"] in ("PASS", "FAIL")
        for r in results)
    counts = {arm: {status: sum(r["arm"] == arm and r["status"] == status for r in results)
                    for status in ("PASS", "FAIL", "SKIP", "BLOCKED")} for arm in ARMS}
    self_reviewed = any(r.get("review_kind") == "self" for r in results)
    return {"passed": passed, "skill_digest": fingerprint, "repeats": repeats,
            "counts": counts, "errors": errors, "results": results,
            "claim_boundary": "Evidence completeness and recorded judgments only; quotes do not prove review accuracy. "
            + ("Includes self-review; independent validation remains pending." if self_reviewed
               else "No statistical superiority or creativity claim is established by this gate.")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases-dir", type=Path, default=ROOT / "evals/brainstorm/cases")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "evals/results/brainstorm/runs")
    parser.add_argument("--report", type=Path, default=ROOT / "evals/results/brainstorm/latest.json")
    parser.add_argument("--skill", type=Path, default=ROOT / "skills/subaru-brainstorm")
    parser.add_argument("--repeats", type=int, default=3, help="paired repeats per case; default 3")
    parser.add_argument("--fingerprint", action="store_true", help="print current runtime digest without running evals")
    args = parser.parse_args()
    try:
        if args.repeats < 1:
            raise ValueError("--repeats must be positive")
        fingerprint = digest_skill(args.skill)
        if args.fingerprint:
            print(fingerprint)
            return 0
        cases = load_cases(args.cases_dir)
        runs = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.runs_dir.glob("*.json"))]
        report = assess(cases, runs, fingerprint, args.repeats)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("check_brainstorm_evals: " + str(exc), file=sys.stderr)
        return 2
    print("brainstorm evidence: " + json.dumps(report["counts"], ensure_ascii=False))
    for error in report["errors"]:
        print("  ERROR: " + error)
    print(report["claim_boundary"])
    print("eval-brainstorm: " + ("PASS" if report["passed"] else "FAIL (incomplete or failing evidence)"))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
