from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from sdd_init.installer import install, shared_directory, snapshot
from test_build import WORKFLOW, builder, project_files


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

    def test_linked_projects_share_updates_and_git_ignores_local_link(self):
        self.assertEqual(install(self.resources, self.skills), "Installed")
        target = self.skills / "sdd-init"
        shared = shared_directory(self.skills)
        repos = [self.root / name for name in ("first", "second")]
        for repo in repos:
            repo.mkdir()
            subprocess.run(["git", "init", "-q", "--template=", str(repo)], check=True, capture_output=True)
            subprocess.run([sys.executable, "-B", "-X", "utf8", str(target / "scripts/govern.py"),
                            "--root", str(repo), "init"], check=True, capture_output=True)
            self.assertTrue((repo / WORKFLOW).samefile(shared))
            result = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
                                    check=True, capture_output=True, text=True)
            self.assertEqual(set(result.stdout.splitlines()),
                             {"?? .codex/config.toml", "?? .gitignore", "?? AGENTS.md"})
        worktree = self.root / "worktree"
        for command in (["add", "."], ["-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                                        "commit", "--no-gpg-sign", "-m", "project references"],
                        ["worktree", "add", "--detach", str(worktree)]):
            subprocess.run(["git", "-C", str(repos[0]), *command], check=True, capture_output=True)
        self.assertFalse((worktree / WORKFLOW).exists())
        refs = (worktree / ".codex/config.toml").read_bytes()
        subprocess.run([sys.executable, "-B", "-X", "utf8", str(target / "scripts/govern.py"),
                        "--root", str(worktree), "init"], check=True, capture_output=True)
        self.assertTrue((worktree / WORKFLOW).samefile(shared))
        self.assertEqual((worktree / ".codex/config.toml").read_bytes(), refs)
        repos.append(worktree)
        before = [{p.relative_to(repo): p.read_bytes() for p in project_files(repo)} for repo in repos]
        file = self.resources / "shared/skills/sdd-doc/SKILL.md"
        file.write_text("new workflow version", encoding="utf-8")
        self.change_release()
        self.assertEqual(install(self.resources, self.skills), "Updated")
        for repo, expected in zip(repos, before):
            self.assertEqual((repo / WORKFLOW / "skills/sdd-doc/SKILL.md").read_text(), "new workflow version")
            self.assertEqual({p.relative_to(repo): p.read_bytes() for p in project_files(repo)}, expected)

    def test_generated_bytecode_does_not_block_reinstall_or_upgrade(self):
        self.assertEqual(install(self.resources, self.skills), "Installed")
        target = self.skills / "sdd-init"
        subprocess.run(
            [sys.executable, "-E", "-X", "utf8", str(target / "scripts/govern.py"),
             "--root", str(self.root), "inspect"],
            check=True, capture_output=True,
        )
        self.assertTrue(list((target / "scripts/__pycache__").glob("project_install.*.pyc")))

        before = snapshot(target)
        self.assertEqual(install(self.resources, self.skills), "Already current")
        self.assertEqual(snapshot(target), before)

        self.change_release()
        self.assertEqual(install(self.resources, self.skills), "Updated")
        expected = snapshot(self.resources)
        self.assertEqual(snapshot(target), {name: digest for name, digest in expected.items()
                                           if not name.startswith("shared/")})
        self.assertEqual(snapshot(shared_directory(self.skills)), {
            name.removeprefix("shared/"): digest for name, digest in expected.items() if name.startswith("shared/")
        })

    def test_untracked_files_still_block_upgrade_around_bytecode_caches(self):
        for name in (
            "scripts/__pycache__/notes.txt",
            "scripts/__pycache__/custom.cpython-314.pyc",
            "scripts/project_install.pyc",
        ):
            with self.subTest(name=name):
                skills = self.root / Path(name).name
                install(self.resources, skills)
                target = skills / "sdd-init"
                extra = target / name
                extra.parent.mkdir(parents=True, exist_ok=True)
                extra.write_bytes(b"user file")
                before = snapshot(target)
                with self.assertRaisesRegex(ValueError, "Modified or untracked files"):
                    install(self.resources, skills)
                self.assertEqual(snapshot(target), before)

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

    def test_untracked_bytecode_in_distribution_does_not_create_destination(self):
        cache = self.resources / "scripts/__pycache__/project_install.cpython-314.pyc"
        cache.parent.mkdir()
        cache.write_bytes(b"untracked file")
        with self.assertRaisesRegex(ValueError, "Modified or untracked files"):
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
        old = self.skills / "sdd-init"
        shutil.copytree(self.resources, old, ignore=shutil.ignore_patterns("shared"))
        (old / "assets/repo-payload.zip").write_bytes(b"legacy distribution")
        (old / "build-manifest.json").write_text(json.dumps({"schema_version": 1, "files": snapshot(old)}))
        recovery.write_bytes(data)
        manifest.write_text(json.dumps({"schema_version": 1, "files": snapshot(self.resources)}))
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertEqual((self.skills / "sdd-init/scripts/project_install.py").read_bytes(), data)

    def test_failed_publish_rolls_back(self):
        install(self.resources, self.skills)
        before = snapshot(self.skills / "sdd-init")
        shared_before = snapshot(shared_directory(self.skills))
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
        self.assertEqual(snapshot(shared_directory(self.skills)), shared_before)

    def test_concurrent_install_is_rejected(self):
        self.skills.mkdir(parents=True)
        (self.skills / ".sdd-init-install.lock").touch()
        with self.assertRaises(FileExistsError):
            install(self.resources, self.skills)
        self.assertFalse((self.skills / "sdd-init").exists())
