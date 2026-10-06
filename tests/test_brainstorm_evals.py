"""Synthetic evidence fixtures test the gate, never the quality of model output."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import check_brainstorm_evals as E
import check_context_budget as B
import check_installability as I
import validate_skills as V


class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": "fixture", "turns": ["synthetic request"],
                     "criteria": {"scope": "Synthetic behavior criterion."}}
        self.run = {
            "case": "fixture", "arm": "skill", "repeat": 1, "status": "executed",
            "model": "synthetic-test-model", "prompt_version": "fixture-v1", "common_prompt": "fixture",
            "generator": "unit-test-fixture", "parameters": {"max_output_tokens": 100},
            "host_capabilities": [], "execution_path": "fixture", "recorded_at": "fixture-time",
            "skill_digest": "digest",
            "transcript": [{"role": "user", "content": "synthetic request"},
                           {"role": "assistant", "content": "synthetic reply"}],
            "review": {"reviewer": "unit-test", "kind": "self", "criteria": {
                "scope": {"passed": True, "reason": "Synthetic review tests validation only.",
                          "evidence": [{"turn": 1, "quote": "synthetic reply"}]}}}}

    def pair(self):
        baseline = copy.deepcopy(self.run)
        baseline["arm"] = "baseline"
        return [baseline, copy.deepcopy(self.run)]

    def assess(self, runs):
        return E.assess({"fixture": self.case}, runs, "digest", repeats=1)

    def test_empty_evidence_cannot_pass(self):
        result = self.assess([])
        self.assertFalse(result["passed"])
        self.assertEqual(result["counts"]["skill"]["SKIP"], 1)

    def test_complete_pair_passes_with_self_review_boundary(self):
        result = self.assess(self.pair())
        self.assertTrue(result["passed"])
        self.assertIn("self-review", result["claim_boundary"])

    def test_baseline_behavior_failure_is_valid_comparison(self):
        runs = self.pair()
        runs[0]["review"]["criteria"]["scope"]["passed"] = False
        self.assertTrue(self.assess(runs)["passed"])

    def test_skill_failure_blocks(self):
        runs = self.pair()
        runs[1]["review"]["criteria"]["scope"]["passed"] = False
        self.assertFalse(self.assess(runs)["passed"])

    def test_missing_baseline_blocks(self):
        self.assertFalse(self.assess([self.run])["passed"])

    def test_duplicate_evidence_blocks(self):
        result = self.assess(self.pair() + [self.run])
        self.assertFalse(result["passed"])
        self.assertTrue(any("duplicate" in error for error in result["errors"]))

    def test_stale_skill_blocks(self):
        self.run["skill_digest"] = "old"
        self.assertIn("skill_digest does not match current runtime instructions",
                      E.validate_run(self.run, self.case, "digest"))

    def test_changed_user_turn_blocks(self):
        self.run["transcript"][0]["content"] = "easier request"
        self.assertIn("user turns differ from the fixed case", E.validate_run(self.run, self.case, "digest"))

    def test_fabricated_quote_blocks(self):
        self.run["review"]["criteria"]["scope"]["evidence"][0]["quote"] = "invented evidence"
        self.assertTrue(any("actual assistant" in error for error in E.validate_run(self.run, self.case, "digest")))

    def test_quote_from_user_is_not_assistant_evidence(self):
        self.run["review"]["criteria"]["scope"]["evidence"] = [{"turn": 0, "quote": "synthetic request"}]
        self.assertTrue(E.validate_run(self.run, self.case, "digest"))

    def test_missing_review_and_truthy_non_bool_block(self):
        for mutation in (None, {"reviewer": "unit-test", "kind": "self", "criteria": {}}):
            run = copy.deepcopy(self.run)
            run["review"] = mutation
            self.assertTrue(E.validate_run(run, self.case, "digest"))
        self.run["review"]["criteria"]["scope"]["passed"] = "true"
        self.assertTrue(E.validate_run(self.run, self.case, "digest"))

    def test_mismatched_controls_block(self):
        for field, value in (("model", "other"), ("parameters", {"max_output_tokens": 200}),
                             ("common_prompt", "other"), ("host_capabilities", ["files"]),
                             ("execution_path", "other")):
            with self.subTest(field=field):
                runs = self.pair()
                runs[1][field] = value
                self.assertFalse(self.assess(runs)["passed"])

    def test_blocked_has_reason_and_never_passes(self):
        blocked = {"case": "fixture", "arm": "skill", "repeat": 1, "status": "BLOCKED"}
        self.assertTrue(E.validate_run(blocked, self.case, "digest"))
        blocked["reason"] = "no configured conversation executor"
        result = self.assess([blocked])
        self.assertFalse(result["passed"])
        self.assertEqual(result["counts"]["skill"]["BLOCKED"], 1)

    def test_all_default_repeats_are_required(self):
        result = E.assess({"fixture": self.case}, self.pair(), "digest")
        self.assertFalse(result["passed"])
        self.assertEqual(result["counts"]["skill"]["SKIP"], 2)

    def test_empty_case_set_and_extra_runs_cannot_form_pass(self):
        self.assertFalse(E.assess({}, [], "digest")["passed"])
        extra = copy.deepcopy(self.run)
        extra["repeat"] = 2
        extra["review"]["criteria"]["scope"]["passed"] = False
        self.assertFalse(self.assess(self.pair() + [extra])["passed"])

    def test_malformed_case_configuration_has_clear_error(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            for data in ([], {"id": "fixture", "turns": []},
                         {"id": "fixture", "turns": ["request"], "criteria": {}}):
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    E.load_cases(Path(tmp))

    def test_multiple_turns_cannot_be_omitted(self):
        self.case["turns"].append("second user turn")
        self.assertTrue(E.validate_run(self.run, self.case, "digest"))

    def test_malformed_transcript_reports_errors(self):
        for transcript in ([None], [{"role": "assistant", "content": 3}], []):
            run = copy.deepcopy(self.run)
            run["transcript"] = transcript
            self.assertTrue(E.validate_run(run, self.case, "digest"))

    def test_fingerprint_changes_on_runtime_edit(self):
        with TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / "references").mkdir()
            (skill / "SKILL.md").write_text("entry")
            before = E.digest_skill(skill)
            (skill / "references/session.md").write_text("new runtime reference")
            self.assertNotEqual(before, E.digest_skill(skill))

    def test_cli_malformed_json_and_missing_records(self):
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            command = [sys.executable, str(ROOT / "tools/check_brainstorm_evals.py"),
                       "--runs-dir", str(directory), "--report", str(directory / "report.json")]
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 1)
            report = json.loads((directory / "report.json").read_text())
            case_count = len(E.load_cases(ROOT / "evals/brainstorm/cases"))
            self.assertEqual(report["counts"]["skill"]["SKIP"], case_count * 3)
            self.assertEqual(report["counts"]["baseline"]["SKIP"], case_count * 3)
            (directory / "report.json").unlink()
            (directory / "broken.json").write_text("{")
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 2)
            self.assertNotIn("Traceback", process.stderr)


class BrainstormPackageTests(unittest.TestCase):
    def test_package_and_isolated_copy_are_installable(self):
        import shutil
        skill = ROOT / "skills/subaru-brainstorm"
        self.assertEqual(V.check_skill(skill), [])
        with TemporaryDirectory() as tmp:
            isolated = Path(tmp) / skill.name
            shutil.copytree(skill, isolated)
            self.assertEqual(I.check_skill(isolated), [])
            import check_links
            for path in isolated.rglob("*.md"):
                self.assertEqual(check_links.scan_file(path), [])

    def test_routes_have_finite_budgets(self):
        skill = ROOT / "skills/subaru-brainstorm"
        findings, _, _ = B.check_skill(skill, verbose=False)
        self.assertEqual(findings, [])
        self.assertEqual(set(B.PROFILES[skill.name]["paths"]), set(B.PROFILES[skill.name]["budgets"]))

    def test_missing_reference_and_oversized_route_block(self):
        profile = {"paths": {"test": ["SKILL.md", "references/session.md"]},
                   "budgets": {"test": 5}, "entry_limit": 5, "file_limit": 5, "conditional": []}
        with TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / "SKILL.md").write_text("large " * 50)
            findings, _, _ = B.check_profile(skill, profile, verbose=False)
            keys = [finding.key for finding in findings]
            self.assertTrue(any("missing-required" in key for key in keys))
            self.assertTrue(any("route-over-budget" in key for key in keys))
            self.assertTrue(any("required-file-too-large" in key for key in keys))

    def test_reference_must_be_linked_and_marked_conditional(self):
        profile = {"paths": {"test": ["SKILL.md"]}, "budgets": {"test": 100},
                   "entry_limit": 100, "file_limit": 100, "conditional": ["references/session.md"]}
        with TemporaryDirectory() as tmp:
            skill = Path(tmp)
            for entry in ("session.md 按需", "[session](references/session.md)"):
                (skill / "SKILL.md").write_text(entry)
                findings, _, _ = B.check_profile(skill, profile, verbose=False)
                self.assertTrue(findings)

    def test_worst_slides_preset_is_enforced_in_gate(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            skill = Path(tmp)
            for rel in B.REQUIRED_PATH:
                path = skill / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("small")
            (skill / "styles/large.md").write_text("words " * 100)
            _, total, _ = B.check_slides_skill(skill, verbose=False)
            with patch.object(B, "REQUIRED_BUDGET", total + 10):
                findings, _, _ = B.check_slides_skill(skill, verbose=False)
                self.assertTrue(any(f.key == "worst-preset-over-budget" for f in findings))


if __name__ == "__main__":
    unittest.main()
