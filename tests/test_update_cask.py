import copy
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.update_cask import BASE_URL, download_sha256, update_cask

ROOT = Path(__file__).resolve().parents[1]


class UpdateCaskTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "harbor.rb"
        self.original = (ROOT / "Casks/harbor.rb").read_text()
        self.path.write_text(self.original)
        self.release = {"tag_name": "v1.10.0", "assets": [
            {"name": f"Harbor-1.10.0-{suffix}.dmg",
             "browser_download_url": f"{BASE_URL}/v1.10.0/Harbor-1.10.0-{suffix}.dmg",
             "digest": "sha256:" + checksum}
            for suffix, checksum in [("Apple-Silicon", "a" * 64), ("Intel", "b" * 64)]
        ]}

    def download(self, asset):
        return "a" * 64 if "Apple-Silicon" in asset["name"] else "b" * 64

    def assert_rejected(self, release=None, downloader=None):
        before = self.path.read_bytes()
        with self.assertRaises((ValueError, subprocess.CalledProcessError)):
            update_cask(release or self.release, self.path, downloader or self.download)
        self.assertEqual(self.path.read_bytes(), before)

    def test_updates_both_architectures_and_preserves_rest(self):
        self.assertEqual(update_cask(self.release, self.path, self.download), "1.10.0")
        text = self.path.read_text()
        self.assertIn('version "1.10.0"', text)
        self.assertIn('on_arm do\n    sha256 "' + "a" * 64 + '"', text)
        self.assertIn('on_intel do\n    sha256 "' + "b" * 64 + '"', text)
        self.assertEqual(text[text.index('  url '):], self.original[self.original.index('  url '):])
        # An already-current release is a no-op, including file mtime.
        mtime = self.path.stat().st_mtime_ns
        update_cask(self.release, self.path, self.download)
        self.assertEqual(self.path.stat().st_mtime_ns, mtime)

    def test_missing_or_duplicate_asset(self):
        for assets in [self.release["assets"][:1], self.release["assets"] + self.release["assets"][:1], []]:
            with self.subTest(assets=assets):
                release = dict(self.release, assets=assets)
                self.assert_rejected(release)

    def test_legacy_single_dmg_rejected(self):
        release = copy.deepcopy(self.release)
        release["assets"][0]["name"] = "Harbor-1.10.0.dmg"
        self.assert_rejected(release)

    def test_invalid_tag(self):
        for tag in ["1.10.0", "v1.10.0-beta", "v1.10", "v1.10.0\n"]:
            with self.subTest(tag=tag):
                self.assert_rejected(dict(self.release, tag_name=tag))

    def test_unexpected_url(self):
        release = copy.deepcopy(self.release)
        release["assets"][0]["browser_download_url"] = "https://example.com/file.dmg"
        self.assert_rejected(release)

    def test_second_download_failure_does_not_write(self):
        def download(asset):
            if "Intel" in asset["name"]:
                raise subprocess.CalledProcessError(22, "curl")
            return self.download(asset)
        self.assert_rejected(downloader=download)

    def test_digest_mismatch_and_invalid_checksum(self):
        for checksum in ["c" * 64, "invalid"]:
            with self.subTest(checksum=checksum):
                self.assert_rejected(downloader=lambda asset: checksum)

    def test_changed_cask_layout_does_not_write(self):
        for text in [self.original.replace("on_intel", "on_other"),
                     self.original.replace("-#{arch}.dmg", ".dmg"),
                     self.original + '  version "duplicate"\n']:
            with self.subTest(text=text):
                self.path.write_text(text)
                self.assert_rejected()

    def test_optional_github_digest(self):
        release = copy.deepcopy(self.release)
        for asset in release["assets"]:
            asset.pop("digest")
        update_cask(release, self.path, self.download)
        self.assertIn('version "1.10.0"', self.path.read_text())

    def test_download_hashes_bytes_and_uses_retry(self):
        def curl(command, check):
            self.assertTrue(check)
            self.assertIn("--fail", command)
            self.assertIn("--retry", command)
            Path(command[command.index("--output") + 1]).write_bytes(b"test dmg bytes")
        with patch("scripts.update_cask.subprocess.run", side_effect=curl):
            result = download_sha256(self.release["assets"][0])
        self.assertEqual(result, hashlib.sha256(b"test dmg bytes").hexdigest())


if __name__ == "__main__":
    unittest.main()
