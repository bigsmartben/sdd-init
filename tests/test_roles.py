"""Role distribution and installer boundaries, using isolated target projects."""
import hashlib
import json
from pathlib import Path
import importlib.util
import json
import os
import re
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

    def install(self, harness="auto", command="init"):
        return subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "--harness", harness, command],
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
            legacy_path = self.target / WORKFLOW / "agents" / f"{name}.toml"
            legacy_data = tomllib.loads(legacy_path.read_text(encoding="utf-8"))
            self.assertEqual(legacy_data["name"], name)
            self.assertEqual(set(legacy_data), set(data))
            copilot = self.target / ".github/agents" / f"{name}.agent.md"
            self.assertTrue(copilot.is_file())
            adapter = copilot.read_text(encoding="utf-8")
            self.assertIn("\ntarget: vscode\n", adapter.split("---", 2)[1])
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
        inspected = self.install("copilot", "inspect")
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertIn(f"Installed roles (codex): {', '.join(sorted(ROLES))}", inspected.stdout)
        self.assertIn("Installed roles (copilot): none", inspected.stdout)

        other = self.folder / "copilot-only"
        other.mkdir()
        self.target = other
        copilot = self.install("copilot")
        self.assertEqual(copilot.returncode, 0, copilot.stderr)
        self.assertFalse((other / ".codex/config.toml").exists())
        inspected = self.install("codex", "inspect")
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertIn("Installed roles (codex): none", inspected.stdout)
        self.assertIn(f"Installed roles (copilot): {', '.join(sorted(ROLES))}", inspected.stdout)
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

    def test_copilot_only_rejects_incompatible_codex_references_before_writes(self):
        loader = importlib.util.spec_from_file_location("role_migration_tx", self.skill / "scripts/project_install.py")
        tx = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(tx)
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        old_shared = self.folder / "legacy-shared"
        old_role = old_shared / "agents/sdd-coder.toml"
        old_role.parent.mkdir(parents=True)
        old_role.write_bytes(b'name = "sdd-coder"\nmodel = "existing-model"\n')
        legacy = self.target / ".agents/skills/sdd-workflow"
        tx.create_workflow_link(legacy, old_shared)
        for anchor in (".agents/skills/sdd-workflow", ".agents/sdd-workflow"):
            link = self.target / anchor
            if anchor != ".agents/skills/sdd-workflow":
                tx.create_workflow_link(link, old_shared)
            absolute = str(link / "agents/sdd-coder.toml")
            references = [f"../{anchor}/agents/sdd-coder.toml", absolute]
            if os.name == "nt":
                references.append("\\\\?\\" + absolute)
            for reference in references:
                config.write_text(f'[agents.sdd-coder]\nconfig_file = {json.dumps(reference, ensure_ascii=False)}\n',
                                  encoding="utf-8")
                path = config.parent / reference
                self.assertTrue(path.samefile(old_role))
                before = self.snapshot()
                identity = tx.link_snapshot(link)
                for command in ("inspect", "init"):
                    with self.subTest(reference=reference, command=command):
                        result = self.install("copilot", command)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("--harness both", result.stderr)
                        self.assertEqual(self.snapshot(), before)
                        self.assertEqual(tx.link_snapshot(link), identity)
                        self.assertTrue(path.samefile(old_role))
                        if anchor == ".agents/skills/sdd-workflow":
                            self.assertFalse((self.target / ".agents/sdd-workflow").exists())

        result = self.install("both")
        self.assertEqual(result.returncode, 0, result.stderr)
        migrated = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]["sdd-coder"]["config_file"]
        self.assertTrue((config.parent / migrated).samefile(self.skill / "shared/roles/codex/sdd-coder.toml"))

    def test_copilot_only_preserves_absolute_codex_references_that_remain_available(self):
        self.assertEqual(self.install("codex").returncode, 0)
        config = self.target / ".codex/config.toml"
        reference = self.target / WORKFLOW / "roles/codex/sdd-coder.toml"
        original = (config.read_text(encoding="utf-8") + "\n[agents.project_alias]\n"
                    f"config_file = {json.dumps(str(reference), ensure_ascii=False)}\n").encode("utf-8")
        config.write_bytes(original)

        result = self.install("copilot")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(config.read_bytes(), original)
        self.assertTrue(reference.samefile(self.skill / "shared/roles/codex/sdd-coder.toml"))

    def test_codex_only_blocks_removal_of_a_copilot_role_dependency(self):
        loader = importlib.util.spec_from_file_location("copilot_migration_tx", self.skill / "scripts/project_install.py")
        tx = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(tx)
        legacy = self.target / tx.LEGACY_WORKFLOW_LINK
        tx.create_workflow_link(legacy, self.skill / "shared")
        role = self.target / ".github/agents/local.agent.md"
        role.parent.mkdir(parents=True)
        dependency = "roles/shared/sdd-coder.md"
        identity = tx.link_snapshot(legacy)
        for reference in (f"[Shared role](../../{tx.LEGACY_WORKFLOW_LINK}/{dependency})",
                          f"Load `{tx.LEGACY_WORKFLOW_LINK}/{dependency}` before acting."):
            role.write_text(f"---\nname: local\ntarget: vscode\n---\n{reference}\n", encoding="utf-8")
            before = self.snapshot()
            for command in ("inspect", "init"):
                with self.subTest(reference=reference, command=command):
                    result = self.install("codex", command)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("未选择 Copilot", result.stderr)
                    self.assertIn(role.name, result.stderr)
                    self.assertTrue((legacy / dependency).is_file())
                    self.assertEqual(tx.link_snapshot(legacy), identity)
                    self.assertEqual(self.snapshot(), before)

    def test_unmanaged_shared_pure_reference_can_be_migrated_without_losing_settings(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        alias = self.target / ".agents/skills/sdd-workflow/agents/sdd-coder.toml"
        config.write_text('model = "project-choice"\n[agents.sdd-coder]\n'
                          'config_file = "../.agents/skills/sdd-workflow/agents/sdd-coder.toml"\n'
                          f'[agents.project_alias]\nconfig_file = {json.dumps(str(alias), ensure_ascii=False)}\n',
                          encoding="utf-8")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = tomllib.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(parsed["model"], "project-choice")
        self.assertTrue((config.parent / parsed["agents"]["sdd-coder"]["config_file"]).samefile(
            self.skill / "shared/roles/codex/sdd-coder.toml"))
        self.assertEqual(parsed["agents"]["project_alias"]["config_file"], parsed["agents"]["sdd-coder"]["config_file"])

    def test_managed_codex_local_role_is_migrated_without_deleting_unmanaged_files(self):
        role = self.target / ".codex/agents/sdd-coder.toml"
        role.parent.mkdir(parents=True)
        role.write_bytes(b'name = "sdd-coder"\nmodel = "managed-choice"\n')
        (self.target / ".codex/config.toml").write_text(
            '# sdd-init roles:start\n[agents.sdd-coder]\n'
            'config_file = "agents/sdd-coder.toml"\n# sdd-init roles:end\n', encoding="utf-8")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(role.exists())
        self.assertEqual(self.install().returncode, 0)

    def test_unmanaged_alias_blocks_deleting_a_managed_codex_role_file(self):
        role = self.target / ".codex/agents/sdd-coder.toml"
        role.parent.mkdir(parents=True)
        role.write_bytes(b'name = "sdd-coder"\n')
        (self.target / ".codex/config.toml").write_text(
            '[agents.project_alias]\nconfig_file = "agents/./sdd-coder.toml"\n'
            '# sdd-init roles:start\n[agents.sdd-coder]\n'
            'config_file = "agents/sdd-coder.toml"\n# sdd-init roles:end\n', encoding="utf-8")
        before = self.snapshot()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_unmanaged_copilot_adapter_collision_is_rejected_without_changes(self):
        role = self.target / ".github/agents/sdd-coder.agent.md"
        role.parent.mkdir(parents=True)
        role.write_bytes(b"---\nname: sdd-coder\n---\nProject-owned instructions\n")
        before = self.snapshot()

        for command in ("inspect", "init"):
            with self.subTest(command=command):
                result = self.install(command=command)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("非受管", result.stderr)
                self.assertIn(".github/agents/sdd-coder.agent.md", result.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_clone_reconnects_with_older_copilot_adapters_and_no_local_state(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        original = self.target
        source = self.skill / "shared/roles/copilot"
        current_devops = (source / "sdd-devops.agent.md").read_bytes()
        current_coder = (source / "sdd-coder.agent.md").read_bytes()
        old_devops = (
            '---\nname: "sdd-devops"\n'
            'description: "负责仓库交付、CI/CD、制品发布、环境与流量运维、排障、备份恢复和退役。"\n'
            '---\nRead and follow `.agents/sdd-workflow/roles/shared/sdd-devops.md` before acting. '
            'That file is the authoritative role contract.\n'
        )
        adapters = original / ".github/agents"
        (adapters / "sdd-devops.agent.md").write_bytes(old_devops.encode("utf-8"))
        old_coder = re.sub(rb'description: [^\n]+', b'description: "Older coder description"',
                           current_coder.split(b"<!-- sdd-init managed role", 1)[0].replace(b"target: vscode\n", b""))
        digest = hashlib.sha256(old_coder).hexdigest()
        (adapters / "sdd-coder.agent.md").write_bytes(
            old_coder + f"<!-- sdd-init managed role sdd-coder sha256:{digest} -->\n".encode(),
        )
        clone = self.folder / "cloned-project"
        (original / ".gitattributes").write_bytes(b"*.agent.md text eol=crlf\n")
        git = ["git", "-C", str(original)]
        for args in (("init", "-q", "--template="), ("add", "."),
                     ("-c", "user.name=SDD test", "-c", "user.email=sdd@example.invalid",
                      "commit", "--no-gpg-sign", "-qm", "Project with the old adapters"),
                     ("clone", "-q", str(original), str(clone))):
            subprocess.run([*git, *args], check=True, capture_output=True)
        self.target = clone
        state = clone / ".sdd-init-state.json"
        self.assertFalse(state.exists())
        self.assertFalse((clone / WORKFLOW).exists())
        for name in ("sdd-devops", "sdd-coder"):
            role = clone / ".github/agents" / f"{name}.agent.md"
            original_bytes = role.read_bytes()
            self.assertIn(b"\r\n", original_bytes)
            role.write_bytes(original_bytes.replace(b"description:", b"description: edited", 1))
            before = self.snapshot()
            result = self.install()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("非受管", result.stderr)
            self.assertEqual(self.snapshot(), before)
            role.write_bytes(original_bytes)

        before = self.snapshot()
        inspected = self.install(command="inspect")
        self.assertEqual(inspected.returncode, 0, inspected.stderr)
        self.assertEqual(self.snapshot(), before)
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Configured harnesses: codex, copilot", result.stdout)
        self.assertTrue((clone / WORKFLOW).samefile(self.skill / "shared"))
        self.assertEqual((clone / ".github/agents/sdd-devops.agent.md").read_bytes(), current_devops)
        self.assertEqual((clone / ".github/agents/sdd-coder.agent.md").read_bytes(), current_coder)
        self.assertEqual(len(json.loads(state.read_bytes())["copilot_roles"]), len(ROLES))
        before = self.snapshot()
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_managed_copilot_ownership_survives_single_harness_refresh(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        state = self.target / ".sdd-init-state.json"
        owned = json.loads(state.read_bytes())["copilot_adapters"]
        self.assertIn(".github/agents/sdd-coder.agent.md", owned)
        role = self.target / ".github/agents/sdd-coder.agent.md"
        modified = b"Customized managed adapter\n"
        role.write_bytes(modified)

        result = self.install("codex")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(role.read_bytes(), modified)
        self.assertEqual(json.loads(state.read_bytes())["copilot_adapters"], owned)

        before = self.snapshot()
        result = self.install("copilot")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("归属校验失败", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_review_companion_resolves_from_the_contract_for_both_adapters(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        config = tomllib.loads((self.target / ".codex/config.toml").read_text(encoding="utf-8"))
        codex_path = self.target / ".codex" / config["agents"]["review-prompt"]["config_file"]
        codex = tomllib.loads(codex_path.read_text(encoding="utf-8"))["developer_instructions"]
        copilot = (self.target / ".github/agents/review-prompt.agent.md").read_text(encoding="utf-8")
        for adapter in (codex, copilot):
            with self.subTest(adapter=adapter):
                reference = re.search(r"Read and follow `?([^`\s]+\.md)", adapter)
                self.assertIsNotNone(reference)
                contract = self.target / reference[1]
                companion = re.search(r"\[审查规则与评价\]\(([^)]+)\)", contract.read_text(encoding="utf-8"))
                self.assertIsNotNone(companion)
                self.assertEqual((contract.parent / companion[1]).read_bytes(),
                                 (self.skill / "shared/roles/shared/review-prompt/prompt-review.md").read_bytes())

    def test_inspect_reports_default_dual_adapter_plan_without_writes(self):
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
             "--root", str(self.target), "inspect"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("codex=none", result.stdout)
        self.assertIn("copilot=none", result.stdout)
        self.assertIn("Harness adapters planned: codex, copilot", result.stdout)
        self.assertIn("Installed roles (codex): none", result.stdout)
        self.assertIn("Installed roles (copilot): none", result.stdout)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_inspect_reports_landed_roles_independent_of_metadata_or_selection(self):
        self.assertEqual(self.install().returncode, 0)
        (self.target / ".github/agents/sdd-devops.agent.md").unlink()
        config = self.target / ".codex/config.toml"
        config.write_bytes(config.read_bytes().replace(b"roles/codex/sdd-coder.toml", b"roles/codex/absent.toml"))
        before = self.snapshot()
        for harness in ("auto", "codex", "copilot"):
            with self.subTest(harness=harness):
                result = self.install(harness, "inspect")
                # Copilot-only cannot preserve the missing Codex reference, but still reports the disk state.
                self.assertEqual(result.returncode, 2 if harness == "copilot" else 0, result.stderr)
                codex = ", ".join(sorted(ROLES - {"sdd-coder"}))
                copilot = ", ".join(sorted(ROLES - {"sdd-devops"}))
                self.assertIn(f"Installed roles (codex): {codex}", result.stdout.splitlines())
                self.assertIn(f"Installed roles (copilot): {copilot}", result.stdout.splitlines())
                self.assertIn("Unresolved role files (codex): sdd-coder", result.stdout)
                self.assertEqual(self.snapshot(), before)

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
        self.assertIn("非受管 Copilot 角色冲突", result.stderr)
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
        self.assertIn("归属校验失败", result.stderr)
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

    def test_invalid_copilot_adapter_fails_before_changes(self):
        entry = self.skill / "shared/roles/copilot/sdd-coder.agent.md"
        original = entry.read_bytes()
        newline = b"\r\n" if b"\r\n" in original else b"\n"
        cases = (
            None,
            original.replace(b'name: "sdd-coder"', b'name: "other-role"'),
            original.replace(b"---" + newline, b"---" + newline + b"model: preset" + newline, 1),
            original.replace(b"---" + newline, b"---" + newline + b"reasoning-effort: high" + newline, 1),
            original.replace(b"target: vscode" + newline, b""),
            original.replace(b"target: vscode", b"target: github-copilot"),
            original.replace(b"target: vscode", b"target: vscode" + newline + b"target: github-copilot"),
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

    def test_same_name_unmanaged_role_is_rejected_and_unrelated_roles_survive(self):
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
        self.assertIn("非受管 Codex", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_same_name_unmanaged_registration_is_rejected_but_managed_upgrade_works(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = (b'model = "main-model"\n[agents.other]\nconfig_file = "other.toml"\n'
                    b'[agents.sdd-coder]\nconfig_file = "local.toml"\n')
        config.write_bytes(original)
        before = self.snapshot()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)
        config.write_bytes(original[:original.index(b'[agents.sdd-coder]')])
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

    def test_inline_same_name_unmanaged_registration_is_rejected(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        config.write_text('[agents]\nenabled = false\n'
                          'sdd-coder = { config_file = "project-role.toml" }\n'
                          'other = { config_file = "other.toml" }\n', encoding="utf-8")
        before = self.snapshot()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_dotted_and_quoted_unmanaged_registrations_are_rejected(self):
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
                before = self.snapshot()
                result = self.install()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.snapshot(), before)

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

    def test_root_inline_agents_table_preserves_unmanaged_conflict(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        original = ('agents = { "sdd-coder" = { config_file = "old.toml" }, '
                    'other = { description = "keep, {text}", config_file = "other.toml" } } # retain\n'
                    'model = "keep"\n')
        config.write_text(original, encoding="utf-8")
        before = self.snapshot()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.snapshot(), before)

    def test_multiline_unmanaged_role_value_is_preserved(self):
        config = self.target / ".codex/config.toml"
        config.parent.mkdir()
        for original in (
            '[agents]\nsdd-coder = [\n  "old",\n  "other",\n]\nenabled = false\n',
            'agents.sdd-coder = [\n  "old",\n]\nmodel = "keep"\n',
        ):
            with self.subTest(original=original):
                config.write_text(original, encoding="utf-8")
                before = self.snapshot()
                result = self.install()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.snapshot(), before)

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

    def test_project_conflicts_for_replacement_roles_are_preserved(self):
        for name in ("sdd-devops", "sdd-architect", "sdd-product-manager", "sdd-doc-consistency", "review-prompt"):
            with self.subTest(name=name):
                project = self.folder / f"conflict-{name}"
                local_roles = project / ".codex/agents"
                local_roles.mkdir(parents=True)
                config = project / ".codex/config.toml"
                config.write_text(f'[agents.{name}]\nconfig_file = "project-role.toml"\n', encoding="utf-8")
                local = local_roles / f"{name}.toml"
                local.write_text(f'name = "{name}"\n', encoding="utf-8")
                before = {p.relative_to(project): p.read_bytes() for p in project_files(project)}
                outcome = subprocess.run(
                    [sys.executable, "-B", "-X", "utf8", str(self.skill / "scripts/govern.py"),
                     "--root", str(project), "init"], capture_output=True, text=True, encoding="utf-8")
                self.assertNotEqual(outcome.returncode, 0)
                self.assertEqual({p.relative_to(project): p.read_bytes() for p in project_files(project)}, before)

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
