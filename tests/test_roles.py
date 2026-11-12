"""Role distribution and installer boundaries, using isolated target projects."""
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

from test_build import WORKFLOW, builder, project_entries, project_files, refresh_manifest

ROLE_MODELS = {
    "sdd-designer": "gpt-6-astra",
    "sdd-coder": "gpt-6.1-sol",
    "sdd-documenter": "gpt-6.1-terra",
    "sdd-validator": "gpt-6.1-terra",
    "sdd-delivery": "gpt-6.1-terra",
}
ROLES = set(ROLE_MODELS)


class RoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.skill = builder.build(self.folder / "skill")
        self.target = self.folder / "project"
        self.target.mkdir()

    def install(self, *args):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "init", *args],
            capture_output=True, text=True, encoding="utf-8")

    def snapshot(self):
        return {p.relative_to(self.target): p.read_bytes()
                for p in project_files(self.target)}

    def test_exact_roles_are_project_scoped_with_default_models_and_no_effort(self):
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

    def test_legacy_role_requires_migration_and_unrelated_roles_survive(self):
        role = self.target / ".codex/agents/sdd-documenter.toml"
        role.parent.mkdir(parents=True)
        role.write_bytes(b'name = "sdd-documenter"\nmodel = "my-role-model"\n')
        config = self.target / ".codex/config.toml"
        original = b'model = "user-choice"\r\n[agents]\r\nenabled = false\r\n'
        config.write_bytes(original)
        custom = role.with_name("user-role.toml")
        custom.write_bytes(b'name = "user-role"\n')
        before = self.snapshot()
        for args in ([], ["--update-skills"]):
            result = self.install(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sdd-documenter.toml", result.stderr)
            self.assertEqual(before, self.snapshot())
        role.rename(self.folder / "preserved-role.toml")
        self.assertEqual(self.install("--update-skills").returncode, 0)
        self.assertTrue(config.read_bytes().startswith(original))
        self.assertEqual(custom.read_bytes(), before[custom.relative_to(self.target)])

    def test_unmanaged_role_conflicts_and_only_managed_references_can_upgrade(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = b'[agents.sdd-coder]\nconfig_file = "local.toml"\n'
        config.write_bytes(original)
        denied = self.install("--update-skills")
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(config.read_bytes(), original)
        self.assertFalse((self.target / WORKFLOW).exists())
        config.write_bytes(b'model = "main-model"\n')
        self.assertEqual(self.install().returncode, 0)
        desired = config.read_bytes()
        config.write_bytes(desired.replace(b"../.agents/skills/sdd-workflow/", b"../old/"))
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(self.install("--update-skills").returncode, 0)
        self.assertEqual(config.read_bytes(), desired)

    def test_invalid_shared_roles_fail_before_any_write(self):
        entry = self.skill / "shared/agents/sdd-designer.toml"
        original = entry.read_bytes().replace(b"\r\n", b"\n")
        cases = {
            "missing": None,
            "malformed": b"name = [",
            "wrong_name": original.replace(b'name = "sdd-designer"', b'name = "other"'),
            "missing_model": original.replace(b'model = "gpt-6-astra"\n', b""),
            "empty_model": original.replace(b'model = "gpt-6-astra"', b'model = ""'),
            "blank_model": original.replace(b'model = "gpt-6-astra"', b'model = "  "'),
            "non_text_model": original.replace(b'model = "gpt-6-astra"', b'model = 42'),
            "wrong_model": original.replace(b'model = "gpt-6-astra"', b'model = "gpt-6.1-sol"'),
            "fixed_effort": original + b'\nmodel_reasoning_effort = "high"\n',
            "unexpected_setting": original + b'\nsandbox_mode = "danger-full-access"\n',
            "empty_description": b'name = "sdd-designer"\nmodel = "gpt-6-astra"\ndescription = ""\ndeveloper_instructions = "plan"\n',
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

    def test_unknown_shared_role_is_rejected(self):
        path = self.skill / "shared/agents/unlisted.toml"
        path.write_text('model = "forced"\\n', encoding="utf-8")
        refresh_manifest(self.skill)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(project_entries(self.target), [])
