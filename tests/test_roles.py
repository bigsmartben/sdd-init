"""Role distribution and installer boundaries, using isolated target projects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

from test_build import WORKFLOW, builder, project_entries, project_files, refresh_manifest

ROLES = {
    "review-prompt", "sdd-architect", "sdd-product-manager",
    "sdd-coder", "sdd-devops", "sdd-doc-consistency",
}
LEGACY_ROLES = ("sdd-delivery", "sdd-designer", "sdd-documenter", "sdd-validator")


class RoleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.skill = builder.build(self.folder / "skill")
        self.target = self.folder / "project"
        self.target.mkdir()

    def install(self, harness="auto"):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "--harness", harness, "init"],
            capture_output=True, text=True, encoding="utf-8")

    def snapshot(self):
        return {p.relative_to(self.target): p.read_bytes()
                for p in project_files(self.target)}

    def test_exact_roles_are_project_scoped_without_model_presets(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.target / ".codex/config.toml"
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        self.assertEqual(set(roles), ROLES)
        self.assertFalse((self.target / ".codex/agents").exists())
        for name, reference in roles.items():
            self.assertEqual(set(reference), {"config_file"})
            path = config.parent / reference["config_file"]
            self.assertTrue(path.samefile(self.skill / "shared/roles/codex" / f"{name}.toml"))
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], name)
            self.assertEqual(set(data), {"name", "description", "developer_instructions"})
            self.assertTrue(all(isinstance(v, str) and v.strip() for v in data.values()))
            copilot = self.target / ".github/agents" / f"{name}.agent.md"
            self.assertTrue(copilot.is_file())
            adapter = copilot.read_text(encoding="utf-8")
            self.assertNotIn("model:", adapter)
            self.assertNotIn("reasoning-effort:", adapter)
            self.assertIn(f"roles/shared/{name}.md", adapter)
        before = self.snapshot()
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(before, self.snapshot())

    def test_explicit_harness_selection_installs_only_requested_adapter(self):
        codex = self.install("codex")
        self.assertEqual(codex.returncode, 0, codex.stderr)
        self.assertTrue((self.target / ".codex/config.toml").is_file())
        self.assertFalse((self.target / ".github/agents").exists())

        other = self.folder / "copilot-only"
        other.mkdir()
        self.target = other
        copilot = self.install("copilot")
        self.assertEqual(copilot.returncode, 0, copilot.stderr)
        self.assertFalse((other / ".codex/config.toml").exists())
        for name in ROLES:
            path = other / ".github/agents" / f"{name}.agent.md"
            self.assertTrue(path.is_file())
            self.assertNotIn("model:", path.read_text(encoding="utf-8"))

    def test_copilot_only_preserves_codex_configuration_and_local_roles(self):
        config = self.target / ".codex/config.toml"
        local_role = self.target / ".codex/agents/sdd-coder.toml"
        config.parent.mkdir()
        local_role.parent.mkdir()
        config.write_bytes(b'model = "project-choice"\n')
        local_role.write_bytes(b'name = "sdd-coder"\nmodel = "custom-model"\n')
        before = self.snapshot()

        result = self.install("copilot")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_bytes(), before[config.relative_to(self.target)])
        self.assertEqual(local_role.read_bytes(), before[local_role.relative_to(self.target)])

    def test_inspect_reports_default_dual_adapter_plan_without_writes(self):
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "inspect"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("codex=none", result.stdout)
        self.assertIn("copilot=none", result.stdout)
        self.assertIn("Harness adapters planned: codex, copilot", result.stdout)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_inspect_reports_codex_and_copilot_project_markers_read_only(self):
        codex = self.target / ".codex/config.toml"
        codex.parent.mkdir()
        codex.write_text('model = "project-choice"\n', encoding="utf-8")
        instructions = self.target / ".github/copilot-instructions.md"
        instructions.parent.mkdir()
        instructions.write_text("# Project instructions\n", encoding="utf-8")
        before = self.snapshot()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "inspect"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("codex=.codex/config.toml", result.stdout)
        self.assertIn("copilot=.github/copilot-instructions.md", result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_unmanaged_same_name_copilot_role_is_preserved_before_any_writes(self):
        role = self.target / ".github/agents/sdd-coder.agent.md"
        role.parent.mkdir(parents=True)
        role.write_bytes(b"project-owned instructions\n")
        before = self.snapshot()

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unmanaged Copilot role collision", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_identical_copilot_role_records_missing_ownership(self):
        self.assertEqual(self.install().returncode, 0)
        role = self.target / ".github/agents/sdd-coder.agent.md"
        state_path = self.target / ".sdd-init-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["copilot_roles"].pop("sdd-coder")
        state_path.write_text(json.dumps(state), encoding="utf-8")

        result = self.install()

        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["copilot_roles"]["sdd-coder"], hashlib.sha256(role.read_bytes()).hexdigest())

    def test_identical_updated_copilot_role_refreshes_stale_ownership(self):
        self.assertEqual(self.install().returncode, 0)
        role = self.target / ".github/agents/sdd-coder.agent.md"
        source = self.skill / "shared/roles/copilot/sdd-coder.agent.md"
        updated = source.read_bytes() + b"\nupdated adapter\n"
        source.write_bytes(updated)
        refresh_manifest(self.skill)
        role.write_bytes(updated)

        result = self.install()

        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads((self.target / ".sdd-init-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["copilot_roles"]["sdd-coder"], hashlib.sha256(updated).hexdigest())

    def test_modified_owned_copilot_role_is_preserved(self):
        self.assertEqual(self.install().returncode, 0)
        role = self.target / ".github/agents/sdd-coder.agent.md"
        modified = role.read_bytes() + b"\nlocal customization\n"
        role.write_bytes(modified)

        result = self.install()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ownership check failed", result.stderr)
        self.assertEqual(role.read_bytes(), modified)

    def test_invalid_utf8_state_is_not_decoded_by_inspect_or_init(self):
        state = self.target / ".sdd-init-state.json"
        state.write_bytes(b"\xff")
        before = self.snapshot()

        inspect = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "inspect"],
            capture_output=True, text=True, encoding="utf-8")

        self.assertEqual(inspect.returncode, 0, inspect.stderr)
        self.assertEqual(self.snapshot(), before)

        result = self.install()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(state.read_bytes())["schema_version"], 1)

    def test_missing_or_pinned_copilot_adapter_fails_before_changes(self):
        entry = self.skill / "shared/roles/copilot/sdd-coder.agent.md"
        original = entry.read_bytes()
        newline = b"\r\n" if b"\r\n" in original else b"\n"
        cases = (
            None,
            original.replace(b'name: "sdd-coder"', b'name: "other-role"'),
            original.replace(b"---" + newline, b"---" + newline + b"model: preset" + newline, 1),
            original.replace(b"---" + newline, b"---" + newline + b"reasoning-effort: high" + newline, 1),
        )
        for data in cases:
            with self.subTest(data=data):
                if data is None:
                    entry.unlink()
                else:
                    entry.write_bytes(data)
                refresh_manifest(self.skill)
                result = self.install()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(project_entries(self.target), [])
                if data is None:
                    entry.write_bytes(original)
        entry.write_bytes(original)
        refresh_manifest(self.skill)

    def test_same_name_role_is_replaced_and_unrelated_roles_survive(self):
        role = self.target / ".codex/agents/sdd-coder.toml"
        role.parent.mkdir(parents=True)
        role.write_bytes(b'name = "sdd-coder"\nmodel = "my-role-model"\n')
        config = self.target / ".codex/config.toml"
        original = b'model = "user-choice"\r\n[agents]\r\nenabled = false\r\n'
        config.write_bytes(original)
        custom = role.with_name("user-role.toml")
        custom.write_bytes(b'name = "user-role"\n')
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(role.exists())
        self.assertTrue(config.read_bytes().startswith(original))
        self.assertEqual(custom.read_bytes(), b'name = "user-role"\n')

    def test_same_name_role_configuration_is_overwritten(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = (b'model = "main-model"\n[agents.other]\nconfig_file = "other.toml"\n'
                    b'[agents.sdd-coder]\nconfig_file = "local.toml"\n')
        config.write_bytes(original)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        desired = config.read_bytes()
        values = tomllib.loads(desired.decode("utf-8"))
        self.assertEqual(values["model"], "main-model")
        self.assertEqual(values["agents"]["other"]["config_file"], "other.toml")
        self.assertEqual(values["agents"]["sdd-coder"]["config_file"],
                         "../.agents/sdd-workflow/roles/codex/sdd-coder.toml")
        customized = desired.replace(b"../.agents/sdd-workflow/", b"../old/")
        config.write_bytes(customized)
        upgraded = self.install()
        self.assertEqual(upgraded.returncode, 0, upgraded.stderr)
        self.assertEqual(config.read_bytes(), desired)
        config.write_bytes(desired.replace(
            b'config_file = "../.agents/sdd-workflow/roles/codex/sdd-coder.toml"',
            b'config_file = "agents/sdd-coder.toml"',
        ))
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(config.read_bytes(), desired)

    def test_inline_same_name_role_configuration_is_overwritten(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        config.write_text('[agents]\nenabled = false\n'
                          'sdd-coder = { config_file = "project-role.toml" }\n'
                          'other = { config_file = "other.toml" }\n', encoding="utf-8")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        self.assertFalse(roles["enabled"])
        self.assertEqual(roles["other"]["config_file"], "other.toml")
        self.assertEqual(roles["sdd-coder"]["config_file"], "../.agents/sdd-workflow/roles/codex/sdd-coder.toml")

    def test_dotted_and_quoted_same_name_role_configuration_is_overwritten(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        for original in (
            'agents."sdd-coder".config_file = "old.toml"\nmodel = "keep"\n',
            '[agents]\n"sdd-coder".config_file = "old.toml"\nenabled = false\n',
            '[agents."sdd-coder"]\nconfig_file = "old.toml"\n'
            '[agents."sdd-coder".settings]\ncustom = true\n',
        ):
            with self.subTest(original=original):
                config.write_text(original, encoding="utf-8")
                result = self.install()
                self.assertEqual(result.returncode, 0, result.stderr)
                roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
                self.assertEqual(roles["sdd-coder"], {
                    "config_file": "../.agents/sdd-workflow/roles/codex/sdd-coder.toml"})

    def test_non_table_agents_setting_is_replaced(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        for original in ('model = "keep"\nagents = false\n',
                         'agents = [\n  "old",\n  "another",\n]\nmodel = "keep"\n'):
            with self.subTest(original=original):
                config.write_text(original, encoding="utf-8")
                result = self.install()
                self.assertEqual(result.returncode, 0, result.stderr)
                values = tomllib.loads(config.read_text(encoding="utf-8"))
                self.assertEqual(values["model"], "keep")
                self.assertEqual(set(values["agents"]), ROLES)

    def test_root_inline_agents_table_is_expanded_and_conflict_overwritten(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = ('agents = { "sdd-coder" = { config_file = "old.toml" }, '
                    'other = { description = "keep, {text}", config_file = "other.toml" } } # retain\n'
                    'model = "keep"\n')
        config.write_text(original, encoding="utf-8")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        values = tomllib.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(values["model"], "keep")
        self.assertEqual(values["agents"]["other"]["description"], "keep, {text}")
        self.assertEqual(values["agents"]["sdd-coder"]["config_file"],
                         "../.agents/sdd-workflow/roles/codex/sdd-coder.toml")
        self.assertIn("# retain", config.read_text(encoding="utf-8"))

    def test_multiline_conflicting_role_value_is_overwritten(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        for original in (
            '[agents]\nsdd-coder = [\n  "old",\n  "other",\n]\nenabled = false\n',
            'agents.sdd-coder = [\n  "old",\n]\nmodel = "keep"\n',
        ):
            with self.subTest(original=original):
                config.write_text(original, encoding="utf-8")
                result = self.install()
                self.assertEqual(result.returncode, 0, result.stderr)
                values = tomllib.loads(config.read_text(encoding="utf-8"))
                self.assertEqual(values["agents"]["sdd-coder"]["config_file"],
                                 "../.agents/sdd-workflow/roles/codex/sdd-coder.toml")
                if "model" in values:
                    self.assertEqual(values["model"], "keep")
                else:
                    self.assertFalse(values["agents"]["enabled"])

    def test_customized_legacy_references_in_managed_block_are_replaced(self):
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
                    outcome = self.install()
                    self.assertEqual(outcome.returncode, 0, outcome.stderr)
                    result = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
                    self.assertEqual(set(result), ROLES)

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

    def test_project_conflicts_for_replacement_roles_are_overwritten(self):
        for name in ("sdd-devops", "sdd-architect", "sdd-product-manager", "sdd-doc-consistency", "review-prompt"):
            with self.subTest(name=name):
                project = self.folder / f"conflict-{name}"
                local_roles = project / ".codex/agents"
                local_roles.mkdir(parents=True)
                config = project / ".codex/config.toml"
                config.write_text(f'[agents.{name}]\nconfig_file = "project-role.toml"\n', encoding="utf-8")
                local = local_roles / f"{name}.toml"
                local.write_text(f'name = "{name}"\n', encoding="utf-8")
                outcome = subprocess.run(
                    [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
                     "--root", str(project), "init"], capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(outcome.returncode, 0, outcome.stderr)
                self.assertFalse(local.exists())
                roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
                self.assertEqual(roles[name]["config_file"], f"../.agents/sdd-workflow/roles/codex/{name}.toml")

    def test_invalid_shared_roles_fail_before_any_write(self):
        entry = self.skill / "shared/roles/codex/sdd-product-manager.toml"
        original = entry.read_bytes().replace(b"\r\n", b"\n")
        cases = {
            "missing": None,
            "malformed": b"name = [",
            "wrong_name": original.replace(b'name = "sdd-product-manager"', b'name = "other"'),
            "fixed_model": b'model = "preset"\n' + original,
            "fixed_effort": b'model_reasoning_effort = "high"\n' + original,
            "unexpected_setting": b'sandbox_mode = "danger-full-access"\n' + original,
            "empty_description": b'name = "sdd-product-manager"\n'
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
        entry = self.skill / "shared/roles/codex/sdd-architect.toml"
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
        path = self.skill / "shared/roles/codex/unlisted.toml"
        path.write_text('model = "forced"\\n', encoding="utf-8")
        refresh_manifest(self.skill)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertEqual(project_entries(self.target), [])

    def test_consistency_role_inherits_sandbox(self):
        name = "sdd-doc-consistency"
        entry = self.skill / "shared/roles/codex" / f"{name}.toml"
        original = entry.read_bytes().replace(b"\r\n", b"\n")
        cases = {
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
