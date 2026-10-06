"""Public-site regression checks; no browser or third-party packages required."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_site import build, versions
from check_site import inspect


class TestPublicSite(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = build(Path(self.temp.name), "https://example.test/project/")

    def test_clean_build_and_project_paths(self):
        self.assertEqual(inspect(self.site), [])
        english = (self.site / "en/index.html").read_text()
        self.assertIn('href="../index.html"', english)
        self.assertIn('src="../examples/management-report/preview.webp"', english)
        self.assertIn('https://example.test/project/en/index.html', english)
        self.assertEqual(len(list(self.site.rglob("*.html"))), 16)
        for version in versions().values():
            self.assertIn(version, english)

    def test_missing_asset_is_blocking(self):
        (self.site / "examples/management-report/preview.webp").unlink()
        self.assertTrue(any("broken" in failure for failure in inspect(self.site)))

    def test_missing_anchor_is_blocking(self):
        page = self.site / "index.html"
        page.write_text(page.read_text().replace('cases.html#management-report', 'cases.html#does-not-exist'))
        self.assertTrue(any("missing anchor" in failure for failure in inspect(self.site)))

    def test_corrupt_download_is_blocking(self):
        (self.site / "examples/rag-sharing/deck.pptx").write_bytes(b"corrupt")
        self.assertTrue(any("hash mismatch" in failure for failure in inspect(self.site)))

    def test_invalid_sitemap_is_blocking(self):
        (self.site / "sitemap.xml").write_text("not xml")
        self.assertTrue(any("sitemap" in failure for failure in inspect(self.site)))

    def test_missing_seo_metadata_is_blocking(self):
        page = self.site / "index.html"
        page.write_text(page.read_text().replace('name="description"', 'name="removed"'))
        self.assertTrue(any("description/canonical" in failure for failure in inspect(self.site)))


if __name__ == "__main__":
    unittest.main()
