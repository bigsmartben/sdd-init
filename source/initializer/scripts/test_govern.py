#!/usr/bin/env python3
"""Portable unittest suite. Run: python scripts/test_govern.py"""
import subprocess
import os
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import sys
import tempfile
from pathlib import Path
import unittest

GOV = Path(__file__).resolve().with_name("govern.py")


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()

    def run_cmd(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(GOV), "--root", str(self.root), *args],
                                text=True, capture_output=True, encoding="utf-8")
        if ok and result.returncode != 0:
            self.fail(f"return={result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}")
        return result


    def legacy_fixture(self, name="payment"):
        self.run_cmd("init")
        folder = self.root / "specs" / name
        folder.mkdir(parents=True, exist_ok=True)
        arch = self.root / "architecture/blueprint.md"
        arch.parent.mkdir(exist_ok=True)
        if not arch.exists():
            arch.write_bytes(b"# Historical architecture\n")
        for filename in ("spec.md", "status.md"):
            path = folder / filename
            if not path.exists():
                path.write_bytes(b"# Historical record\n")

    def bootstrap(self):
        self.legacy_fixture()


    def test_baseline_distribution_and_existing_blueprint_preservation(self):
        from zipfile import ZipFile
        self.run_cmd("init")
        baseline = self.root / ".agents/sdd/references/observability-baseline.md"
        source = GOV.parent.parent / "references/observability-baseline.md"
        self.assertEqual(baseline.read_bytes(), source.read_bytes())
        blueprint = self.root / "architecture/blueprint.md"
        original = b"# Existing project architecture\n"
        blueprint.parent.mkdir(exist_ok=True)
        blueprint.write_bytes(original)
        baseline.write_text("old baseline", encoding="utf-8")
        self.assertNotEqual(self.run_cmd("init", ok=False).returncode, 0)
        self.assertEqual(baseline.read_text(encoding="utf-8"), "old baseline")
        result = self.run_cmd("init", "--update-skills")
        self.assertEqual(blueprint.read_bytes(), original)
        self.assertEqual(baseline.read_bytes(), source.read_bytes())
        self.assertEqual(result.returncode, 0)
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.run_cmd("init")
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_observability_payload_conflict_and_explicit_upgrade(self):
        self.run_cmd("init")
        resource = self.root / ".agents/sdd/assets/observability/check.py"
        schema = self.root / ".agents/sdd/assets/observability/event-1.0.0.schema.json"
        source = GOV.parent.parent / "assets/observability"
        self.assertEqual(resource.read_bytes(), (source / "check.py").read_bytes())
        self.assertEqual(schema.read_bytes(), (source / schema.name).read_bytes())
        resource.write_text("user customization", encoding="utf-8")
        self.assertNotEqual(self.run_cmd("init", ok=False).returncode, 0)
        self.assertEqual(resource.read_text(encoding="utf-8"), "user customization")
        self.run_cmd("init", "--update-skills")
        self.assertEqual(resource.read_bytes(), (source / "check.py").read_bytes())

    def test_missing_baseline_rejected_before_install(self):
        import importlib.util
        from zipfile import ZipFile
        loader = importlib.util.spec_from_file_location("baseline_govern", GOV)
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        broken = Path(self.tmp.name) / "missing-baseline.zip"
        with ZipFile(module.PROJECT_PAYLOAD) as source, ZipFile(broken, "w") as target:
            for name in source.namelist():
                if name != ".agents/sdd/references/observability-baseline.md":
                    target.writestr(name, source.read(name))
        module.PROJECT_PAYLOAD = broken
        with self.assertRaises(ValueError):
            module.cmd_init(self.root, module.build_parser().parse_args(["init"]))
        self.assertEqual([p for p in self.root.iterdir() if p.name != ".sdd-init.lock"], [])

    def test_global_single_skill_and_local_six(self):
        from zipfile import ZipFile
        with ZipFile(GOV.parent.parent / "assets/repo-payload.zip") as archive:
            self.assertEqual(len([n for n in archive.namelist() if n.endswith("/SKILL.md")]), 6)
        self.run_cmd("init")
        self.assertEqual({p.parent.name for p in (self.root / ".agents/skills").glob("*/SKILL.md")},
                         {"sdd-doc", "sdd-imp", "sdd-test-loop", "sdd-review-loop", "sdd-commit", "sdd-deploy"})
        self.assertFalse((self.root / ".agents/skills/sdd-init").exists())
        result = subprocess.run([sys.executable, str(self.root / ".agents/sdd/scripts/govern.py"),
                                 "--root", str(self.root), "inspect"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installed_roles_and_user_owned_main_model(self):
        self.run_cmd("init")
        import tomllib
        roles = list((self.root / ".codex/agents").glob("*.toml"))
        expected_models = {
            "sdd-designer": "gpt-6-astra",
            "sdd-coder": "gpt-6.1-sol",
            "sdd-documenter": "gpt-6.1-terra",
            "sdd-validator": "gpt-6.1-terra",
            "sdd-delivery": "gpt-6.1-terra",
        }
        self.assertEqual({path.stem for path in roles}, set(expected_models))
        for path in roles:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], path.stem)
            self.assertEqual(set(data), {"name", "description", "model", "developer_instructions"})
            self.assertEqual(data["model"], expected_models[path.stem])
        self.assertFalse((self.root / ".codex/config.toml").exists())
        self.assertFalse((self.root / "architecture").exists())
        self.assertFalse((self.root / "specs").exists())

    def test_payload_missing_required_reference_fails_before_writing(self):
        import importlib.util
        from zipfile import ZipFile
        loader = importlib.util.spec_from_file_location("govern_under_test", GOV)
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        broken = Path(self.tmp.name) / "broken.zip"
        with ZipFile(module.PROJECT_PAYLOAD) as source, ZipFile(broken, "w") as out:
            for name in source.namelist():
                if name != ".agents/sdd/references/delegation.md":
                    out.writestr(name, source.read(name))
        module.PROJECT_PAYLOAD = broken
        with self.assertRaises(ValueError):
            module.cmd_init(self.root, module.build_parser().parse_args(["init"]))
        self.assertEqual([p for p in self.root.iterdir() if p.name != ".sdd-init.lock"], [])

    def test_runtime_claims_do_not_leak_into_repo_guidance(self):
        self.run_cmd("init")
        guidance = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("线程标识", guidance)
        self.assertNotIn("运行时未核验", guidance)
        self.assertFalse((self.root / ".codex/agent-routing.md").exists())

    def test_merges_existing_config_and_preserves_unrelated_keys(self):
        import tomllib
        codex = self.root / ".codex"
        codex.mkdir()
        config = codex / "config.toml"
        original = '# project metadata\n[mcp_servers.custom]\nurl = "https://example.invalid/mcp"\n'
        config.write_text(original, encoding="utf-8")
        self.run_cmd("init")
        after = config.read_text(encoding="utf-8")
        self.assertIn(original, after)
        parsed = tomllib.loads(after)
        self.assertEqual(parsed["mcp_servers"]["custom"]["url"], "https://example.invalid/mcp")
        self.assertNotIn("model", parsed)
        self.assertNotIn("model_reasoning_effort", parsed)
        self.run_cmd("init")
        self.assertEqual(after, config.read_text(encoding="utf-8"))

    def test_conflicting_codex_config_requires_explicit_upgrade(self):
        config = self.root / ".codex/config.toml"
        config.parent.mkdir()
        original = b'model = "other-model"\n[agents]\nenabled = false\n'
        config.write_bytes(original)
        for args in ((), ("--update-skills",)):
            self.run_cmd("init", *args)
            self.assertEqual(config.read_bytes(), original)

    def test_config_with_existing_agent_subtable_merges_correctly(self):
        import tomllib
        codex=self.root / ".codex"
        codex.mkdir()
        cfg=codex / "config.toml"
        cfg.write_text('[agents.custom]\ndescription = "local agent"\nconfig_file = "agents/custom.toml"\n',encoding="utf-8")
        self.run_cmd("init")
        result=tomllib.loads(cfg.read_text(encoding="utf-8"))
        self.assertEqual(result["agents"]["custom"]["description"],"local agent")
        self.assertNotIn("enabled", result["agents"])

    def test_init_protects_local_customizations_unless_approved(self):
        self.run_cmd("init")
        path = self.root / ".agents/skills/sdd-doc/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n# local customized\n", encoding="utf-8")
        denied = self.run_cmd("init", ok=False)
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("--update-skills", denied.stderr)
        self.assertIn("local customized", path.read_text(encoding="utf-8"))
        self.run_cmd("init", "--update-skills")
        self.assertNotIn("local customized", path.read_text(encoding="utf-8"))

    def test_init_idempotent_and_add_singleton(self):
        self.bootstrap()
        self.legacy_fixture()
        specs = list((self.root / "specs").glob("**/spec.md"))
        self.assertEqual(len(specs), 1)
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8").count("sdd-contract-governance:start"), 1)

    def test_existing_agents_preserved_and_merged_once(self):
        (self.root / "AGENTS.md").write_text("MY OWN RULES\n", encoding="utf-8")
        self.run_cmd("init")
        self.assertIn("MY OWN RULES\n", (self.root / "AGENTS.md").read_text(encoding="utf-8"))
        self.run_cmd("init")
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8").count("sdd-contract-governance:start"), 1)
        self.assertTrue((self.root / "AGENTS.md").read_text(encoding="utf-8").startswith("<!-- agent-communication:start -->"))

    def test_init_writes_persistent_repo_guidance_without_extra_documents(self):
        self.run_cmd("init")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        import re
        targets = re.findall(r"\]\(([^)]+)\)", agents)
        self.assertIn(".agents/sdd/references/sdd-repository-governance.md", targets)
        self.assertIn(".agents/sdd/references/delegation.md", targets)
        for target in targets:
            self.assertTrue((self.root / target.split("#")[0]).is_file(), target)
        governance = (self.root / ".agents/sdd/references/sdd-repository-governance.md").read_text(encoding="utf-8")
        self.assertIn("docs/blueprint.md", governance)
        self.assertTrue((self.root / ".agents/skills/sdd-imp/SKILL.md").is_file())
        self.assertFalse((self.root / "sdd-repository-governance.md").exists())
        self.assertFalse((self.root / "specs").exists())

    def test_init_rejects_shadowed_root_agents_override(self):
        (self.root / "AGENTS.override.md").write_text("OVERRIDE\n", encoding="utf-8")
        result = self.run_cmd("init", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AGENTS.override.md", result.stderr)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_reject_invalid_slug(self):
        self.run_cmd("init")
        result = self.run_cmd("init", "--name", "../../evil", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root.parent / "evil").exists())


    def test_speckit_inspired_spec_has_single_verifiable_acceptance_contract(self):
        self.bootstrap()
        spec = (GOV.parent.parent / "assets/spec_template.md").read_text(encoding="utf-8")
        status = (GOV.parent.parent / "assets/status_template.md").read_text(encoding="utf-8")
        self.assertIn("Given：前提", spec)
        self.assertIn("When：触发", spec)
        self.assertIn("Then：结果与通过标准", spec)
        self.assertIn("边界、失败、并发、取消与恢复", spec)
        self.assertIn("FR-001", spec)
        self.assertNotIn("| SC-001 |", spec)  # No competing acceptance table.
        self.assertEqual(sum(1 for x in spec.splitlines() if x.startswith("| AC-001 |")), 1)
        self.assertIn("{ROWS}", status)
        self.assertNotIn("| SC-001 |", status)
        self.assertFalse((self.root / "specs/payment/plan.md").exists())
        self.assertFalse((self.root / "specs/payment/tasks.md").exists())

    def test_embedded_spec_template_limits_implementation_choices(self):
        self.bootstrap()
        data = (GOV.parent.parent / "assets/spec_template.md").read_text(encoding="utf-8")
        self.assertIn("不固化具体技术方案", data)
        self.assertIn("只固化需求契约", data)
        self.assertIn("设计模式", data)


    def test_user_main_model_and_effort_survive_all_init_modes(self):
        import tomllib
        config = self.root / ".codex/config.toml"
        config.parent.mkdir()
        config.write_text('model = "my-discussion-model"\nmodel_reasoning_effort = "xhigh"\n', encoding="utf-8")
        for args in [(), ("--update-skills",)]:
            self.run_cmd("init", *args)
            data = tomllib.loads(config.read_text(encoding="utf-8"))
            self.assertEqual(data["model"], "my-discussion-model")
            self.assertEqual(data["model_reasoning_effort"], "xhigh")


    def test_installed_reference_links_resolve(self):
        import re
        self.run_cmd("init")
        for path in (self.root / ".agents").rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#")[0]).is_file(), (path, link))


    def test_init_preserves_existing_spec_without_backfilling_status(self):
        self.legacy_fixture()
        status = self.root / "specs/payment/status.md"
        status.unlink()
        spec = self.root / "specs/payment/spec.md"
        before = spec.read_bytes()
        self.run_cmd("init")
        self.assertFalse(status.exists())
        self.assertEqual(spec.read_bytes(), before)
        status.write_text("manual checkpoint", encoding="utf-8")
        self.run_cmd("init", "--update-skills")
        self.assertEqual(status.read_text(encoding="utf-8"), "manual checkpoint")

    def test_init_rejects_legacy_entity_creation_options(self):
        result = self.run_cmd("init", "--name", "payment", "--name", "order", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_workflows_allow_natural_language_selection(self):
        self.run_cmd("init")
        for name in ("sdd-doc", "sdd-imp", "sdd-test-loop", "sdd-review-loop", "sdd-commit", "sdd-deploy"):
            metadata = (self.root / f".agents/skills/{name}/agents/openai.yaml").read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: true", metadata)
        self.assertIn("allow_implicit_invocation: true", (GOV.parent.parent / "agents/openai.yaml").read_text(encoding="utf-8"))
        for name in ("sdd-accept",):
            self.assertFalse((self.root / ".agents/skills" / name).exists())

    def test_inspect_read_only(self):
        self.run_cmd("inspect")
        self.assertEqual(list(self.root.iterdir()), [])


    def test_architecture_rule_catalog_is_not_project_authority(self):
        self.bootstrap()
        blueprint = (self.root / "architecture/blueprint.md").read_text(encoding="utf-8")
        self.assertNotIn("ARC-OBS-001", blueprint)
        catalog = (GOV.parent.parent / "assets/architecture-rule-catalog.md").read_text(encoding="utf-8")
        self.assertIn("observability-baseline.md", catalog)


if __name__ == "__main__":
    unittest.main(verbosity=2)
