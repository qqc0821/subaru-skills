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
import run_evals  # noqa: E402
import html_deck_inspect  # noqa: E402
import renderer_locate  # noqa: E402
import check_consistency  # noqa: E402
import check_style_system  # noqa: E402
import pptx_inspect  # noqa: E402
import validate_pptx  # noqa: E402

DETECT_SPEC = importlib.util.spec_from_file_location(
    "detect_capabilities", ROOT / "skills" / "subaru-slides" / "scripts" / "detect_capabilities.py"
)
detect_capabilities = importlib.util.module_from_spec(DETECT_SPEC)
DETECT_SPEC.loader.exec_module(detect_capabilities)

FONT_SPEC = importlib.util.spec_from_file_location(
    "detect_fonts", ROOT / "skills" / "subaru-slides" / "scripts" / "detect_fonts.py"
)
detect_fonts = importlib.util.module_from_spec(FONT_SPEC)
FONT_SPEC.loader.exec_module(detect_fonts)

SKILL = C.ROOT / "skills" / "subaru-slides"


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
        self.assertEqual(data["foundation"], "styles/foundation.json")
        self.assertTrue((SKILL / data["foundation"]).is_file())
        self.assertEqual(data["count"], len(data["styles"]))
        ids = [s["id"] for s in data["styles"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in data["styles"]:
            if s.get("sample"):
                self.assertTrue((SKILL / s["sample"]).exists(), s["id"] + " sample missing")

    def test_samples_use_their_style_ids(self):
        data = json.loads(C.read_text(SKILL / "styles" / "index.json"))
        for s in data["styles"]:
            if s.get("sample"):
                self.assertEqual(Path(s["sample"]).name, s["id"] + ".webp")

    def test_presets_match_registry_samples(self):
        data = json.loads(C.read_text(SKILL / "styles" / "index.json"))
        for s in data["styles"]:
            frontmatter, _ = C.parse_frontmatter(C.read_text(SKILL / s["preset"]))
            preset_sample = frontmatter.get("sample")
            if preset_sample == "null":
                preset_sample = None
            self.assertEqual(preset_sample, s.get("sample"), s["id"] + " preset sample mismatch")

    def test_theme_recommendations_resolve(self):
        data = json.loads(C.read_text(SKILL / "styles" / "index.json"))
        ids = {s["id"] for s in data["styles"]}
        for rec in data["theme_recommendations"]:
            for slot in ("first", "second", "third"):
                if rec.get(slot):
                    self.assertIn(rec[slot], ids, "unknown style in " + str(rec.get("theme")))


class TestSemanticQualityGuards(unittest.TestCase):
    def test_corrupt_marker_guard_ignores_fenced_examples(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "guide.md"
            path.write_text("visible @@ marker\n```text\nfenced @@ marker\n```\n", encoding="utf-8")
            findings = check_consistency.corrupt_marker_findings([path])
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0].line, 1)

    def test_noncanonical_style_sample_is_rejected(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            skill = Path(tmp) / "demo-skill"
            samples = skill / "assets" / "style-samples"
            styles = skill / "styles"
            samples.mkdir(parents=True)
            styles.mkdir()
            (styles / "foundation.json").write_text(json.dumps({
                "schema_version": 1,
                "default_profile": "default",
                "profiles": {"default": {"text_roles": {
                    "slide-title": {}, "body": {}, "diagram-node": {}, "footnote": {},
                }}},
                "cjk": {}, "layout": {}, "accessibility": {}, "autofit": {},
            }), encoding="utf-8")
            (samples / "legacy.webp").write_bytes(b"webp")
            (styles / "demo.md").write_text(
                "---\nid: demo\nsample: assets/style-samples/legacy.webp\n---\n",
                encoding="utf-8",
            )
            index = styles / "index.json"
            index.write_text(json.dumps({
                "count": 1,
                "foundation": "styles/foundation.json",
                "styles": [{
                    "id": "demo",
                    "sample": "assets/style-samples/legacy.webp",
                    "preset": "styles/demo.md",
                }],
            }), encoding="utf-8")
            keys = {f.key for f in check_style_system.validate_index(skill, index)}
            self.assertIn("noncanonical-sample:demo-skill:demo", keys)
            self.assertIn("unexpected-sample:demo-skill:legacy.webp", keys)

class TestDeckTools(unittest.TestCase):
    def test_shape_metadata_is_parsed_for_quality_rules(self):
        self.assertEqual(
            validate_pptx.parse_shape_metadata("role=node;group=journey;index=01"),
            {"role": "node", "group": "journey", "index": "01"},
        )
        self.assertEqual(validate_pptx.parse_shape_metadata("not metadata"), {})

    def test_cjk_probe_uses_foundation_candidates(self):
        result = detect_fonts.probe("zh-CN", "linux")
        self.assertEqual(result["foundation"], "styles/foundation.json")
        self.assertTrue(result["candidates"])

    def test_inspector_reports_new_quality_metrics_for_a_minimal_deck(self):
        from tempfile import TemporaryDirectory
        import zipfile

        with TemporaryDirectory() as tmp:
            pptx = Path(tmp) / "deck.pptx"
            with zipfile.ZipFile(pptx, "w") as zf:
                zf.writestr("ppt/presentation.xml", "<p:presentation xmlns:p='p'><p:sldIdLst><p:sldId/></p:sldIdLst></p:presentation>")
                zf.writestr("ppt/slides/slide1.xml", """
                    <p:sld xmlns:p='p' xmlns:a='a'><p:spTree><p:sp>
                    <p:txBody><a:p><a:r><a:rPr sz='2000' lang='zh-CN'><a:ea typeface='Noto Sans CJK SC'/></a:rPr><a:t>中文</a:t></a:r></a:p></p:txBody>
                    </p:sp></p:spTree></p:sld>""")
            metrics = pptx_inspect.inspect(str(pptx))
            self.assertEqual(metrics["cjk_text_shape_count"], 1)
            self.assertEqual(metrics["cjk_shapes_with_east_asian_font_count"], 1)
            self.assertEqual(metrics["min_font_size_pt"], 20.0)

    def test_validator_flags_cjk_without_east_asian_font_metadata(self):
        from tempfile import TemporaryDirectory
        import zipfile

        with TemporaryDirectory() as tmp:
            pptx = Path(tmp) / "deck.pptx"
            with zipfile.ZipFile(pptx, "w") as zf:
                zf.writestr("ppt/presentation.xml", "<p:presentation xmlns:p='p'/>")
                zf.writestr("ppt/slides/slide1.xml", """
                    <p:sld xmlns:p='p' xmlns:a='a'><p:spTree><p:sp>
                    <p:txBody><a:p><a:r><a:rPr sz='1800'/><a:t>中文</a:t></a:r></a:p></p:txBody>
                    </p:sp></p:spTree></p:sld>""")
            keys = {finding.key for finding in validate_pptx.validate(str(pptx))}
            self.assertIn("cjk-missing-ea-font:1:0", keys)
            self.assertIn("cjk-missing-language:1:0", keys)

    def test_validator_flags_small_content_text_but_not_a_footnote(self):
        from tempfile import TemporaryDirectory
        import zipfile

        with TemporaryDirectory() as tmp:
            pptx = Path(tmp) / "deck.pptx"
            with zipfile.ZipFile(pptx, "w") as zf:
                zf.writestr("ppt/presentation.xml", "<p:presentation xmlns:p='p'/>")
                zf.writestr("ppt/slides/slide1.xml", """
                    <p:sld xmlns:p='p' xmlns:a='a'><p:spTree>
                    <p:sp><p:nvSpPr><p:cNvPr name='role=body'/></p:nvSpPr><p:txBody><a:p><a:r><a:rPr sz='1400'/><a:t>Too small</a:t></a:r></a:p></p:txBody></p:sp>
                    <p:sp><p:nvSpPr><p:cNvPr name='role=footnote'/></p:nvSpPr><p:txBody><a:p><a:r><a:rPr sz='1000'/><a:t>Source</a:t></a:r></a:p></p:txBody></p:sp>
                    </p:spTree></p:sld>""")
            keys = {finding.key for finding in validate_pptx.validate(str(pptx))}
            self.assertIn("font-below-minimum:1:0", keys)
            self.assertNotIn("font-below-minimum:1:1", keys)
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


class TestRendererLocate(unittest.TestCase):
    def _fake(self, root, relative):
        path = Path(root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\n", encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_home_glob_discovers_override_renderer(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            exe = self._fake(tmp, ".cache/codex-runtimes/rt-1/dependencies/bin/override/soffice")
            self.assertEqual(
                renderer_locate.locate(
                    names=[],
                    env_names=[],
                    abs_paths=[],
                    home_globs=renderer_locate.HOME_GLOBS_SOFFICE,
                    home=tmp,
                ),
                str(exe),
            )

    def test_missing_renderer_returns_none(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            self.assertIsNone(
                renderer_locate.locate(
                    names=[], home_globs=(".cache/absent/*/soffice",), home=tmp
                )
            )

    def test_env_override_wins_over_home_glob(self):
        import os
        from tempfile import TemporaryDirectory
        from unittest import mock

        with TemporaryDirectory() as tmp:
            override = self._fake(tmp, "custom/soffice")
            other = self._fake(tmp, ".cache/codex-runtimes/rt-9/dependencies/bin/override/soffice")
            with mock.patch.dict(os.environ, {"SOFFICE_BIN": str(override)}):
                self.assertEqual(renderer_locate.find_soffice(home=tmp), str(override))
            self.assertNotEqual(str(override), str(other))


class TestInstalledPackageIsStandalone(unittest.TestCase):
    """A consumer only receives skills/<name>/ — it must run with no repository around it."""

    def test_capability_probe_runs_from_an_isolated_copy(self):
        import shutil
        import subprocess
        from tempfile import TemporaryDirectory

        pkg = ROOT / "skills" / "subaru-slides"
        with TemporaryDirectory() as tmp:
            installed = Path(tmp) / "skills" / pkg.name
            shutil.copytree(pkg, installed, ignore=shutil.ignore_patterns("__pycache__"))

            # Nothing of the repository is reachable from this copy.
            self.assertFalse((Path(tmp) / "tools").exists())

            proc = subprocess.run(
                [sys.executable, str(installed / "scripts" / "detect_capabilities.py")],
                cwd=tmp, capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("recommended path:", proc.stdout)
            self.assertIn("order: A -> B2 -> C -> B -> fallback", proc.stdout)

            fonts = subprocess.run(
                [sys.executable, str(installed / "scripts" / "detect_fonts.py"), "--doctor"],
                cwd=tmp, capture_output=True, text=True,
            )
            self.assertEqual(fonts.returncode, 0, fonts.stderr)
            self.assertIn("detect_fonts doctor", fonts.stdout)

class TestInstallabilityBoundary(unittest.TestCase):
    """Reference to repository-only tooling breaks the moment the skill is installed.

    The 'allowed' cases matter as much as the caught ones: `make new-task` and
    `make new-style` scaffold local files and stay valid for a consumer.
    """

    CAUGHT = [
        ("AGENTS.md", "see AGENTS.md for the rules"),
        ("make check", "run make check before committing"),
        ("make validate", "run make validate PPTX=deck.pptx"),
        ("make render", "run make render PPTX=deck.pptx"),
        ("make montage", "run make montage DIR=slides"),
        ("tools script", "use tools/validate_pptx.py on the deck"),
        ("schemas file", "see schemas/style.preset.schema.json"),
        ("parent tools", "see ../../tools/check.sh"),
        ("parent schemas", "see ../../schemas/x.json"),
    ]
    ALLOWED = [
        ("make new-task", "scaffold with make new-task"),
        ("make new-style", "scaffold with make new-style ID=x NAME=y"),
        ("own script", "run scripts/detect_capabilities.py"),
        ("own reference", "read references/qa/checklist.md"),
        ("styles index", "read styles/index.json"),
    ]

    def _check(self, body):
        import importlib
        from tempfile import TemporaryDirectory

        if "check_installability" not in sys.modules:
            sys.path.insert(0, str(ROOT / "tools"))
        check = importlib.import_module("check_installability")

        with TemporaryDirectory() as tmp:
            pkg = Path(tmp) / "demo-skill"
            pkg.mkdir()
            (pkg / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: d\n---\n\n" + body + "\n",
                encoding="utf-8",
            )
            return check.check_skill(pkg)

    def test_repository_only_references_are_caught(self):
        for label, body in self.CAUGHT:
            with self.subTest(case=label):
                keys = {f.key for f in self._check(body)}
                self.assertTrue(any("repo-only" in k for k in keys), (label, keys))

    def test_consumer_valid_commands_are_allowed(self):
        for label, body in self.ALLOWED:
            with self.subTest(case=label):
                keys = {f.key for f in self._check(body)}
                self.assertFalse(any("repo-only" in k for k in keys), (label, keys))

    def test_unclosed_repo_only_marker_is_caught(self):
        keys = {f.key for f in self._check("<!-- repo-only -->\nunclosed passage")}
        self.assertTrue(any("unbalanced" in k for k in keys), keys)

    def test_marked_passage_is_skipped(self):
        body = "<!-- repo-only -->\nrun make check\n<!-- /repo-only -->"
        keys = {f.key for f in self._check(body)}
        self.assertFalse(any("repo-only-dependency" in k for k in keys), keys)

    def test_shipped_skill_passes_the_boundary_check(self):
        import importlib

        if "check_installability" not in sys.modules:
            sys.path.insert(0, str(ROOT / "tools"))
        check = importlib.import_module("check_installability")
        findings = check.check_skill(ROOT / "skills" / "subaru-slides")
        self.assertEqual(findings, [], [f.key for f in findings])


if __name__ == "__main__":
    unittest.main()
