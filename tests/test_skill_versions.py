"""Package version regression checks; no external dependencies."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import validate_skills as V


class TestSkillVersions(unittest.TestCase):
    def version_findings(self, metadata):
        with TemporaryDirectory() as tmp:
            pkg = Path(tmp) / 'example'
            pkg.mkdir()
            (pkg / 'SKILL.md').write_text(
                '---\nname: example\ndescription: Use when exploring a question.\n'
                + metadata + '\n---\n', encoding='utf-8')
            return [f.key for f in V.check_skill(pkg) if 'version' in f.key]

    def test_missing_and_malformed_metadata(self):
        for metadata in ('', 'metadata: invalid', 'metadata:\n  author: example'):
            with self.subTest(metadata=metadata):
                self.assertEqual(self.version_findings(metadata), ['example:missing-version'])

    def test_semver_acceptance_and_rejection(self):
        valid = ('0.1.0', '1.2.3', '0.2.0-dev.0', '1.0.0-rc.1+build.02')
        invalid = ('v1.0.0', '1.0', '01.0.0', '1.0.0-01', '1.0.0-', '1.0.0+a..b', '1.0.0\n')
        for version in valid:
            with self.subTest(version=version):
                self.assertEqual(self.version_findings('metadata:\n  version: "' + version + '"'), [])
        for version in invalid:
            with self.subTest(version=version):
                self.assertFalse(V.VERSION_RE.fullmatch(version))
                if '\n' not in version:
                    self.assertEqual(self.version_findings('metadata:\n  version: "' + version + '"'), ['example:version-format'])

    def test_schema_and_validator_contract_match(self):
        schema = json.loads((ROOT / 'schemas/skill.frontmatter.schema.json').read_text())
        self.assertIn('metadata', schema['required'])
        metadata = schema['properties']['metadata']
        self.assertIn('version', metadata['required'])
        self.assertEqual(metadata['properties']['version']['pattern'], V.VERSION_RE.pattern)


if __name__ == '__main__':
    unittest.main()
