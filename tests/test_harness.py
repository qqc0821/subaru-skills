"""Regression tests for the subaru-skills harness.

Standard library only. Run with:  python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import _common as C  # noqa: E402
import pptx_inspect  # noqa: E402
import run_evals  # noqa: E402
import validate_pptx  # noqa: E402
import html_deck_inspect  # noqa: E402

DETECT_SPEC = importlib.util.spec_from_file_location(
    "detect_capabilities", ROOT / "skills" / "subaru-slides" / "scripts" / "detect_capabilities.py"
)
detect_capabilities = importlib.util.module_from_spec(DETECT_SPEC)
DETECT_SPEC.loader.exec_module(detect_capabilities)

SKILL = C.ROOT / "skills" / "subaru-slides"
DECK = C.ROOT / "output" / "subaru-ev-trends.pptx"


class TestCommon(unittest.TestCase):
    def test_frontmatter(self):
        fm, _ = C.parse_frontmatter(C.read_text(SKILL / "SKILL.md"))
        self.assertEqual(fm.get("name"), "subaru-slides")
        self.assertTrue(fm.get("description"))

    def test_frontmatter_contains_core_slide_triggers(self):
        fm, _ = C.parse_frontmatter(C.read_text(SKILL / "SKILL.md"))
        description = fm["description"].lower()
        for trigger in ("ppt", "幻灯片", "演示文稿", "keynote", "slides"):
            self.assertIn(trigger.lower(), description)

    def test_openai_yaml(self):
        data = C.parse_simple_yaml(C.read_text(SKILL / "agents" / "openai.yaml"))
        self.assertTrue(data["interface"]["display_name"])
        self.assertIn("allow_implicit_invocation", data["policy"])

    def test_skill_md_line_budget(self):
        lines = C.read_text(SKILL / "SKILL.md").count("\n") + 1
        self.assertLessEqual(lines, C.MAX_SKILL_MD_LINES)


class TestStyleSystem(unittest.TestCase):
    def test_index_matches_count_and_samples(self):
        data = json.loads(C.read_text(SKILL / "styles" / "index.json"))
        self.assertEqual(data["count"], len(data["styles"]))
        ids = [s["id"] for s in data["styles"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in data["styles"]:
            if s.get("sample"):
                self.assertTrue((SKILL / s["sample"]).exists(), s["id"] + " sample missing")

    def test_theme_recommendations_resolve(self):
        data = json.loads(C.read_text(SKILL / "styles" / "index.json"))
        ids = {s["id"] for s in data["styles"]}
        for rec in data["theme_recommendations"]:
            for slot in ("first", "second", "third"):
                if rec.get(slot):
                    self.assertIn(rec[slot], ids, "unknown style in " + str(rec.get("theme")))


class TestDeckTools(unittest.TestCase):
    @unittest.skipUnless(DECK.is_file(), "reference deck not present")
    def test_inspect(self):
        m = pptx_inspect.inspect(str(DECK))
        self.assertGreaterEqual(m["slide_count"], 6)
        self.assertGreaterEqual(m["chart_count"], 1)
        self.assertGreater(m["cjk_chars"], 0)

    @unittest.skipUnless(DECK.is_file(), "reference deck not present")
    def test_validate_has_no_errors(self):
        findings = validate_pptx.validate(str(DECK))
        errors = [f.message for f in findings if f.severity == "error"]
        self.assertEqual(errors, [], "unexpected structural errors: " + str(errors))

    def test_html_deck_inspector_rejects_missing_stage(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.html"
            path.write_text("<!doctype html><html><body><section>Bad</section></body></html>", encoding="utf-8")
            metrics = html_deck_inspect.inspect(str(path))
            self.assertGreater(metrics["html_validation_error_count"], 0)

    def test_html_deck_fixture_has_explicit_text_color(self):
        fixture = ROOT / "evals" / "cases" / "html-deck" / "fixture.html"
        metrics = html_deck_inspect.inspect(str(fixture))
        self.assertEqual(metrics["html_validation_errors"], [])
        self.assertEqual(metrics["explicit_slide_text_color_rule_count"], 1)


class TestEvalEngine(unittest.TestCase):
    def test_missing_case_directory_is_not_green(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(run_evals.main(["--evals-dir", tmp]), 1)

    def test_evaluate(self):
        checks = run_evals.evaluate({"slide_count": 5, "chart_count": 0},
                                    {"assert": {"slide_count_min": 3, "chart_count_min": 1}})
        result = {c[0]: c[1] for c in checks}
        self.assertTrue(result["slide_count_min"])
        self.assertFalse(result["chart_count_min"])

    def test_coverage_gate_rejects_zero_pass(self):
        skipped = [{"case": "runnable", "path": "C", "reason": "artifact missing"}]
        gate = run_evals.coverage_gate([], skipped, [], {"min_pass": 1, "max_skip": 0})
        self.assertFalse(gate["passed"])
        self.assertEqual(gate["counts"]["pass"], 0)

    def test_blocked_requires_reason(self):
        blocked = [{"case": "native", "path": "A", "reason": ""}]
        gate = run_evals.coverage_gate([], [], blocked, {"min_pass": 0})
        self.assertFalse(gate["passed"])
        check = next(c for c in gate["checks"] if c["id"] == "blocked_requires_reason")
        self.assertEqual(check["actual"], ["native"])

    def test_exact_and_membership_assertions(self):
        checks = run_evals.evaluate(
            {"execution_path": "B", "validation_error_count": 0},
            {"assert": {"execution_path_eq": "B", "execution_path_in": ["B", "fallback"]}},
        )
        self.assertTrue(all(ok for _, ok, _ in checks))

    def test_run_metadata_is_required(self):
        results = [{"case": "fallback", "status": "PASS", "run_metadata": {}}]
        gate = run_evals.coverage_gate(results, [], [], {"min_pass": 1})
        self.assertFalse(gate["passed"])
        check = next(c for c in gate["checks"] if c["id"] == "required_run_metadata")
        self.assertEqual(check["actual"][0]["case"], "fallback")


class TestPathRouting(unittest.TestCase):
    def test_native_builder_wins_capability_order(self):
        path, _ = detect_capabilities.recommend({"python_pptx": True, "imagegen": True})
        self.assertEqual(path, "A")

    def test_html_wins_over_image_only(self):
        path, _ = detect_capabilities.recommend({"deck_stage": True, "imagegen": True})
        self.assertEqual(path, "C")

    def test_image_only_and_fallback(self):
        self.assertEqual(detect_capabilities.recommend({"imagegen": True})[0], "B")
        self.assertEqual(detect_capabilities.recommend({})[0], "fallback")


if __name__ == "__main__":
    unittest.main()
