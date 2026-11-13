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
WORKFLOW = ".agents/skills/sdd-workflow"
SHARED = GOV.parent.parent / "shared"


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


    def test_shared_observability_resources_and_project_preservation(self):
        self.run_cmd("init")
        resource = self.root / WORKFLOW / "sdd/assets/observability/check.py"
        self.assertTrue(resource.samefile(SHARED / "sdd/assets/observability/check.py"))
        blueprint = self.root / "architecture/blueprint.md"
        blueprint.parent.mkdir()
        original = b"# Existing project architecture\\n"
        blueprint.write_bytes(original)
        self.run_cmd("init")
        self.assertEqual(blueprint.read_bytes(), original)

    def test_global_entry_and_project_skills(self):
        self.assertFalse((GOV.parent.parent / "assets/repo-payload.zip").exists())
        self.run_cmd("init")
        self.assertEqual({p.parent.name for p in (self.root / WORKFLOW / "skills").glob("*/SKILL.md")},
                         {"sdd-doc", "sdd-imp", "sdd-test-loop", "sdd-review-code",
                          "sdd-review-prompt", "sdd-commit", "sdd-deploy"})
        self.assertFalse((self.root / ".agents/skills/sdd-init").exists())
        result = subprocess.run([sys.executable, str(self.root / WORKFLOW / "sdd/scripts/govern.py"),
                                 "--root", str(self.root), "inspect"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installed_role_references_and_default_models(self):
        self.run_cmd("init")
        import tomllib
        config = self.root / ".codex/config.toml"
        roles = tomllib.loads(config.read_text(encoding="utf-8"))["agents"]
        expected_models = {
            "sdd-designer": "gpt-6-astra",
            "sdd-coder": "gpt-6.1-sol",
            "sdd-documenter": "gpt-6.1-terra",
            "sdd-validator": "gpt-6.1-terra",
            "sdd-delivery": "gpt-6.1-terra",
        }
        self.assertEqual(set(roles), set(expected_models))
        for name, model in expected_models.items():
            role = config.parent / roles[name]["config_file"]
            self.assertTrue(role.samefile(SHARED / "agents" / f"{name}.toml"))
            self.assertEqual(tomllib.loads(role.read_text(encoding="utf-8"))["model"], model)
        self.assertFalse((self.root / ".codex/agents").exists())
        self.assertFalse((self.root / "architecture").exists())
        self.assertFalse((self.root / "specs").exists())

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

    def test_init_preserves_project_agent_settings(self):
        config = self.root / ".codex/config.toml"
        config.parent.mkdir()
        original = b'model = "other-model"\n[agents]\nenabled = false\n'
        config.write_bytes(original)
        self.run_cmd("init")
        self.assertTrue(config.read_bytes().startswith(original))

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

    def test_init_protects_same_name_project_skill(self):
        path = self.root / ".agents/skills/sdd-doc/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("local customization", encoding="utf-8")
        denied = self.run_cmd("init", ok=False)
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn("sdd-doc", denied.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "local customization")
        self.assertFalse((self.root / WORKFLOW).exists())

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
        self.assertIn(f"{WORKFLOW}/sdd/references/sdd-repository-governance.md", targets)
        self.assertIn(f"{WORKFLOW}/sdd/references/delegation.md", targets)
        for target in targets:
            self.assertTrue((self.root / target.split("#")[0]).is_file(), target)
        governance = (self.root / f"{WORKFLOW}/sdd/references/sdd-repository-governance.md").read_text(encoding="utf-8")
        self.assertIn("docs/blueprint.md", governance)
        self.assertTrue((self.root / f"{WORKFLOW}/skills/sdd-imp/SKILL.md").is_file())
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
        spec = (SHARED / "sdd/assets/spec_template.md").read_text(encoding="utf-8")
        status = (SHARED / "sdd/assets/status_template.md").read_text(encoding="utf-8")
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
        data = (SHARED / "sdd/assets/spec_template.md").read_text(encoding="utf-8")
        self.assertIn("不固化具体技术方案", data)
        self.assertIn("只固化需求契约", data)
        self.assertIn("设计模式", data)


    def test_user_main_model_and_effort_survive_init(self):
        import tomllib
        config = self.root / ".codex/config.toml"
        config.parent.mkdir()
        config.write_text('model = "my-discussion-model"\nmodel_reasoning_effort = "xhigh"\n', encoding="utf-8")
        self.run_cmd("init")
        data = tomllib.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(data["model"], "my-discussion-model")
        self.assertEqual(data["model_reasoning_effort"], "xhigh")


    def test_installed_reference_links_resolve(self):
        import re
        self.run_cmd("init")
        for path in (self.root / WORKFLOW).rglob("*.md"):
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
        self.run_cmd("init")
        self.assertEqual(status.read_text(encoding="utf-8"), "manual checkpoint")

    def test_init_rejects_legacy_entity_creation_options(self):
        result = self.run_cmd("init", "--name", "payment", "--name", "order", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_workflows_allow_natural_language_selection(self):
        self.run_cmd("init")
        for name in ("sdd-doc", "sdd-imp", "sdd-test-loop", "sdd-review-code",
                     "sdd-review-prompt", "sdd-commit", "sdd-deploy"):
            metadata = (self.root / WORKFLOW / f"skills/{name}/agents/openai.yaml").read_text(encoding="utf-8")
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
        catalog = (SHARED / "sdd/assets/architecture-rule-catalog.md").read_text(encoding="utf-8")
        self.assertIn("observability-baseline.md", catalog)


if __name__ == "__main__":
    unittest.main(verbosity=2)
