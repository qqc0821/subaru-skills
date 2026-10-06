"""Typography contracts, negative resolution cases and real OOXML policy checks."""
from __future__ import annotations

import json
import sys
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "skills/subaru-slides/scripts"))
import typography as T
import detect_fonts as F
import validate_pptx as V
import check_style_system as S


class TestProfiles(unittest.TestCase):
    def setUp(self):
        self.foundation = T.read_json(T.SKILL_DIR / "styles/foundation.json")
        self.config = T.read_json(T.SKILL_DIR / "typography/profiles.json")

    def test_profile_inherits_sizes_and_aliases_without_mutating_source(self):
        original = deepcopy(self.foundation)
        roles = T.resolve_viewing_profile(self.foundation, "large-room")
        self.assertEqual(roles["cover-title"]["min_pt"], 48)
        self.assertEqual(roles["body"]["hard_min_pt"], 20)
        self.assertEqual(roles["metric-unit"], roles["body"])
        self.assertEqual(roles["display-title"], roles["cover-title"])
        roles["display-title"]["min_pt"] = 1
        self.assertEqual(self.foundation, original)

    def test_legacy_profile_implicitly_inherits_default(self):
        del self.foundation["profiles"]["large-room"]["inherits"]
        self.assertEqual(T.resolve_viewing_profile(self.foundation, "large-room")["section-title"]["min_pt"], 40)

    def test_cycles_and_unknown_aliases_are_rejected(self):
        self.foundation["profiles"]["meeting-room"]["inherits"] = "large-room"
        with self.assertRaises(ValueError):
            T.resolve_viewing_profile(self.foundation)
        self.foundation["profiles"]["meeting-room"].pop("inherits")
        self.foundation["role_aliases"]["display-title"] = "missing"
        with self.assertRaises(ValueError):
            T.resolve_viewing_profile(self.foundation)

    def test_script_cycle_is_rejected_before_font_discovery(self):
        self.config["profiles"]["portable-single"]["ea"] = {"same_as": "latin"}
        with self.assertRaises(ValueError):
            T.validate_configuration(self.foundation, self.config)

    def test_invalid_size_fails_contract(self):
        self.foundation["profiles"]["meeting-room"]["text_roles"]["body"]["max_pt"] = 1
        with self.assertRaises(ValueError):
            T.validate_configuration(self.foundation, self.config)

    def test_malformed_config_maps_fail_with_readable_errors(self):
        for change in [lambda c: c.update(role_styles=[]),
                       lambda c: c["profiles"].update({"bad": []}),
                       lambda c: c["profiles"]["portable-single"].update(style_fallbacks=[])]:
            config = deepcopy(self.config)
            change(config)
            with self.assertRaises(ValueError):
                T.validate_configuration(self.foundation, config)

    def test_make_check_contract_catches_invalid_font_config(self):
        with TemporaryDirectory() as tmp:
            skill = Path(tmp) / "subaru-slides"
            (skill / "typography").mkdir(parents=True)
            (skill / "styles").mkdir()
            foundation_path = skill / "styles/foundation.json"
            foundation_path.write_text(json.dumps(self.foundation))
            self.config["default_profile"] = "missing"
            (skill / "typography/profiles.json").write_text(json.dumps(self.config))
            keys = {f.key for f in S.validate_foundation(skill, foundation_path)}
            self.assertIn("typography-contract:subaru-slides", keys)

    def test_contract_accepts_partial_inherited_roles(self):
        self.foundation["profiles"]["large-room"]["text_roles"] = {}
        with TemporaryDirectory() as tmp:
            skill = Path(tmp) / "subaru-slides"
            (skill / "typography").mkdir(parents=True)
            (skill / "styles").mkdir()
            path = skill / "styles/foundation.json"
            path.write_text(json.dumps(self.foundation))
            (skill / "typography/profiles.json").write_text(json.dumps(self.config))
            self.assertEqual(S.validate_foundation(skill, path), [])

    def test_missing_optional_fonttools_is_unverified_not_absent(self):
        with patch.object(T, "fonttools_available", return_value=False):
            result = F.probe_profile("portable-single", include_system=False)
        self.assertEqual(result["status"], "unverified")
        self.assertEqual(result["verification"]["builder"], "unverified")
        self.assertIsNone(result["roles"]["body"]["ea"]["resolved"])

    def test_astral_han_and_punctuation_are_tested_in_correct_script(self):
        text = "客户𠀀， FlowDesk / ¥199"
        self.assertEqual(T.script_text(text, "ea"), "客户𠀀，")
        self.assertEqual(T.script_text(text, "latin"), "FlowDesk/¥199")


