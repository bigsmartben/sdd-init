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

    def test_new_install_has_only_current_skills_and_no_project_entities(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            {p.parent.name for p in (target / ".agents/skills").glob("*/SKILL.md")},
            {"sdd-doc", "sdd-imp", "sdd-accept", "sdd-commit"})
        for name in ("specs", "architecture", ".codex/config.toml", "plan.md"):
            self.assertFalse((target / name).exists(), name)
        for name in ("issue.md", "blueprint.md", "draft-pr.md", "acceptance.md", "prototype-reference.md"):
            self.assertTrue((target / ".agents/sdd/assets" / name).is_file(), name)

    def test_retired_skills_block_upgrade_before_writing(self):
        skill = builder.build(self.folder / "skill")
        for name in ("sdd-test-loop", "sdd-review-loop"):
            target = self.folder / name
            old = target / ".agents/skills" / name / "SKILL.md"
            old.parent.mkdir(parents=True)
            old.write_bytes(b"customized legacy instructions\n")
            before = {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)}
            result = subprocess.run(
                [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                 "--root", str(target), "init", "--update-skills"],
                capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(name, result.stderr)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in builder.source_files(target)})

    def test_missing_new_template_rejected_before_writing(self):
        skill = builder.build(self.folder / "skill")
        spec = importlib.util.spec_from_file_location("candidate_govern", skill / "scripts/govern.py")
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        broken = self.folder / "broken.zip"
        with zipfile.ZipFile(installer.PROJECT_PAYLOAD) as source, zipfile.ZipFile(broken, "w") as dest:
            for name in source.namelist():
                if name != ".agents/sdd/assets/issue.md":
                    dest.writestr(name, source.read(name))
        installer.PROJECT_PAYLOAD = broken
        target = self.folder / "project"
        target.mkdir()
        with self.assertRaises(ValueError):
            installer.cmd_init(target, installer.build_parser().parse_args(["init"]))
        self.assertEqual(list(target.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
