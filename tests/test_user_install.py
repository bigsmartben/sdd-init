from pathlib import Path
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from sdd_init.installer import install, recover_installation, shared_directory, snapshot
from sdd_init import installer
from sdd_init.cli import inspect
from sdd_init.release import (
    LOCK_BYTES, USER_LOCK, USER_ROLE_ASSET, WORKFLOW_REVIEW_ROLE, content_id, recovery_directory,
    shared_files, user_lock, verified,
)
from test_build import LEGACY_WORKFLOW, PROJECT_SKILLS, WORKFLOW, builder, legacy_fragment, project_files, refresh_manifest


class UserInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.resources = builder.build(self.root / "resources")
        self.skills = self.root / "home/.agents/skills"
        codex = self.root / "home/.codex"
        environment = patch.dict(os.environ, {"CODEX_HOME": str(codex)})
        environment.start()
        self.addCleanup(environment.stop)
        self.role = codex / "agents/review-prompt.toml"

    def install_legacy_role(self, role=None):
        role = role or self.role
        old_release = self.root / "legacy-user-role-release"
        shutil.copytree(self.resources, old_release)
        data = (old_release / WORKFLOW_REVIEW_ROLE).read_bytes()
        (old_release / WORKFLOW_REVIEW_ROLE).unlink()
        asset = old_release / USER_ROLE_ASSET
        asset.parent.mkdir(parents=True)
        asset.write_bytes(data)
        refresh_manifest(old_release)
        target = self.skills / "sdd-init"
        shutil.copytree(old_release, target, ignore=shutil.ignore_patterns("shared"))
        shutil.copytree(old_release / "shared", shared_directory(self.skills))
        manifest = target / "build-manifest.json"
        record = json.loads(manifest.read_bytes())
        record["user_role_path"] = str(role)
        manifest.write_text(json.dumps(record), encoding="utf-8")
        role.parent.mkdir(parents=True, exist_ok=True)
        role.write_bytes(data)
        return installer.verified_installation(target, shared_directory(self.skills), role)

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
        self.assertFalse(self.role.parent.exists())
        self.assertEqual(install(self.resources, self.skills), "Already current")
        self.assertEqual({p.name for p in self.skills.iterdir()}, {"sdd-init", USER_LOCK})
        self.assertEqual((self.skills / USER_LOCK).read_bytes(), LOCK_BYTES)
        self.assertEqual(len(list(self.skills.rglob("SKILL.md"))), 1)
        role_revision = (self.resources / WORKFLOW_REVIEW_ROLE).read_bytes() + b"\n# new reviewer\n"
        (self.resources / WORKFLOW_REVIEW_ROLE).write_bytes(role_revision)
        self.change_release()
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertEqual((self.skills / "sdd-init/SKILL.md").read_text(), "new release")
        self.assertEqual((shared_directory(self.skills) / "agents/review-prompt.toml").read_bytes(), role_revision)
        self.assertFalse(self.role.parent.exists())
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
            self.assertEqual({p.name for p in (repo / ".agents/skills").iterdir()}, set(PROJECT_SKILLS))
            for name in PROJECT_SKILLS:
                self.assertTrue((repo / ".agents/skills" / name).samefile(shared / "skills" / name))
            self.assertFalse((repo / LEGACY_WORKFLOW).exists())
            result = subprocess.run(["git", "--no-pager", "--no-optional-locks", "-C", str(repo),
                                     "status", "--porcelain", "--untracked-files=all"],
                                    check=True, capture_output=True, text=True)
            self.assertEqual(set(result.stdout.splitlines()),
                             {"?? .codex/config.toml", "?? .gitignore", "?? AGENTS.md"})
        worktree = self.root / "worktree"
        for command in (["add", "."], ["-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                                        "commit", "--no-gpg-sign", "-m", "project references"],
                        ["worktree", "add", "--detach", str(worktree)]):
            subprocess.run(["git", "-C", str(repos[0]), *command], check=True, capture_output=True)
        self.assertFalse((worktree / WORKFLOW).exists())
        for name in PROJECT_SKILLS:
            self.assertFalse((worktree / ".agents/skills" / name).exists())
        refs = (worktree / ".codex/config.toml").read_bytes()
        subprocess.run([sys.executable, "-B", "-X", "utf8", str(target / "scripts/govern.py"),
                        "--root", str(worktree), "init"], check=True, capture_output=True)
        self.assertTrue((worktree / WORKFLOW).samefile(shared))
        for name in PROJECT_SKILLS:
            self.assertTrue((worktree / ".agents/skills" / name).samefile(shared / "skills" / name))
        self.assertEqual((worktree / ".codex/config.toml").read_bytes(), refs)
        repos.append(worktree)
        before = [{p.relative_to(repo): p.read_bytes() for p in project_files(repo)} for repo in repos]
        role_path = "agents/sdd-architect.toml"
        role = self.resources / "shared" / role_path
        role.write_text(role.read_text(encoding="utf-8") + "\n# new workflow version\n", encoding="utf-8")
        skill_path = "skills/sdd-bugfix/SKILL.md"
        skill = self.resources / "shared" / skill_path
        skill.write_bytes(skill.read_bytes() + b"\n<!-- shared skill update -->\n")
        self.change_release()
        self.assertEqual(install(self.resources, self.skills), "Updated")
        for repo, expected in zip(repos, before):
            config = repo / ".codex/config.toml"
            ref = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]["sdd-architect"]["config_file"]
            self.assertTrue((config.parent / ref).samefile(shared / role_path))
            self.assertEqual((config.parent / ref).read_bytes(), role.read_bytes())
            entry = repo / ".agents/skills/sdd-bugfix/SKILL.md"
            self.assertTrue(entry.samefile(shared / skill_path))
            self.assertEqual(entry.read_bytes(), skill.read_bytes())
            self.assertEqual({p.relative_to(repo): p.read_bytes() for p in project_files(repo)}, expected)
        new_version = content_id(shared_files(verified(self.resources)))
        subprocess.run([sys.executable, "-B", "-X", "utf8", str(target / "scripts/govern.py"),
                        "--root", str(repos[0]), "init"], check=True, capture_output=True)
        self.assertEqual(json.loads((repos[0] / ".sdd-init-state.json").read_bytes())["shared_version"], new_version)
        for repo in repos[1:]:
            self.assertNotEqual(json.loads((repo / ".sdd-init-state.json").read_bytes())["shared_version"], new_version)

    def test_upgrade_retires_managed_skills_and_roles_and_registers_replacements(self):
        old_release = self.root / "old-release"
        shutil.copytree(self.resources, old_release)
        retired = {name: Path(f"skills/{name}/SKILL.md")
                   for name in ("sdd-doc", "sdd-imp", "sdd-review-code", "sdd-commit", "sdd-deploy", "sdd-review-prompt")}
        for name, relative in retired.items():
            old_skill = old_release / "shared" / relative
            old_skill.parent.mkdir(parents=True)
            old_skill.write_text(f"---\nname: {name}\ndescription: Retired workflow.\n---\n", encoding="utf-8")
            old_metadata = old_skill.parent / "agents/openai.yaml"
            old_metadata.parent.mkdir()
            old_metadata.write_text(f'interface:\n  display_name: "{name}"\n', encoding="utf-8")
        added_skills = ("sdd-develop", "sdd-architecture", "sdd-refactor")
        skill_files = ("SKILL.md", "agents/openai.yaml")
        for name in added_skills:
            for relative in skill_files:
                (old_release / "shared/skills" / name / relative).unlink()
        prompt_template = Path("sdd/assets/prompt_review_template.md")
        (old_release / "shared" / prompt_template).write_text("# Old prompt review template\n", encoding="utf-8")
        old_models = {
            "sdd-designer": "gpt-6-astra",
            "sdd-delivery": "gpt-6.1-terra",
            "sdd-documenter": "gpt-6.1-terra",
            "sdd-validator": "gpt-6.1-terra",
        }
        replacements = ("sdd-architect", "sdd-product-manager", "sdd-devops", "sdd-doc-consistency", "review-prompt")
        for name in replacements:
            (old_release / "shared/agents" / f"{name}.toml").unlink()
        for name, model in old_models.items():
            (old_release / "shared/agents" / f"{name}.toml").write_text(
                f'name = "{name}"\nmodel = "{model}"\ndescription = "Legacy role"\n'
                'developer_instructions = "Legacy instructions"\n', encoding="utf-8",
            )
        delivery_resources = (
            Path("sdd/references/traffic.md"),
            Path("sdd/references/recovery.md"),
            Path("sdd/assets/delivery_record_template.md"),
        )
        for path in delivery_resources:
            (old_release / "shared" / path).unlink()
        old_fragment = legacy_fragment("navigation")
        (old_release / "assets/agents-fragment.md").write_text(old_fragment + "\n", encoding="utf-8")
        refresh_manifest(old_release)
        shutil.copytree(old_release, self.skills / "sdd-init", ignore=shutil.ignore_patterns("shared"))
        shutil.copytree(old_release / "shared", shared_directory(self.skills))
        self.assertFalse(self.role.exists())

        project = self.root / "project"
        project.mkdir()
        shared = shared_directory(self.skills)
        govern = self.skills / "sdd-init/scripts/govern.py"
        init = [sys.executable, "-B", "-X", "utf8", str(govern), "--root", str(project), "init"]
        local_text = "# Project guidance\n"
        agents = project / "AGENTS.md"
        agents.write_text(local_text, encoding="utf-8")
        history = project / "docs/test-reports/orders/b1-review.md"
        history.parent.mkdir(parents=True)
        history_bytes = b"# Historical sdd-review-code\r\n\r\nCHK-001: FAIL at B1\r\n"
        history.write_bytes(history_bytes)
        config = project / ".codex/config.toml"
        config.parent.mkdir()
        project_settings = b'model = "project-choice"\r\n[mcp_servers.custom]\r\nurl = "https://example.invalid/mcp"\r\n'
        # Construct the historical on-disk layout instead of rewriting today's
        # installer to accept a release with a different fixed skill/link table.
        workflow = project / LEGACY_WORKFLOW
        spec = importlib.util.spec_from_file_location("legacy_link_fixture", govern.with_name("project_install.py"))
        transaction = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(transaction)
        transaction.create_workflow_link(workflow, shared)
        agents.write_text(local_text,
                          encoding="utf-8")
        old_role_names = sorted(set(old_models) | {"sdd-coder"})
        old_role_block = "# sdd-init roles:start\r\n" + "".join(
            f'[agents.{name}]\r\nconfig_file = "../{LEGACY_WORKFLOW}/agents/{name}.toml"\r\n'
            for name in old_role_names
        ) + "# sdd-init roles:end\r\n"
        config.write_bytes(project_settings + old_role_block.encode("utf-8"))
        (project / ".gitignore").write_bytes(f"/build/\r\n/{LEGACY_WORKFLOW}\r\n".encode())
        self.assertFalse((project / WORKFLOW).exists())
        for name in added_skills:
            self.assertFalse((workflow / "skills" / name / "SKILL.md").exists())
        for path in delivery_resources:
            self.assertFalse((workflow / path).exists())
        old_roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        self.assertEqual(set(old_roles), set(old_models) | {"sdd-coder"})
        for name in old_models:
            self.assertTrue((config.parent / old_roles[name]["config_file"]).samefile(shared / "agents" / f"{name}.toml"))
        for name, path in retired.items():
            self.assertTrue((workflow / path).samefile(shared / path))
        self.assertTrue((workflow / prompt_template).is_file())
        # Exercise resource/link migration without retaining legacy Main guidance.
        self.assertFalse((project / ".sdd-init-state.json").exists())

        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertFalse(self.role.exists())
        self.assertTrue(workflow.samefile(shared))
        for name in old_models:
            self.assertFalse((workflow / "agents" / f"{name}.toml").exists())
        for path in retired.values():
            self.assertFalse((workflow / path.parent).exists())
        self.assertFalse((workflow / prompt_template).exists())
        result = subprocess.run(init, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        workflow = project / WORKFLOW
        self.assertTrue(workflow.samefile(shared))
        self.assertFalse((project / LEGACY_WORKFLOW).exists())
        self.assertEqual({p.name for p in (project / ".agents/skills").iterdir()}, set(PROJECT_SKILLS))
        for name in PROJECT_SKILLS:
            path = project / ".agents/skills" / name
            self.assertTrue(path.samefile(shared / "skills" / name))
            if os.name == "nt":
                self.assertEqual(path.lstat().st_reparse_tag, 0xA0000003)
            else:
                self.assertTrue(path.is_symlink())
        guidance = agents.read_text(encoding="utf-8")
        self.assertIn(local_text, guidance)
        self.assertIn(f"({WORKFLOW}/sdd/references/delegation.md#实施交接)", guidance)
        self.assertIn("[sdd-deliver](.agents/skills/sdd-deliver/SKILL.md)", guidance)
        for path in delivery_resources:
            self.assertTrue((workflow / path).samefile(shared / path))
        for name in added_skills:
            self.assertIn(f"[{name}](.agents/skills/{name}/SKILL.md)", guidance)
            for relative in skill_files:
                self.assertTrue((project / ".agents/skills" / name / relative).samefile(
                    shared / "skills" / name / relative))
        for name in retired:
            self.assertNotIn(f"[{name}]", guidance)
        self.assertNotIn("/sdd-review-code/", guidance)
        self.assertEqual(history.read_bytes(), history_bytes)
        self.assertNotIn("sdd-documenter", guidance)
        after = config.read_bytes()
        self.assertTrue(after.startswith(project_settings))
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        self.assertEqual(set(roles), set(replacements) | {"sdd-coder"})
        for name in roles:
            self.assertTrue((config.parent / roles[name]["config_file"]).samefile(shared / "agents" / f"{name}.toml"))
        rules = Path("sdd/references/implementation.md")
        self.assertTrue((workflow / rules).samefile(shared / rules))
        subprocess.run(init, check=True, capture_output=True)
        self.assertEqual(config.read_bytes(), after)
        self.assertEqual(agents.read_text(encoding="utf-8"), guidance)

    def test_generated_bytecode_does_not_block_reinstall_or_upgrade(self):
        self.assertEqual(install(self.resources, self.skills), "Installed")
        target = self.skills / "sdd-init"
        subprocess.run([sys.executable, "-E", "-c",
                        "import sys; sys.path.insert(0, sys.argv[1]); import project_install",
                        str(target / "scripts")], check=True, capture_output=True)
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
                agents_dir = skills.with_suffix(".agents")
                install(self.resources, skills, agents_dir)
                target = skills / "sdd-init"
                extra = target / name
                extra.parent.mkdir(parents=True, exist_ok=True)
                extra.write_bytes(b"user file")
                before = snapshot(target)
                with self.assertRaisesRegex(ValueError, "Modified or untracked files"):
                    install(self.resources, skills, agents_dir)
                self.assertEqual(snapshot(target), before)

    def test_custom_missing_extra_and_unmanaged_files_block_without_writes(self):
        for kind in ("custom", "missing", "extra", "unmanaged"):
            with self.subTest(kind=kind):
                skills = self.root / kind
                agents_dir = skills.with_suffix(".agents")
                install(self.resources, skills, agents_dir)
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
                    install(self.resources, skills, agents_dir)
                self.assertEqual(snapshot(target), before)
                self.assertEqual((skills / USER_LOCK).read_bytes(), LOCK_BYTES)
                self.assertFalse(recovery_directory(skills).exists())

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

    def test_missing_manifest_verifier_blocks_distribution(self):
        (self.resources / "scripts/release.py").unlink()
        refresh_manifest(self.resources)
        with self.assertRaisesRegex(ValueError, "scripts/release.py"):
            install(self.resources, self.skills)
        self.assertFalse(self.skills.exists())

    def test_invalid_preset_role_blocks_distribution_before_installation(self):
        role = self.resources / WORKFLOW_REVIEW_ROLE
        for payload in (None, b'name = "wrong-role"\n'):
            with self.subTest(payload=payload):
                if payload is None:
                    role.unlink()
                else:
                    role.write_bytes(payload)
                refresh_manifest(self.resources)
                with self.assertRaisesRegex(ValueError, "review-prompt.toml"):
                    install(self.resources, self.skills)
                self.assertFalse(self.skills.exists())
                self.assertFalse(self.role.parent.exists())

    def test_unmanaged_user_roles_are_not_touched_or_registered_globally(self):
        for name, data in (
            (self.role.name, (self.resources / WORKFLOW_REVIEW_ROLE).read_bytes()),
            ("my-reviewer.toml", b'name = "review-prompt"\ndescription = "custom"\n'
             b'developer_instructions = "keep"\n'),
        ):
            with self.subTest(name=name):
                conflict = self.role.with_name(name)
                self.role.parent.mkdir(parents=True, exist_ok=True)
                conflict.write_bytes(data)
                install(self.resources, self.skills)
                self.assertEqual(conflict.read_bytes(), data)
                self.assertFalse((self.role.parent / installer.ROLE_LOCK).exists())
                conflict.unlink()

    def test_modified_recorded_role_is_retired_without_conflict_prompt(self):
        self.role.parent.mkdir(parents=True)
        other = self.role.with_name("custom.toml")
        settings = self.role.parent.parent / "config.toml"
        other.write_bytes(b'name = "review-prompt"\r\n')
        settings.write_bytes(b'model = "user-choice"\r\n')
        self.install_legacy_role()
        self.role.write_bytes(b"edited role")
        report = io.StringIO()
        with redirect_stdout(report):
            inspect(self.skills, self.resources)
        self.assertIn("Legacy user role to retire", report.getvalue())
        self.assertEqual(self.role.read_bytes(), b"edited role")
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertFalse(self.role.exists())
        self.assertEqual(other.read_bytes(), b'name = "review-prompt"\r\n')
        self.assertEqual(settings.read_bytes(), b'model = "user-choice"\r\n')
        self.assertEqual(install(self.resources, self.skills), "Already current")

    def test_missing_recorded_role_does_not_block_upgrade(self):
        self.install_legacy_role()
        self.role.unlink()
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertFalse(self.role.exists())
        self.assertEqual(install(self.resources, self.skills), "Already current")

    def test_new_installations_do_not_claim_or_lock_user_roles(self):
        other_skills = self.root / "other/skills"
        self.role.parent.mkdir(parents=True)
        with user_lock(self.role.parent, name=installer.ROLE_LOCK):
            self.assertEqual(install(self.resources, other_skills), "Installed")
            self.assertEqual(install(self.resources, self.skills), "Installed")
        self.assertFalse(self.role.exists())
        self.assertFalse((self.root / "other/agents/review-prompt.toml").exists())

    def test_upgrade_retires_recorded_user_role_and_refreshes_existing_project(self):
        recorded_role = self.root / "original-config/agents/review-prompt.toml"
        self.install_legacy_role(recorded_role)
        project = self.root / "connected-project"
        project.mkdir()
        command = [sys.executable, "-B", "-X", "utf8", str(self.skills / "sdd-init/scripts/govern.py"),
                   "--root", str(project), "init"]
        self.assertEqual(install(self.resources, self.skills), "Updated")
        subprocess.run(command, check=True, capture_output=True)
        config = project / ".codex/config.toml"
        current = config.read_text(encoding="utf-8")
        old = current.replace('[agents.review-prompt]\nconfig_file = "../.agents/sdd-workflow/agents/review-prompt.toml"\n', "")
        config.write_text(old, encoding="utf-8")
        subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(config.read_text(encoding="utf-8"), current)
        self.assertFalse(recorded_role.exists())
        self.assertFalse(self.role.exists())
        manifest = json.loads((self.skills / "sdd-init/build-manifest.json").read_bytes())
        self.assertNotIn("user_role_path", manifest)
        self.assertNotIn(USER_ROLE_ASSET, manifest["files"])
        self.assertEqual(install(self.resources, self.skills), "Already current")
        roles = tomllib.loads(current)["agents"]
        self.assertEqual(len(roles), 6)
        self.assertEqual(roles["review-prompt"]["config_file"], "../.agents/sdd-workflow/agents/review-prompt.toml")

    def test_failed_publish_rolls_back(self):
        install(self.resources, self.skills)
        before = snapshot(self.skills / "sdd-init")
        shared_before = snapshot(shared_directory(self.skills))
        self.change_release()
        rename = Path.rename
        def fail_stage(path, destination):
            if path.name == "stage":
                raise OSError("simulated publish failure")
            return rename(path, destination)
        with patch.object(Path, "rename", fail_stage):
            with self.assertRaises(OSError):
                install(self.resources, self.skills)
        self.assertEqual(snapshot(self.skills / "sdd-init"), before)
        self.assertEqual(snapshot(shared_directory(self.skills)), shared_before)

    def test_concurrent_install_is_rejected(self):
        self.skills.mkdir(parents=True)
        with user_lock(self.skills):
            with self.assertRaises(FileExistsError):
                install(self.resources, self.skills)
        self.assertEqual(install(self.resources, self.skills), "Installed")

    def test_legacy_lock_is_preserved(self):
        self.skills.mkdir(parents=True)
        (self.skills / USER_LOCK).touch()
        with self.assertRaises(FileExistsError):
            install(self.resources, self.skills)
        self.assertFalse((self.skills / "sdd-init").exists())
        self.assertEqual((self.skills / USER_LOCK).read_bytes(), b"")

    def crash_install(self, condition):
        code = """
import os, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from sdd_init.installer import install
original = Path.rename
def crash(path, destination):
    result = original(path, destination)
    if CONDITION:
        os._exit(79)
    return result
Path.rename = crash
install(Path(sys.argv[2]), Path(sys.argv[3]))
""".replace("CONDITION", condition)
        result = subprocess.run([sys.executable, "-B", "-c", code, str(ROOT / "src"),
                                 str(self.resources), str(self.skills), condition], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 79, result.stderr)

    def test_interrupted_shared_upgrade_can_recover_without_republishing(self):
        install(self.resources, self.skills)
        target = self.skills / "sdd-init"
        shared = shared_directory(self.skills)
        before = verified(target, shared=shared)
        self.change_release()
        self.crash_install("path.name == 'shared' and path.parent.name == 'stage'")
        self.assertFalse(target.exists())
        self.assertTrue((recovery_directory(self.skills) / "journal.json").is_file())
        self.assertTrue(recover_installation(self.skills))
        self.assertFalse(recover_installation(self.skills))
        self.assertEqual(verified(target, shared=shared), before)
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertEqual(install(self.resources, self.skills), "Already current")

    def test_interrupted_legacy_role_retirement_rolls_back_and_can_retry(self):
        before = self.install_legacy_role()
        previous = self.role.read_bytes()
        self.crash_install("path.name == 'review-prompt.toml'")
        self.assertFalse(self.role.exists())
        with self.assertRaisesRegex(ValueError, "original --agents-dir"):
            recover_installation(self.skills, self.root / "other/agents")
        self.assertTrue(recover_installation(self.skills))
        self.assertEqual(self.role.read_bytes(), previous)
        self.assertEqual(verified(self.skills / "sdd-init", shared=shared_directory(self.skills)), before)
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertFalse(self.role.exists())

    def test_interrupted_force_retirement_restores_modified_role_bytes(self):
        self.install_legacy_role()
        edited = b"locally modified legacy role"
        self.role.write_bytes(edited)
        self.crash_install("path.name == 'review-prompt.toml'")
        self.assertFalse(self.role.exists())
        self.assertTrue(recover_installation(self.skills))
        self.assertEqual(self.role.read_bytes(), edited)
        self.assertEqual(install(self.resources, self.skills), "Updated")
        self.assertFalse(self.role.exists())

    def test_failed_upgrade_restores_originally_missing_role_state(self):
        self.install_legacy_role()
        self.role.unlink()
        before = snapshot(self.skills / "sdd-init")
        rename = Path.rename
        def fail_stage(path, destination):
            if path.name == "stage":
                raise OSError("simulated publish failure")
            return rename(path, destination)
        with patch.object(Path, "rename", fail_stage):
            with self.assertRaises(OSError):
                install(self.resources, self.skills)
        self.assertEqual(snapshot(self.skills / "sdd-init"), before)
        self.assertFalse(self.role.exists())
        self.assertEqual(install(self.resources, self.skills), "Updated")

    def test_force_retirement_preserves_changed_backup_during_committed_recovery(self):
        self.install_legacy_role()
        self.role.write_bytes(b"edited before upgrade")
        role_folder = installer.role_recovery_directory(self.role, self.skills / "sdd-init")
        with patch.object(installer, "clean_role", side_effect=OSError("cleanup denied")):
            with self.assertRaisesRegex(ValueError, "Recovery blocked"):
                install(self.resources, self.skills)
        backup = role_folder / "old-role"
        self.assertEqual(backup.read_bytes(), b"edited before upgrade")
        backup.write_bytes(b"external change after upgrade")
        with self.assertRaisesRegex(ValueError, "Recovery blocked.*old-role"):
            recover_installation(self.skills)
        self.assertEqual(backup.read_bytes(), b"external change after upgrade")
        backup.write_bytes(b"edited before upgrade")
        self.assertTrue(recover_installation(self.skills))
        self.assertFalse(self.role.exists())

    def test_preexisting_user_role_publish_journal_can_recover_before_upgrade(self):
        files = self.install_legacy_role()
        target, shared, folder = installer.locations(self.skills)
        folder.mkdir()
        role_folder = installer.role_recovery_directory(self.role, target)
        role_folder.mkdir()
        os.link(self.role, role_folder / "stage")
        installer.save(folder, {"schema_version": 2, "target": str(target), "role": str(self.role),
                                "state": "prepared", "before": None, "after": files})
        self.assertTrue(recover_installation(self.skills))
        self.assertFalse(self.role.exists())
        self.assertFalse(target.exists())
        self.assertFalse(shared.exists())
        self.assertEqual(install(self.resources, self.skills), "Installed")
        self.assertFalse(self.role.exists())

    def test_interrupted_role_retirement_preserves_external_edit_then_can_restore(self):
        self.install_legacy_role()
        previous = self.role.read_bytes()
        self.crash_install("path.name == 'review-prompt.toml'")
        self.role.write_bytes(b"external edit")
        with self.assertRaisesRegex(ValueError, "Recovery blocked.*review-prompt"):
            recover_installation(self.skills)
        self.assertEqual(self.role.read_bytes(), b"external edit")
        self.assertFalse((self.skills / "sdd-init").exists())
        self.role.unlink()
        self.assertTrue(recover_installation(self.skills))
        self.assertEqual(self.role.read_bytes(), previous)
        self.assertEqual(install(self.resources, self.skills), "Updated")

    def test_shared_recovery_preserves_external_edit_and_corrupt_journal(self):
        install(self.resources, self.skills)
        self.change_release()
        self.crash_install("path.name == 'stage'")
        target = self.skills / "sdd-init"
        skill = target / "SKILL.md"
        written = skill.read_bytes()
        journal = recovery_directory(self.skills) / "journal.json"
        prepared = journal.read_bytes()
        skill.write_bytes(b"external edit")
        with self.assertRaisesRegex(ValueError, "Recovery blocked.*SKILL.md"):
            recover_installation(self.skills)
        self.assertEqual(skill.read_bytes(), b"external edit")
        self.assertEqual(journal.read_bytes(), prepared)
        skill.write_bytes(written)
        journal.write_bytes(b"damaged")
        with self.assertRaisesRegex(ValueError, "Recovery blocked"):
            install(self.resources, self.skills)
        self.assertEqual(journal.read_bytes(), b"damaged")
        self.assertEqual(skill.read_bytes(), written)
        journal.write_bytes(prepared)
        self.assertTrue(recover_installation(self.skills))

    def test_shared_cleanup_can_resume_after_commit(self):
        install(self.resources, self.skills)
        self.change_release()
        folder = recovery_directory(self.skills)
        with patch.object(installer, "clean", side_effect=OSError("cleanup denied")):
            with self.assertRaisesRegex(ValueError, "Recovery blocked"):
                install(self.resources, self.skills)
        self.assertEqual(json.loads((folder / "journal.json").read_bytes())["state"], "committed")
        self.assertTrue(recover_installation(self.skills))
        self.assertEqual(verified(self.skills / "sdd-init", shared=shared_directory(self.skills)),
                         verified(self.resources))
        self.assertFalse(folder.exists())

    def test_missing_journal_preserves_staged_resources(self):
        self.skills.mkdir(parents=True)
        folder = recovery_directory(self.skills)
        stage = folder / "stage"
        stage.mkdir(parents=True)
        staged_file = stage / "SKILL.md"
        staged_file.write_bytes(b"review recovery ownership")
        with self.assertRaisesRegex(ValueError, "Missing recovery journal"):
            install(self.resources, self.skills)
        self.assertEqual(staged_file.read_bytes(), b"review recovery ownership")
