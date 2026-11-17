import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("next_release_version", ROOT / "scripts/next_release_version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def metadata(version, newline="\n"):
    return f'[project]{newline}name = "sdd-init"{newline}version = "{version}"{newline}'


class ReleaseVersionTests(unittest.TestCase):
    def test_unchanged_or_older_candidate_increments_base_patch(self):
        for version in ("0.8.0", "0.7.4"):
            with self.subTest(version=version):
                chosen, updated = module.update_version(metadata("0.8.0"), metadata(version, "\r\n"))
                self.assertEqual(chosen, "0.8.1")
                self.assertEqual(updated, metadata("0.8.1", "\r\n"))

    def test_explicit_higher_version_is_preserved(self):
        candidate = metadata("1.0.0")
        self.assertEqual(module.update_version(metadata("0.8.0"), candidate), ("1.0.0", candidate))

    def test_rejects_unsupported_or_ambiguous_versions(self):
        for candidate in (metadata("0.8.1rc1"), metadata("0.08.1"),
                          metadata("0.8.0") + '[other]\nversion = "0.8.0"\n'):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    module.update_version(metadata("0.8.0"), candidate)

    def test_cli_updates_only_candidate_and_rejects_invalid_base(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "base.toml"
            candidate = Path(directory) / "candidate.toml"
            base.write_bytes(metadata("0.8.0").encode())
            candidate.write_bytes(metadata("0.8.0", "\r\n").encode())
            command = [sys.executable, "-B", str(ROOT / "scripts/next_release_version.py"),
                       "--base", str(base), "--project", str(candidate)]
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "0.8.1")
            self.assertEqual(candidate.read_bytes(), metadata("0.8.1", "\r\n").encode())
            base.write_bytes(metadata("invalid").encode())
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(candidate.read_bytes(), metadata("0.8.1", "\r\n").encode())


if __name__ == "__main__":
    unittest.main()
