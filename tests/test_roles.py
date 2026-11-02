"""Role distribution and installer boundaries, using isolated target projects."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile

from test_build import builder

ROLES = {
    "sdd-requirements", "sdd-architect", "sdd-planner", "sdd-documenter",
    "sdd-implementer", "sdd-acceptor", "sdd-delivery",
}


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
                for p in self.target.rglob("*") if p.is_file()}

    def test_exact_roles_are_project_scoped_and_model_neutral(self):
        self.assertEqual([p for p in self.skill.rglob("*.toml") if p.stem in ROLES], [])
        self.assertFalse((self.skill / ".codex").exists())
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = list((self.target / ".codex/agents").glob("*.toml"))
        self.assertEqual({p.stem for p in paths}, ROLES)
        for path in paths:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], path.stem)
            self.assertEqual(set(data), {"name", "description", "developer_instructions"})
            self.assertTrue(all(isinstance(v, str) and v.strip() for v in data.values()))
        self.assertFalse((self.target / ".codex/config.toml").exists())
        before = self.snapshot()
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, self.snapshot())

    def test_role_conflict_blocks_all_writes_then_explicit_upgrade_preserves_config(self):
        role = self.target / ".codex/agents/sdd-documenter.toml"
        role.parent.mkdir(parents=True)
        role.write_bytes(b'name = "sdd-documenter"\n# local customization\n')
        config = self.target / ".codex/config.toml"
        config.write_bytes(b'model = "user-choice"\nmodel_reasoning_effort = "high"\n[agents]\nenabled = false\n')
        custom = role.with_name("user-role.toml")
        custom.write_bytes(b'name = "user-role"\n')
        before = self.snapshot()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sdd-documenter.toml", result.stderr)
        self.assertEqual(before, self.snapshot())
        result = self.install("--update-skills")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_bytes(), before[config.relative_to(self.target)])
        self.assertEqual(custom.read_bytes(), before[custom.relative_to(self.target)])
        self.assertNotIn(b"local customization", role.read_bytes())

    def test_invalid_role_payloads_fail_before_any_write(self):
        entry = ".codex/agents/sdd-planner.toml"
        with zipfile.ZipFile(self.skill / "assets/repo-payload.zip") as archive:
            original = {name: archive.read(name) for name in archive.namelist()}
        cases = {
            "missing": None,
            "malformed": b"name = [",
            "wrong_name": original[entry].replace(b'name = "sdd-planner"', b'name = "other"'),
            "fixed_model": original[entry] + b'\nmodel = "gpt-6-astra"\n',
            "fixed_effort": original[entry] + b'\nmodel_reasoning_effort = "high"\n',
            "empty_description": b'name = "sdd-planner"\ndescription = ""\ndeveloper_instructions = "plan"\n',
        }
        for label, data in cases.items():
            with self.subTest(label=label):
                broken = self.folder / (label + ".zip")
                with zipfile.ZipFile(broken, "w") as archive:
                    for name, content in original.items():
                        if name != entry:
                            archive.writestr(name, content)
                        elif data is not None:
                            archive.writestr(name, data)
                spec = importlib.util.spec_from_file_location("role_installer", self.skill / "scripts/govern.py")
                installer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(installer)
                installer.PROJECT_PAYLOAD = broken
                with self.assertRaises(ValueError):
                    installer.cmd_init(self.target, installer.build_parser().parse_args(["init"]))
                self.assertEqual(list(self.target.iterdir()), [])

    def test_payload_cannot_install_user_runtime_configuration_or_unknown_roles(self):
        for entry in (".codex/config.toml", ".codex/agents/unlisted.toml"):
            with self.subTest(entry=entry):
                spec = importlib.util.spec_from_file_location("role_installer", self.skill / "scripts/govern.py")
                installer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(installer)
                broken = self.folder / "unexpected.zip"
                with zipfile.ZipFile(installer.PROJECT_PAYLOAD) as source, zipfile.ZipFile(broken, "w") as dest:
                    for name in source.namelist():
                        dest.writestr(name, source.read(name))
                    dest.writestr(entry, b'model = "forced"\n')
                installer.PROJECT_PAYLOAD = broken
                with self.assertRaises(ValueError):
                    installer.cmd_init(self.target, installer.build_parser().parse_args(["init"]))
                self.assertEqual(list(self.target.iterdir()), [])