class TestFaceResolution(unittest.TestCase):
    def face(self, family="MiSans", style="Bold", weight=630, axes=None, width=5, italic=False):
        return {"family": family, "aliases": [family], "style": style, "weight": weight,
                "axes": axes or {}, "width": width, "italic": italic, "file": "font.ttf", "face_index": 0}

    @staticmethod
    def covered(face, text):
        return {"status": "verified", "missing": [], "tested_characters": len(set(text))}

    def test_named_bold_accepts_real_nonstandard_numeric_weight(self):
        result = T.choose_face(["MiSans"], "Bold", [self.face()], "中文", self.covered)
        self.assertEqual(result["resolved"]["weight"], 630)
        self.assertFalse(result["fallback"]["used"])

    def test_missing_semibold_is_not_faked_from_regular(self):
        result = T.choose_face(["MiSans"], "Semibold", [self.face(style="Regular", weight=330)], "中文", self.covered)
        self.assertIsNone(result["resolved"])
        self.assertEqual(result["fallback"]["attempts"][0]["reason"], "missing-static-face")

    def test_condensed_italic_and_variable_faces_do_not_pass_as_normal_static_bold(self):
        for overrides in [{"width": 3}, {"italic": True}, {"axes": {"wght": [100, 400, 900]}}]:
            result = T.choose_face(["MiSans"], "Bold", [self.face(**overrides)], "中文", self.covered)
            self.assertEqual(result["status"], "failed")

    def test_substring_family_match_does_not_accept_a_different_family(self):
        result = T.choose_face(["Noto Sans"], "Bold", [self.face(family="Noto Sans CJK SC")], "API", self.covered)
        self.assertEqual(result["status"], "failed")
        self.assertFalse(F.same_family("Noto Sans", "Noto Sans CJK SC"))

    def test_glyph_failure_triggers_declared_family_fallback_and_records_missing_char(self):
        def coverage(face, text):
            return {"status": "failed" if face["family"] == "MiSans" else "verified",
                    "missing": ["𠀀"] if face["family"] == "MiSans" else []}
        result = T.choose_face(["MiSans", "Noto Sans CJK SC"], "Bold",
                               [self.face(), self.face(family="Noto Sans CJK SC", weight=700)], "𠀀", coverage)
        self.assertEqual(result["resolved"]["family"], "Noto Sans CJK SC")
        self.assertTrue(result["fallback"]["used"])
        self.assertEqual(result["fallback"]["attempts"][0]["missing"], ["𠀀"])

    def test_declared_style_fallback_records_actual_face(self):
        face = self.face(family="PingFang SC", style="Semibold", weight=600)
        result = T.choose_face(["PingFang SC"], "Bold", [face], "中文", self.covered, ["Semibold"])
        self.assertEqual(result["requested"]["style"], "Bold")
        self.assertEqual(result["resolved"]["style"], "Semibold")
        self.assertTrue(result["fallback"]["used"])

    def test_no_glyph_coverage_claim_without_actual_text(self):
        result = T.choose_face(["MiSans"], "Bold", [self.face()], "", self.covered)
        self.assertEqual(result["coverage"]["status"], "unverified")


