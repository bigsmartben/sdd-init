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

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.root), *args], text=True, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def bootstrap(self):
        self.run_cmd("init", "--name", "payment")

    def approved_contract(self):
        self.bootstrap()
        arch = self.root / "architecture/blueprint.md"
        arch.write_text("# 蓝图\n\n## 核心架构\n- ARC-001：订单对数据写入有所有权。\n", encoding="utf-8")
        spec = self.root / "specs/payment/spec.md"
        spec.write_text("# Payment\n\n## 目标\n完成订单模块重构\n\n## 架构依据\n- ARC-001\n\n## 验收条件\n\n| ID | 通过条件 | 证据类型 |\n| --- | --- | --- |\n| AC-001 | 相关测试通过 | pytest |\n", encoding="utf-8")

    def pass_both_gates(self):
        self.run_cmd("attest", "--name", "payment", "--gate", "test", "--result", "PASS", "--evidence", "全量 AC 复核已完成")
        self.run_cmd("attest", "--name", "payment", "--gate", "review", "--result", "PASS", "--evidence", "适用 ARC 与全局边界审查已完成")

    def test_baseline_distribution_and_existing_blueprint_preservation(self):
        from zipfile import ZipFile
        self.run_cmd("init")
        baseline = self.root / ".agents/sdd/references/observability-baseline.md"
        source = GOV.parent.parent / "references/observability-baseline.md"
        self.assertEqual(baseline.read_bytes(), source.read_bytes())
        blueprint = self.root / "architecture/blueprint.md"
        original = b"# Existing project architecture\n"
        blueprint.write_bytes(original)
        baseline.write_text("old baseline", encoding="utf-8")
        self.assertNotEqual(self.run_cmd("init", ok=False).returncode, 0)
        self.assertEqual(baseline.read_text(encoding="utf-8"), "old baseline")
        result = self.run_cmd("init", "--update-skills")
        self.assertEqual(blueprint.read_bytes(), original)
        self.assertEqual(baseline.read_bytes(), source.read_bytes())
        self.assertIn("BASELINE", result.stdout)
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
        self.assertEqual(list(self.root.iterdir()), [])

    def test_global_single_skill_and_local_five(self):
        from zipfile import ZipFile
        with ZipFile(GOV.parent.parent / "assets/repo-payload.zip") as archive:
            self.assertEqual(len([n for n in archive.namelist() if n.endswith("/SKILL.md")]), 5)
        self.run_cmd("init")
        self.assertEqual({p.parent.name for p in (self.root / ".agents/skills").glob("*/SKILL.md")},
                         {"sdd-doc", "sdd-imp", "sdd-review-loop", "sdd-test-loop", "sdd-commit"})
        self.assertFalse((self.root / ".agents/skills/sdd-init").exists())
        result = subprocess.run([sys.executable, str(self.root / ".agents/sdd/scripts/govern.py"),
                                 "--root", str(self.root), "inspect"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_installed_roles_and_user_owned_main_model(self):
        import tomllib
        self.run_cmd("init")
        expected = {}
        files = list((self.root / ".codex/agents").glob("*.toml"))
        self.assertEqual({p.stem for p in files}, set(expected))
        for file in files:
            data = tomllib.loads(file.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], file.stem)
            self.assertEqual(data["model"], expected[file.stem])
            self.assertNotIn("model_reasoning_effort", data)
        config = tomllib.loads((self.root / ".codex/config.toml").read_text(encoding="utf-8"))
        self.assertNotIn("model", config)
        self.assertNotIn("model_reasoning_effort", config)
        self.assertTrue(config["agents"]["enabled"])

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
        self.assertEqual(list(self.root.iterdir()), [])

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
        import tomllib
        codex = self.root / ".codex"
        codex.mkdir()
        config = codex / "config.toml"
        config.write_text('model = "other-model"\n[agents]\nenabled = false\n', encoding="utf-8")
        result=self.run_cmd("init",ok=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("--update-skills", result.stderr)
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.run_cmd("init","--update-skills")
        data=tomllib.loads(config.read_text(encoding="utf-8"))
        self.assertEqual(data["model"],"other-model")
        self.assertTrue(data["agents"]["enabled"])

    def test_config_with_existing_agent_subtable_merges_correctly(self):
        import tomllib
        codex=self.root / ".codex"
        codex.mkdir()
        cfg=codex / "config.toml"
        cfg.write_text('[agents.custom]\ndescription = "local agent"\nconfig_file = "agents/custom.toml"\n',encoding="utf-8")
        self.run_cmd("init")
        result=tomllib.loads(cfg.read_text(encoding="utf-8"))
        self.assertEqual(result["agents"]["custom"]["description"],"local agent")
        self.assertTrue(result["agents"]["enabled"])

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
        self.run_cmd("init", "--name", "payment")
        specs = list((self.root / "specs").glob("**/spec.md"))
        self.assertEqual(len(specs), 1)
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8").count("sdd-contract-governance:start"), 1)

    def test_existing_agents_preserved_and_merged_once(self):
        (self.root / "AGENTS.md").write_text("MY OWN RULES\n", encoding="utf-8")
        self.run_cmd("init")
        self.assertIn("MY OWN RULES\n", (self.root / "AGENTS.md").read_text(encoding="utf-8"))
        self.run_cmd("init")
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8").count("sdd-contract-governance:start"), 1)
        self.assertTrue((self.root / "AGENTS.md").read_text(encoding="utf-8").startswith("MY OWN RULES\n"))

    def test_init_writes_persistent_repo_guidance_without_extra_documents(self):
        self.run_cmd("init")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        import re
        targets = re.findall(r"\]\(([^)]+)\)", agents)
        self.assertIn(".agents/sdd/references/governance.md", targets)
        self.assertIn(".agents/sdd/references/delegation.md", targets)
        for target in targets:
            self.assertTrue((self.root / target.split("#")[0]).is_file(), target)
        governance = (self.root / ".agents/sdd/references/governance.md").read_text(encoding="utf-8")
        self.assertIn("architecture/blueprint.md", governance)
        self.assertTrue((self.root / ".agents/skills/sdd-imp/SKILL.md").is_file())
        self.assertFalse((self.root / "governance.md").exists())
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

    def test_missing_arch_reference_is_error(self):
        self.bootstrap()
        spec = self.root / "specs/payment/spec.md"
        data = spec.read_text(encoding="utf-8") + "\n- 特殊架构约束：ARC-999\n"
        spec.write_text(data, encoding="utf-8")
        result = self.run_cmd("check", ok=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ARC-999", result.stdout)

    def test_start_is_non_destructive_for_same_iteration(self):
        self.bootstrap()
        self.run_cmd("start", "--name", "payment", "--iteration", "phase-a")
        status = self.root / "specs/payment/status.md"
        status.write_text(status.read_text(encoding="utf-8").replace("- 无", "- 本次特定阻塞"), encoding="utf-8")
        self.run_cmd("start", "--name", "payment", "--iteration", "phase-a")
        self.assertIn("本次特定阻塞", status.read_text(encoding="utf-8"))
        result = self.run_cmd("start", "--name", "payment", "--iteration", "phase-b", ok=False)
        self.assertNotEqual(result.returncode, 0)

    def test_git_snapshot_freshness_and_finish(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        (self.root / "main.py").write_text("print('ok')\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "init")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "pytest test_payment.py: 12 passed")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "dependency audit: passed")
        self.pass_both_gates()
        self.run_cmd("check", "--strict")
        (self.root / "main.py").write_text("print('changed')\n", encoding="utf-8")
        result = self.run_cmd("check", "--strict", ok=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("STALE", result.stdout)
        # User has actually re-validated the altered code; record their new evidence.
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "pytest test_payment.py: 12 passed after change")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "dependency audit: passed after change")
        self.pass_both_gates()
        # sdd-imp finishes WITHOUT committing; explicit sdd-commit submits exactly once.
        self.run_cmd("finish", "--name", "payment")
        self.assertIn("- State: COMPLETED", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))
        self.assertEqual(subprocess.run(["git", "-C", str(self.root), "rev-list", "--count", "HEAD"], capture_output=True, text=True, encoding="utf-8").stdout.strip(), "1")
        self.assertEqual(subprocess.run(["git", "-C", str(self.root), "diff", "--cached", "--name-only"], capture_output=True, text=True, encoding="utf-8").stdout.strip(), "")
        self.run_cmd("commit", "--name", "payment", "--include", "main.py")
        self.assertEqual(subprocess.run(["git", "-C", str(self.root), "rev-list", "--count", "HEAD"], capture_output=True, text=True, encoding="utf-8").stdout.strip(), "2")
        self.run_cmd("check", "--strict")  # commit does not stale evidence
        again = self.run_cmd("commit", "--name", "payment", "--include", "main.py", ok=False)
        self.assertIn("重复提交", again.stderr)
        self.assertNotEqual(again.returncode, 0)
        self.run_cmd("start", "--name", "payment", "--iteration", "r2")
        self.assertIn("UNVERIFIED", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))

    def test_speckit_inspired_spec_has_single_verifiable_acceptance_contract(self):
        self.bootstrap()
        spec = (self.root / "specs/payment/spec.md").read_text(encoding="utf-8")
        status = (self.root / "specs/payment/status.md").read_text(encoding="utf-8")
        self.assertIn("Given：前提", spec)
        self.assertIn("When：触发", spec)
        self.assertIn("Then：可观察结果", spec)
        self.assertIn("边界条件与失败场景", spec)
        self.assertIn("FR-001", spec)
        self.assertIn("SC-001", spec)
        self.assertEqual(sum(1 for x in spec.splitlines() if x.startswith("| AC-001 |")), 1)
        self.assertIn("| AC-001 | UNVERIFIED | - | - |", status)
        self.assertNotIn("| SC-001 |", status)
        self.assertFalse((self.root / "specs/payment/plan.md").exists())
        self.assertFalse((self.root / "specs/payment/tasks.md").exists())

    def test_embedded_spec_template_limits_implementation_choices(self):
        self.bootstrap()
        data = (self.root / "specs/payment/spec.md").read_text(encoding="utf-8")
        self.assertIn("不固化具体技术方案", data)
        self.assertIn("只固化需求契约", data)
        self.assertIn("设计模式", data)

    def test_finish_commits_only_explicit_scope(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        (self.root / "impl.py").write_text("print(1)\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        (self.root / "impl.py").write_text("print(2)\n", encoding="utf-8")
        self.run_cmd("start", "--name", "payment", "--iteration", "refactor-a")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "pytest passed")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "architecture audit passed")
        self.pass_both_gates()
        self.run_cmd("finish", "--name", "payment")
        self.run_cmd("commit", "--name", "payment", "--include", "impl.py")
        (self.root / "unrelated.txt").write_text("not in iteration\n", encoding="utf-8")
        committed = subprocess.run(["git", "-C", str(self.root), "show", "--pretty=format:", "--name-only", "HEAD"], capture_output=True, text=True, encoding="utf-8").stdout
        self.assertIn("impl.py", committed)
        self.assertIn("specs/payment/status.md", committed)
        self.assertNotIn("unrelated.txt", committed)
        self.assertTrue((self.root / "unrelated.txt").exists())
        self.assertNotEqual(self.run_cmd("check", "--name", "payment", "--strict", ok=False).returncode, 0)  # unrelated code makes old evidence stale

    def test_finish_rejects_staged_unrelated_and_does_not_claim_complete(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "pytest passed")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "arch passed")
        self.run_cmd("finish", "--name", "payment")
        (self.root / "personal.txt").write_text("do not stage me\n", encoding="utf-8")
        self.git("add", "personal.txt")
        result = self.run_cmd("commit", "--name", "payment", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMPLETED", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))
        self.assertEqual(subprocess.run(["git", "-C", str(self.root), "rev-list", "--count", "HEAD"], capture_output=True, text=True, encoding="utf-8").stdout.strip(), "1")

    def test_scope_path_rejects_traversal(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "pytest passed")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "arch passed")
        self.run_cmd("finish", "--name", "payment")
        result = self.run_cmd("commit", "--name", "payment", "--include", "../elsewhere", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COMPLETED", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))

    def test_finish_rejects_unverified(self):
        self.approved_contract()
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        result = self.run_cmd("finish", "--name", "payment", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("IN_PROGRESS", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))

    def test_check_accepts_multiple_named_specs(self):
        self.bootstrap()
        self.run_cmd("init", "--name", "order")
        both = self.run_cmd("check", "--name", "payment", "--name", "order")
        self.assertIn("Checked 2 capability(s)", both.stdout)
        self.run_cmd("check", "--name", "payment")
        # An error in one selected Spec should fail the batch, not a different single Spec.
        order = self.root / "specs/order/spec.md"
        order.write_text(order.read_text(encoding="utf-8") + "\n- ARC-999\n", encoding="utf-8")
        self.run_cmd("check", "--name", "payment")
        bad = self.run_cmd("check", "--name", "payment", "--name", "order", ok=False)
        self.assertIn("ARC-999", bad.stdout)
        self.assertIn("Checked 2 capability(s)", bad.stdout)

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

    def test_post_implementation_user_driven_audit_is_allowed(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.run_cmd("start", "--name", "payment", "--iteration", "i1")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "project tests passed")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "basic architecture check passed")
        self.run_cmd("finish", "--name", "payment")
        # No implicit Gate approval, even after implementation is marked complete.
        self.assertNotEqual(self.run_cmd("check", "--name", "payment", "--strict", "--require-gates", ok=False).returncode, 0)
        self.run_cmd("attest", "--name", "payment", "--gate", "review", "--result", "PASS", "--evidence", "explicit external audit approved")
        self.run_cmd("attest", "--name", "payment", "--gate", "test", "--result", "PASS", "--evidence", "explicit end-to-end scenarios passed")
        self.run_cmd("check", "--name", "payment", "--strict", "--require-gates")


    def test_installed_reference_links_resolve(self):
        import re
        self.run_cmd("init")
        for path in (self.root / ".agents").rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#")[0]).is_file(), (path, link))

    def test_commit_rejects_early_and_stale_without_changing_status(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        (self.root / "impl.py").write_text("print('a')\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        self.assertNotEqual(self.run_cmd("commit", "--name", "payment", ok=False).returncode, 0)
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "test")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "arch")
        self.run_cmd("finish", "--name", "payment")
        (self.root / "impl.py").write_text("print('b')\n", encoding="utf-8")
        bad = self.run_cmd("commit", "--name", "payment", "--include", "impl.py", ok=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("快照", bad.stdout + bad.stderr)
        self.assertIn("COMPLETED", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))

    def test_init_backfills_status_for_existing_spec_without_overwrite(self):
        self.run_cmd("init", "--name", "payment")
        status = self.root / "specs/payment/status.md"
        status.unlink()
        spec = self.root / "specs/payment/spec.md"
        spec.write_text("# Payment\n\n| ID | Given | When | Then |\n| --- | --- | --- | --- |\n| AC-007 | a | b | c |\n", encoding="utf-8")
        self.run_cmd("init")
        self.assertIn("| AC-007 | UNVERIFIED | - | - |", status.read_text(encoding="utf-8"))
        status.write_text("manual checkpoint", encoding="utf-8")
        self.run_cmd("init", "--name", "payment")
        self.assertEqual(status.read_text(encoding="utf-8"), "manual checkpoint")

    def test_init_creates_multiple_capability_triplets(self):
        self.run_cmd("init", "--name", "payment", "--name", "order")
        for name in ("payment", "order"):
            self.assertTrue((self.root / f"specs/{name}/spec.md").exists())
            self.assertTrue((self.root / f"specs/{name}/status.md").exists())

    def test_all_workflows_explicit(self):
        self.run_cmd("init")
        import yaml
        for name in ("sdd-doc", "sdd-imp", "sdd-review-loop", "sdd-test-loop", "sdd-commit"):
            policy = yaml.safe_load((self.root / f".agents/skills/{name}/agents/openai.yaml").read_text(encoding="utf-8"))
            self.assertEqual(policy["policy"]["allow_implicit_invocation"], False)
        self.assertFalse((self.root / ".agents/skills/sdd-spec").exists())
        self.assertFalse((self.root / ".agents/skills/sdd-arch").exists())

    def test_inspect_read_only(self):
        self.run_cmd("inspect")
        self.assertEqual(list(self.root.iterdir()), [])


    def test_architecture_gate_requires_independent_evidence(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "contract tests passed")
        check = self.run_cmd("check", "--strict", ok=False)
        self.assertIn("ARC-001", check.stdout)
        self.assertNotEqual(self.run_cmd("finish", "--name", "payment", ok=False).returncode, 0)
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "dependency boundary checked")
        # A user-driven review/test loop is NOT mandatory for sdd-imp completion.
        self.run_cmd("finish", "--name", "payment")
        status = (self.root / "specs/payment/status.md").read_text(encoding="utf-8")
        self.assertIn("- Review Gate: UNVERIFIED", status)
        self.assertIn("- Test Gate: UNVERIFIED", status)
        self.assertNotEqual(self.run_cmd("check", "--name", "payment", "--require-gates", "--strict", ok=False).returncode, 0)

    def test_unknown_arc_cannot_be_passed(self):
        self.approved_contract()
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        result = self.run_cmd("record", "--name", "payment", "--arc", "ARC-999", "--result", "PASS", "--evidence", "unknown", ok=False)
        self.assertNotEqual(result.returncode, 0)

    def test_gates_require_underlying_ac_arc_evidence(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        attempt = self.run_cmd("attest", "--name", "payment", "--gate", "review", "--result", "PASS", "--evidence", "reviewed", ok=False)
        self.assertNotEqual(attempt.returncode, 0)
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "tested")
        self.run_cmd("attest", "--name", "payment", "--gate", "test", "--result", "PASS", "--evidence", "test coverage reviewed")
        self.assertNotEqual(self.run_cmd("finish", "--name", "payment", ok=False).returncode, 0)

    def test_finish_rejects_unrelated_dirty_even_if_unstaged(self):
        self.approved_contract()
        self.git("init", "-q")
        self.git("config", "user.email", "dev@example.test")
        self.git("config", "user.name", "Test")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        (self.root / "unrelated.txt").write_text("unrelated\n", encoding="utf-8")
        self.run_cmd("start", "--name", "payment", "--iteration", "r1")
        self.run_cmd("record", "--name", "payment", "--ac", "AC-001", "--result", "PASS", "--evidence", "tests passed")
        self.run_cmd("record", "--name", "payment", "--arc", "ARC-001", "--result", "PASS", "--evidence", "arch passed")
        self.pass_both_gates()
        self.run_cmd("finish", "--name", "payment")
        result = self.run_cmd("commit", "--name", "payment", ok=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("未批准范围", result.stderr)
        self.assertTrue((self.root / "unrelated.txt").exists())
        self.assertIn("COMPLETED", (self.root / "specs/payment/status.md").read_text(encoding="utf-8"))

    def test_architecture_rule_catalog_is_not_project_authority(self):
        self.bootstrap()
        blueprint = (self.root / "architecture/blueprint.md").read_text(encoding="utf-8")
        self.assertNotIn("ARC-OBS-001", blueprint)
        catalog = (GOV.parent.parent / "assets/architecture-rule-catalog.md").read_text(encoding="utf-8")
        self.assertIn("observability-baseline.md", catalog)


if __name__ == "__main__":
    unittest.main(verbosity=2)
