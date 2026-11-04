from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from sdd_init.installer import install, snapshot
from test_build import builder


class UserInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.resources = builder.build(self.root / "resources")
        self.skills = self.root / "home/.agents/skills"

    def change_release(self):
        (self.resources / "SKILL.md").write_text("new release", encoding="utf-8")
        manifest = self.resources / "build-manifest.json"
        data = json.loads(manifest.read_text())
        data["files"] = snapshot(self.resources)
        manifest.write_text(json.dumps(data))

    def test_install_repeat_upgrade_and_project_isolation(self):
        project = self.root / "project"
        project.mkdir()
        (project / "custom.txt").write_text("keep")
        self.assertEqual(install(self.resources, self.skills), "Installed")
        self.assertEqual(install(self.resources, self.skills), "Already current")
        self.assertEqual(list(self.skills.iterdir()), [self.skills / "sdd-init"])
        self.assertEqual(len(list(self.skills.rglob("SKILL.md"))), 1)
        self.change_release()
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertEqual((self.skills / "sdd-init/SKILL.md").read_text(), "new release")
        self.assertEqual((project / "custom.txt").read_text(), "keep")

    def test_custom_missing_extra_and_unmanaged_files_block_without_writes(self):
        for kind in ("custom", "missing", "extra", "unmanaged"):
            with self.subTest(kind=kind):
                skills = self.root / kind
                install(self.resources, skills)
                target = skills / "sdd-init"
                if kind == "custom":
                    (target / "SKILL.md").write_text("custom")
                elif kind == "missing":
                    (target / "SKILL.md").unlink()
                elif kind == "extra":
                    (target / "notes.txt").write_text("personal")
                else:
                    (target / "build-manifest.json").unlink()
                before = snapshot(target)
                with self.assertRaises(ValueError):
                    install(self.resources, skills)
                self.assertEqual(snapshot(target), before)
                self.assertFalse((skills / ".sdd-init-install.lock").exists())

    def test_corrupt_distribution_does_not_create_destination(self):
        (self.resources / "SKILL.md").write_text("corrupt")
        with self.assertRaises(ValueError):
            install(self.resources, self.skills)
        self.assertFalse(self.skills.exists())

    def test_missing_recovery_module_rejected_and_old_install_can_upgrade(self):
        recovery = self.resources / "scripts/project_install.py"
        data = recovery.read_bytes()
        recovery.unlink()
        manifest = self.resources / "build-manifest.json"
        manifest.write_text(json.dumps({"schema_version": 1, "files": snapshot(self.resources)}))
        with self.assertRaisesRegex(ValueError, "project_install.py"):
            install(self.resources, self.skills)
        self.assertFalse(self.skills.exists())
        # Model an already installed, intact older release without this module.
        shutil.copytree(self.resources, self.skills / "sdd-init")
        recovery.write_bytes(data)
        manifest.write_text(json.dumps({"schema_version": 1, "files": snapshot(self.resources)}))
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertEqual((self.skills / "sdd-init/scripts/project_install.py").read_bytes(), data)

    def test_failed_publish_rolls_back(self):
        install(self.resources, self.skills)
        before = snapshot(self.skills / "sdd-init")
        self.change_release()
        rename = Path.rename
        def fail_stage(path, destination):
            if path.name == "skill":
                raise OSError("simulated publish failure")
            return rename(path, destination)
        with patch.object(Path, "rename", fail_stage):
            with self.assertRaises(OSError):
                install(self.resources, self.skills)
        self.assertEqual(snapshot(self.skills / "sdd-init"), before)

    def test_concurrent_install_is_rejected(self):
        self.skills.mkdir(parents=True)
        (self.skills / ".sdd-init-install.lock").touch()
        with self.assertRaises(FileExistsError):
            install(self.resources, self.skills)
        self.assertFalse((self.skills / "sdd-init").exists())
