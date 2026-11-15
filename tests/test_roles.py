"""Role distribution and installer boundaries, using isolated target projects."""
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

from test_build import WORKFLOW, builder, project_entries, project_files, refresh_manifest

ROLE_MODELS = {
    "sdd-architect": "gpt-6-astra",
    "sdd-product-manager": "gpt-6-astra",
    "sdd-coder": "gpt-6.1-sol",
    "sdd-devops": "gpt-6.1-terra",
    "sdd-doc-consistency": "gpt-6.1-terra",
}
ROLES = set(ROLE_MODELS)
LEGACY_ROLES = ("sdd-delivery", "sdd-designer", "sdd-documenter", "sdd-validator")


class RoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.skill = builder.build(self.folder / "skill")
        self.target = self.folder / "project"
        self.target.mkdir()

    def install(self):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "init"],
            capture_output=True, text=True, encoding="utf-8")

    def snapshot(self):
        return {p.relative_to(self.target): p.read_bytes()
                for p in project_files(self.target)}

    def test_exact_roles_are_project_scoped_with_default_models(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.target / ".codex/config.toml"
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        self.assertEqual(set(roles), ROLES)
        self.assertFalse((self.target / ".codex/agents").exists())
        for name, reference in roles.items():
            self.assertEqual(set(reference), {"config_file"})
            path = config.parent / reference["config_file"]
            self.assertTrue(path.samefile(self.skill / "shared/agents" / f"{name}.toml"))
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], name)
            self.assertEqual(set(data), {"name", "description", "model", "developer_instructions"})
            self.assertEqual(data["model"], ROLE_MODELS[name])
            self.assertTrue(all(isinstance(v, str) and v.strip() for v in data.values()))
        before = self.snapshot()
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, self.snapshot())

    def test_same_name_role_conflicts_and_unrelated_roles_survive(self):
        role = self.target / ".codex/agents/sdd-coder.toml"
        role.parent.mkdir(parents=True)
        role.write_bytes(b'name = "sdd-coder"\nmodel = "my-role-model"\n')
        config = self.target / ".codex/config.toml"
        original = b'model = "user-choice"\r\n[agents]\r\nenabled = false\r\n'
        config.write_bytes(original)
        custom = role.with_name("user-role.toml")
        custom.write_bytes(b'name = "user-role"\n')
        before = self.snapshot()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sdd-coder.toml", result.stderr)
        self.assertEqual(before, self.snapshot())
        role.rename(self.folder / "preserved-role.toml")
        self.assertEqual(self.install().returncode, 0)
        self.assertTrue(config.read_bytes().startswith(original))
        self.assertEqual(custom.read_bytes(), before[custom.relative_to(self.target)])

    def test_unmanaged_role_conflicts_and_only_managed_references_can_upgrade(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = b'[agents.sdd-coder]\nconfig_file = "local.toml"\n'
        config.write_bytes(original)
        denied = self.install()
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(config.read_bytes(), original)
        self.assertFalse((self.target / WORKFLOW).exists())
        config.write_bytes(b'model = "main-model"\n')
        self.assertEqual(self.install().returncode, 0)
        desired = config.read_bytes()
        customized = desired.replace(b"../.agents/sdd-workflow/", b"../old/")
        config.write_bytes(customized)
        denied = self.install()
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("角色引用块含定制", denied.stderr)
        self.assertEqual(config.read_bytes(), customized)
        config.write_bytes(desired.replace(
            b'config_file = "../.agents/sdd-workflow/agents/sdd-coder.toml"',
            b'config_file = "agents/sdd-coder.toml"',
        ))
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(config.read_bytes(), desired)

    def test_customized_legacy_references_in_managed_block_are_not_removed(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        for name in LEGACY_ROLES:
            for reference in (
                'config_file = "project-role.toml"\n',
                f'config_file = "../{WORKFLOW}/agents/{name}.toml"\ndescription = "Project role"\n',
            ):
                with self.subTest(name=name, reference=reference):
                    config.write_text(f"# sdd-init roles:start\n[agents.{name}]\n{reference}# sdd-init roles:end\n",
                                      encoding="utf-8")
                    before = self.snapshot()
                    outcome = self.install()
                    self.assertNotEqual(outcome.returncode, 0)
                    self.assertEqual(self.snapshot(), before)
                    self.assertFalse((self.target / WORKFLOW).exists())

    def test_legacy_project_roles_outside_managed_block_survive(self):
        config = self.target / ".codex/config.toml"
        local_roles = config.parent / "agents"
        local_roles.mkdir(parents=True)
        references = "".join(f'[agents.{name}]\nconfig_file = "agents/{name}.toml"\n' for name in LEGACY_ROLES)
        config.write_bytes(references.encode())
        for name in LEGACY_ROLES:
            (local_roles / f"{name}.toml").write_text(f'name = "{name}"\n', encoding="utf-8")
        before = self.snapshot()
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(config.read_bytes().startswith(references.encode()))
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        self.assertEqual(set(roles), ROLES | set(LEGACY_ROLES))
        for name in LEGACY_ROLES:
            role = config.parent / roles[name]["config_file"]
            self.assertEqual(role.read_bytes(), before[role.relative_to(self.target)])

    def test_project_conflicts_for_replacement_roles_fail_before_changes(self):
        config = self.target / ".codex/config.toml"
        local_roles = config.parent / "agents"
        local_roles.mkdir(parents=True)
        for name in ("sdd-devops", "sdd-architect", "sdd-product-manager", "sdd-doc-consistency"):
            with self.subTest(name=name, location="config"):
                config.write_text(f'[agents.{name}]\nconfig_file = "project-role.toml"\n', encoding="utf-8")
                before = self.snapshot()
                outcome = self.install()
                self.assertNotEqual(outcome.returncode, 0)
                self.assertIn(name, outcome.stderr)
                self.assertEqual(self.snapshot(), before)
                self.assertFalse((self.target / WORKFLOW).exists())
                config.unlink()
            with self.subTest(name=name, location="file"):
                local = local_roles / f"{name}.toml"
                local.write_text(f'name = "{name}"\n', encoding="utf-8")
                before = self.snapshot()
                outcome = self.install()
                self.assertNotEqual(outcome.returncode, 0)
                self.assertIn(f"{name}.toml", outcome.stderr)
                self.assertEqual(self.snapshot(), before)
                self.assertFalse((self.target / WORKFLOW).exists())
                local.unlink()

    def test_invalid_shared_roles_fail_before_any_write(self):
        entry = self.skill / "shared/agents/sdd-product-manager.toml"
        original = entry.read_bytes().replace(b"\r\n", b"\n")
        cases = {
            "missing": None,
            "malformed": b"name = [",
            "wrong_name": original.replace(b'name = "sdd-product-manager"', b'name = "other"'),
            "missing_model": original.replace(b'model = "gpt-6-astra"\n', b""),
            "empty_model": original.replace(b'model = "gpt-6-astra"', b'model = ""'),
            "blank_model": original.replace(b'model = "gpt-6-astra"', b'model = "  "'),
            "non_text_model": original.replace(b'model = "gpt-6-astra"', b'model = 42'),
            "wrong_model": original.replace(b'model = "gpt-6-astra"', b'model = "gpt-6.1-sol"'),
            "fixed_effort": original + b'\nmodel_reasoning_effort = "high"\n',
            "unexpected_setting": original + b'\nsandbox_mode = "danger-full-access"\n',
            "empty_description": b'name = "sdd-product-manager"\nmodel = "gpt-6-astra"\n'
                                 b'description = ""\ndeveloper_instructions = "plan"\n',
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                if data is None:
                    entry.unlink()
                else:
                    entry.write_bytes(data)
                refresh_manifest(self.skill)
                self.assertNotEqual(self.install().returncode, 0)
                self.assertEqual(project_entries(self.target), [])

    def test_missing_and_malformed_architect_role_fail_before_changes(self):
        entry = self.skill / "shared/agents/sdd-architect.toml"
        entry.unlink()
        refresh_manifest(self.skill)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(project_entries(self.target), [])

        entry.write_bytes(b"name = [")
        refresh_manifest(self.skill)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sdd-architect", result.stderr)
        self.assertEqual(project_entries(self.target), [])

    def test_unknown_shared_role_is_rejected(self):
        path = self.skill / "shared/agents/unlisted.toml"
        path.write_text('model = "forced"\\n', encoding="utf-8")
        refresh_manifest(self.skill)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(project_entries(self.target), [])

    def test_consistency_role_requires_default_model_and_inherits_sandbox(self):
        name = "sdd-doc-consistency"
        entry = self.skill / "shared/agents" / f"{name}.toml"
        original = entry.read_bytes().replace(b"\r\n", b"\n")
        cases = {
            "missing_model": original.replace(b'model = "gpt-6.1-terra"\n', b""),
            "wrong_model": original.replace(b'model = "gpt-6.1-terra"', b'model = "gpt-6.1-sol"'),
            "legacy_read_only_override": original + b'\nsandbox_mode = "read-only"\n',
            "workspace_write_override": original + b'\nsandbox_mode = "workspace-write"\n',
            "full_access_override": original + b'\nsandbox_mode = "danger-full-access"\n',
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                entry.write_bytes(data)
                refresh_manifest(self.skill)
                result = self.install()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(name, result.stderr)
                self.assertEqual(project_entries(self.target), [])
