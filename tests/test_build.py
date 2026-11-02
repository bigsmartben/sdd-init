from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def test_payload_and_shared_resources_match_canonical_source(self):
        output = builder.build(self.folder / "skill")
        project = ROOT / "source/project"
        expected = {p.relative_to(project).as_posix(): p.read_bytes() for p in builder.source_files(project)}
        with zipfile.ZipFile(output / "assets/repo-payload.zip") as archive:
            self.assertEqual(set(archive.namelist()), set(expected))
            for name, data in expected.items():
                self.assertEqual(archive.read(name), data)
        for directory in ("assets", "references"):
            source = project / ".agents/sdd" / directory
            for path in builder.source_files(source):
                self.assertEqual(path.read_bytes(), (output / directory / path.relative_to(source)).read_bytes())

    def test_build_is_reproducible_and_does_not_overwrite(self):
        first = builder.build(self.folder / "first")
        second = builder.build(self.folder / "second")
        contents = lambda p: {f.relative_to(p): f.read_bytes() for f in builder.source_files(p)}
        self.assertEqual(contents(first), contents(second))
        with self.assertRaises(FileExistsError):
            builder.build(first)
        with self.assertRaises(ValueError):
            builder.build(ROOT / "source/not-an-output")

    def test_generated_installer_is_idempotent_and_preserves_existing_contract(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        (target / "architecture").mkdir()
        contract = target / "architecture/blueprint.md"
        contract.write_bytes(b"# Existing architecture\n")
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(contract.read_bytes(), b"# Existing architecture\n")
        before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})


if __name__ == "__main__":
    unittest.main()