@unittest.skipUnless(T.fonttools_available(), "optional fontTools unavailable")
class TestFontFileIntegration(unittest.TestCase):
    def make_font(self, path):
        from fontTools.fontBuilder import FontBuilder
        from fontTools.pens.ttGlyphPen import TTGlyphPen
        builder = FontBuilder(1000, isTTF=True)
        names = [".notdef", "A", "uni4E2D"]
        builder.setupGlyphOrder(names)
        builder.setupCharacterMap({65: "A", 0x4E2D: "uni4E2D"})
        builder.setupGlyf({name: TTGlyphPen(None).glyph() for name in names})
        builder.setupHorizontalMetrics({name: (1000, 0) for name in names})
        builder.setupHorizontalHeader(ascent=800, descent=-200)
        builder.setupNameTable({"familyName": "Test Font", "styleName": "Regular",
                               "uniqueFontIdentifier": "TestFont-1", "fullName": "Test Font Regular",
                               "psName": "TestFont-Regular", "version": "Version 1.0"})
        builder.setupOS2(usWeightClass=330, sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
        builder.setupPost()
        builder.setupMaxp()
        builder.save(path)

    def test_real_binary_metadata_and_missing_glyphs(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "regular.ttf"
            self.make_font(path)
            face = T.inspect_font_file(path)[0]
            self.assertEqual(face["weight"], 330)
            self.assertEqual(face["postscript_name"], "TestFont-Regular")
            self.assertEqual(T.font_coverage(face, "中A")["status"], "verified")
            self.assertEqual(T.font_coverage(face, "中𠀀")["missing"], ["𠀀"])

    def test_real_profile_probe_distinguishes_cmap_from_renderer(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "regular.ttf"
            self.make_font(path)
            config = T.read_json(T.SKILL_DIR / "typography/profiles.json")
            config["role_styles"] = {}
            config["profiles"]["test"] = {"ea": {"families": ["Test Font"]}, "latin": {"same_as": "ea"}}
            cp = Path(tmp) / "profiles.json"
            cp.write_text(json.dumps(config))
            result = F.probe_profile("test", text="中 A", font_files=[path], include_system=False, config_path=cp)
            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["roles"]["body"]["ea"]["coverage"]["status"], "verified")
            self.assertEqual(result["verification"]["final_pptx_render"], "unverified")
            failed = F.probe_profile("test", text="𠀀", font_files=[path], include_system=False, config_path=cp)
            self.assertEqual(failed["status"], "failed")


class TestFontPolicy(unittest.TestCase):
    policy = {"roles": {"body": {"ea": ["Noto Sans CJK SC"], "latin": ["Helvetica Neue"]}}}

    def validate(self, runs, role="body", policy=None):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.pptx"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("ppt/presentation.xml", "<p:presentation xmlns:p='p'/>")
                z.writestr("ppt/slides/slide1.xml", f"<p:sld xmlns:p='p' xmlns:a='a'><p:spTree><p:sp><p:nvSpPr><p:cNvPr name='role={role}'/></p:nvSpPr><p:txBody><a:p>{runs}</a:p></p:txBody></p:sp></p:spTree></p:sld>")
            return {f.key for f in V.validate(str(path), policy or self.policy)}

    @staticmethod
    def xml_run(text="中文 API", ea="Noto Sans CJK SC", latin="Helvetica Neue"):
        return f"<a:r><a:rPr sz='2200' lang='zh-CN'><a:ea typeface='{ea}'/><a:latin typeface='{latin}'/></a:rPr><a:t>{text}</a:t></a:r>"

    def test_intentional_bilingual_pair_is_valid(self):
        keys = self.validate(self.xml_run())
        self.assertFalse(any(k.startswith(("mixed-fonts", "unexpected-font")) for k in keys))

    def test_third_family_is_reported_at_exact_run_and_script(self):
        keys = self.validate(self.xml_run()+self.xml_run(text="Extra", latin="Comic Sans MS"))
        self.assertIn("unexpected-font:1:0:1:latin", keys)

    def test_correct_family_on_wrong_script_still_fails(self):
        keys = self.validate(self.xml_run(ea="Helvetica Neue"))
        self.assertIn("unexpected-font:1:0:0:ea", keys)

    def test_unused_font_declaration_does_not_trigger_warning(self):
        keys = self.validate(self.xml_run(text="中文", latin="Comic Sans MS"))
        self.assertFalse(any(k.startswith("unexpected-font") for k in keys))

    def test_unknown_role_is_reported_without_wildcard(self):
        self.assertIn("font-policy-undeclared-role:1:0", self.validate(self.xml_run(), role="brand"))

    def test_inherited_theme_font_is_unverified_not_accepted(self):
        self.assertIn("font-policy-unverified:1:0:0:latin", self.validate(self.xml_run(latin="+mn-lt")))

    def test_paragraph_default_face_is_used_when_run_inherits_it(self):
        runs = "<a:pPr><a:defRPr><a:ea typeface='Noto Sans CJK SC'/><a:latin typeface='Helvetica Neue'/></a:defRPr></a:pPr><a:r><a:rPr sz='2200'/><a:t>中文 API</a:t></a:r>"
        keys = self.validate(runs)
        self.assertFalse(any(k.startswith(("font-policy-unverified", "unexpected-font")) for k in keys))

    def test_empty_policy_cannot_silence_mixed_fonts(self):
        with self.assertRaises(ValueError):
            V.validate_font_policy({"roles": {}})
        with self.assertRaises(ValueError):
            V.validate_font_policy({"roles": {"*": {"ea": [], "latin": []}}})


if __name__ == "__main__":
    unittest.main()
