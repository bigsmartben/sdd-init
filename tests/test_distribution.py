import importlib.util
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import re
import sys
import tempfile
import tomllib
from types import SimpleNamespace
import unittest
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from sdd_init.cli import apply
from sdd_init import repository

spec = importlib.util.spec_from_file_location("builder", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DistributionTests(unittest.TestCase):
    def test_legacy_task_label_resolves_to_shipped_role(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = builder.build(Path(directory) / "bundle")
            main = (bundle / "assets" / repository.MAIN_RULES).read_text("utf-8")
            self.assertRegex(main, r"(?m)^- \*\*implementer\*\*[^\n]*\[Coder\]")
            roles = bundle / "assets/.codex/agents"
            self.assertFalse((roles / "coder.toml").exists())
            role = tomllib.loads((roles / "implementer.toml").read_text("utf-8"))
            self.assertEqual(role["name"], "implementer")

    def test_published_main_routes_by_role_and_lists_scene_aliases(self):
        expected_terms = {
            "architect": ("arch／架构", "blueprint／蓝图", "整体结构、组件职责、关键接口和实施约束"),
            "analyst": ("根因", "修复约束"),
            "implementer": ("imp／implent／实现／修复", "基础单测"),
            "tester": ("verify／测试／质量评估", "集成验证"),
            "devops": ("build／构建／CI", "实际操作结果和待授权项"),
            "uat-observer": ("live-uat／陪测／人工验收", "/live-uat", "环境记录", "用户确认实际体验"),
        }
        with tempfile.TemporaryDirectory() as directory:
            bundle = builder.build(Path(directory) / "bundle")
            assets = bundle / "assets"
            main = (assets / repository.MAIN_RULES).read_text("utf-8")
            entry = (assets / "AGENTS.md").read_text("utf-8")
            _, path_rules = main.split("**选择路径。**", 1)
            self.assertIn("当前用例的反馈直接接续本轮", main)
            path_rule = path_rules.splitlines()[0]
            for path in ("Fast Path", "Orchestrator Path"):
                self.assertIn(path, path_rule)
            path_section = path_rules.split("**路由与交付。**", 1)[0]
            stages = re.findall(r"(?m)^\d+\. \*\*(.+?)。\*\* (.+)$", path_section)
            cases = {
                "意图确认前": ("默认走 Fast Path", "只读了解上下文", "确认后才开始工程执行"),
                "确认意图时": ("目标、交付终点、验收条件和执行路径", "实际区别", "推荐和具体理由",
                              "请用户选择", "已明确选择时沿用该决定", "避免重复询问"),
                "确认路径后": ("主会话执行、验证并交付", "当前宿主的原生子 Agent",
                              "主会话接回、验收并交付", "跨角色交接由主会话完成"),
                "执行遇阻时": ("沿用已确认的路径", "在原路径内处理阻塞", "报告阻塞原因和恢复条件"),
            }
            self.assertEqual([label for label, _ in stages], list(cases))
            for label, rule in stages:
                with self.subTest(path_stage=label):
                    for term in cases[label]:
                        self.assertIn(term, rule)
            self.assertRegex(path_section, r"(?m)^确认前参考预计涉及的文件数、模块范围、.*已有失败记录")
            self.assertEqual(path_section.count("请用户选择"), 1)
            for obsolete in ("转入调度", "换路径", "再切换", "重新选择"):
                self.assertNotIn(obsolete, path_section)
            self.assertTrue(entry.startswith("在主会话开始时读取"))
            self.assertNotIn("Fast Path", entry)
            self.assertNotIn("Orchestrator Path", entry)
            entries = re.findall(r"^- \*\*([\w-]+)\*\*[^\S\n]+(.+)$", main, re.MULTILINE)
            self.assertCountEqual([role for role, _ in entries], expected_terms.keys())
            for role, description in entries:
                for term in expected_terms[role]:
                    with self.subTest(role=role, term=term):
                        self.assertIn(term, description)
            route = main.split("## 路由\n", 1)[1]
            aliases = ("plan／计划／实施方案", "diagnose／诊断／排查", "/speckit.*",
                       *(term for terms in expected_terms.values() for term in terms
                         if "／" in term or term == "/live-uat"))
            for alias in aliases:
                with self.subTest(alias=alias):
                    self.assertEqual(main.count(f"`{alias}`"), 1)
                    self.assertIn(f"`{alias}`", route)
            self.assertIn("【热词->热词】", route)
            self.assertIn(repository.MAIN_RULES, entry)
            self.assertNotIn("## 路由", entry)
            self.assertIn("`fork_context` 时用 `false`", route)
            self.assertIn("`fork_turns` 时用 `none`", route)
            self.assertRegex(route, r"(?m)^- .*plan／计划／实施方案.*本阶段只交付计划.*到此结束")
            self.assertIn("每张工单指定一个主责角色，写明交付物、授权范围和验收条件", route)
            self.assertRegex(route, r"(?m)^- \*\*architect\*\*.*架构重构设计交付可独立实施的工单，明确获得实施授权后再派代码修改")
            self.assertRegex(main, r"任一步收到 `ERROR`[^。]*失败原因[^。]*剩余资源[^。]*恢复")
            profiles = bundle / "assets/.codex/agents"
            contract_terms = {
                "architect": ("系统 → 子系统 → 组件", "关键业务用例", "自行修订并复核",
                              "前置依赖、须保持的业务行为和回归方法", "保持业务源码只读"),
                "analyst": ("预期和实际", "复现、诊断和根因定位", "授权内可行的取证后仍未定位", "最小补证需求"),
                "implementer": ("已确认的功能、缺陷或重构工单", "基础单测失败的修正与复跑",
                                "缺陷单复跑原复现用例", "重构单验证结构目标和原有业务行为"),
                "tester": ("自行修正测试资产并复跑", "其余可验项继续", "逐项列依据、步骤、实测和结论"),
                "devops": ("计划、检查、构建或发布", "从失败点复跑并继续到工单终点",
                           "发布核对目标端版本及制品", "先核对实态，再决定是否重试", "待授权操作"),
                "uat-observer": ("限时实测入口", "对应时段证据", "实际请求命中新代码",
                                 "CLEANED 附本轮资源状态", "剩余资源和恢复条件"),
            }
            for path in profiles.glob("*.toml"):
                codex_text = path.read_text("utf-8")
                instructions = tomllib.loads(codex_text)["developer_instructions"]
                copilot_text = (
                    assets / repository.profile_path("copilot", path.stem)
                ).read_text("utf-8")
                frontmatter = yaml.safe_load(copilot_text.split("---", 2)[1])
                tools = ["read", "search"]
                if path.stem not in {"architect", "analyst"}:
                    if path.stem != "uat-observer":
                        tools.append("edit")
                    tools.append("execute")
                with self.subTest(role=path.stem):
                    self.assertEqual(frontmatter["tools"], tools)
                    self.assertIs(frontmatter["include-custom-instructions"], False)
                    self.assertIs(frontmatter["user-invocable"], False)
                    self.assertNotIn(path.stem, entry)
                    for alias in aliases:
                        self.assertNotIn(alias, entry)
                        self.assertNotIn(alias, codex_text)
                        self.assertNotIn(alias, copilot_text)
                    for peer in (set(expected_terms) - {path.stem}) | {"Main"}:
                        self.assertNotRegex(codex_text, rf"(?i)\b{re.escape(peer)}\b")
                        self.assertNotRegex(copilot_text, rf"(?i)\b{re.escape(peer)}\b")
                    for term in contract_terms[path.stem]:
                        self.assertIn(term, instructions)

    def test_quality_outcomes_are_understood_by_main(self):
        source = ROOT / "source/project/.codex"
        main = (source / "agentsmd_template.md").read_text("utf-8")
        tester = tomllib.loads((source / "agents/tester.toml").read_text("utf-8"))
        for outcome in ("REJECTED", "PASS", "FAIL", "NEEDS_DECISION", "BLOCKED"):
            with self.subTest(outcome=outcome):
                self.assertIn(outcome, tester["developer_instructions"])
                self.assertIn(outcome, main)

    def test_conflict_preflight_and_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bundle = builder.build(root / "bundle")
            home = root / "home"
            skill = home / ".agents/skills/sdd-init"
            entry = skill / "SKILL.md"
            entry.parent.mkdir(parents=True)
            entry.write_bytes(b"personal")
            self.assertEqual(apply(bundle, skill, True), 1)
            self.assertEqual(entry.read_bytes(), b"personal")
            self.assertFalse((skill / "assets").exists())
            entry.unlink()
            self.assertEqual(apply(bundle, skill, False), 0)
            self.assertFalse(entry.exists())
            self.assertEqual(apply(bundle, skill, True), 0)
            self.assertEqual(apply(bundle, skill, True), 0)
            for path in bundle.rglob("*"):
                if path.is_file():
                    self.assertEqual((skill / path.relative_to(bundle)).read_bytes(), path.read_bytes())
            self.assertFalse((home / ".codex").exists())


class RepositoryOnboardingTests(unittest.TestCase):
    CI_SOURCE = "git+https://github.com/example/sdd-init.git@" + "a" * 40

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.assets = builder.build(root / "bundle") / "assets"
        self.root = root / "repo"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.main = self.root / "AGENTS.md"

    def options(self, action, harness, **kwargs):
        defaults = dict(repo=self.root, upgrade=None, merged_file=None,
                        reuse_role=[], ci_source=None, expect=None)
        return SimpleNamespace(action=action, harness=harness, **(defaults | kwargs))

    def run_command(self, action, harness, code=0, **kwargs):
        with redirect_stdout(StringIO()) as output:
            result = repository.run(self.assets, self.options(action, harness, **kwargs))
        self.assertEqual(result, code, output.getvalue())
        return output.getvalue()

    def plan_and_apply(self, harness, **kwargs):
        preview = self.run_command("plan", harness, **kwargs)
        fingerprint = preview.split("Plan: ")[-1].strip()
        return self.run_command("apply", harness, expect=fingerprint, **kwargs)

    def test_first_install_repeat_and_add_other_host_in_both_orders(self):
        for first, second in (("codex", "copilot"), ("copilot", "codex")):
            with self.subTest(first=first), tempfile.TemporaryDirectory() as directory:
                self.root = Path(directory)
                subprocess.run(["git", "init", "-q", str(self.root)], check=True)
                self.main = self.root / "AGENTS.md"
                self.plan_and_apply(first)
                self.assertEqual(self.main.read_bytes(), (self.assets / "AGENTS.md").read_bytes().replace(b"\r\n", b"\n"))
                rules = self.root / repository.MAIN_RULES
                self.assertEqual(rules.read_bytes(), (self.assets / repository.MAIN_RULES).read_bytes())
                before = {name: (self.root / repository.profile_path(first, name)).read_bytes()
                          for name in repository.ROLES}
                self.assertNotIn("Written:", self.plan_and_apply(first))
                self.assertNotIn("Written: AGENTS.md", self.plan_and_apply(second))
                self.assertEqual(rules.read_bytes(), (self.assets / repository.MAIN_RULES).read_bytes())
                self.assertFalse((self.root / ".github/workflows").exists())
                for name, profile in before.items():
                    self.assertEqual((self.root / repository.profile_path(first, name)).read_bytes(), profile)
                self.run_command("check", first)
                self.run_command("check", second)

    def test_main_rules_conflict_and_managed_update(self):
        self.plan_and_apply("codex")
        rules = self.root / repository.MAIN_RULES
        rules.write_bytes(b"Project-owned rules")
        self.assertIn("Existing file conflicts", self.run_command("plan", "codex", code=1))
        self.assertEqual(rules.read_bytes(), b"Project-owned rules")
        self.run_command("check", "codex", code=1)
        rules.write_bytes(repository.MAIN_RULES_MARKER + b"Previous managed content\n")
        root_entry = self.main.read_bytes()
        self.plan_and_apply("codex")
        self.assertEqual(self.main.read_bytes(), root_entry)
        self.assertEqual(rules.read_bytes(), (self.assets / repository.MAIN_RULES).read_bytes())

    def test_waiting_for_choice_preserves_files_and_merge_is_idempotent(self):
        personal = b"\xef\xbb\xbf# Project\r\n\r\nRun project checks.\r\n"
        self.main.write_bytes(personal)
        preview = self.run_command("plan", "codex", code=1)
        self.assertIn("(merge)", preview)
        self.assertIn("(replace)", preview)
        self.run_command("apply", "codex", code=1)
        self.assertEqual(self.main.read_bytes(), personal)
        self.assertFalse((self.root / ".codex").exists())
        self.plan_and_apply("codex", upgrade="merge")
        merged = self.main.read_bytes()
        self.assertTrue(merged.startswith(personal))
        self.assertEqual(merged.count(repository.BEGIN), 1)
        self.plan_and_apply("copilot")
        self.assertEqual(self.main.read_bytes(), merged)
        self.run_command("check", "codex")
        self.run_command("check", "copilot")

    def test_replace_rejects_stale_approval_then_replaces_reviewed_file(self):
        self.main.write_bytes(b"Original project instructions\n")
        preview = self.run_command("plan", "codex", upgrade="replace")
        self.assertIn("-Original project instructions", preview)
        fingerprint = preview.split("Plan: ")[-1].strip()
        self.main.write_bytes(b"Project edited after preview\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.run_command("apply", "codex", upgrade="replace", expect=fingerprint)
        self.assertEqual(self.main.read_bytes(), b"Project edited after preview\n")
        self.assertFalse((self.root / ".codex").exists())
        self.plan_and_apply("codex", upgrade="replace")
        self.assertEqual(self.main.read_bytes(), (self.assets / "AGENTS.md").read_bytes().replace(b"\r\n", b"\n"))

    def test_reviewed_merge_updates_managed_block_with_project_content(self):
        old = b"# Project\n\n" + repository.BEGIN + b"\nold\n" + repository.END + b"\n"
        self.main.write_bytes(old)
        candidate = self.root.parent / "reviewed.md"
        template = repository.normalized((self.assets / "AGENTS.md").read_bytes())
        candidate.write_bytes(repository.merge_rules(old.replace(b"# Project", b"# Reviewed project"), template))
        self.plan_and_apply("codex", upgrade="merge", merged_file=candidate)
        self.assertEqual(self.main.read_bytes(), candidate.read_bytes())
        self.assertEqual(self.main.read_bytes().count(repository.BEGIN), 1)
        self.run_command("check", "codex")

    def test_managed_main_block_updates_in_place(self):
        prefix = b"\xef\xbb\xbf# Project\r\n\r\nKeep this.\r\n\r\n"
        suffix = b"\r\n\r\n# Team conventions\r\n"
        previous = repository.main_block(b"# Main Agent\n\nPrevious template text.", b"\r\n")
        template = repository.normalized((self.assets / "AGENTS.md").read_bytes())
        current = repository.main_block(template, b"\r\n")
        existing = prefix + previous + suffix
        self.main.write_bytes(existing)
        self.run_command("check", "codex", code=1)
        preview = self.run_command("plan", "codex")
        self.assertIn("update managed Main block in place", preview)
        self.assertEqual(self.main.read_bytes(), existing)
        self.plan_and_apply("codex")
        self.assertEqual(self.main.read_bytes(), prefix + current + suffix)
        self.assertNotIn("Written:", self.plan_and_apply("codex"))
        self.run_command("check", "codex")

    def test_duplicate_main_markers_require_a_user_choice(self):
        block = repository.main_block(b"Managed content")
        existing = block + b"\n\n" + block + b"\n"
        self.main.write_bytes(existing)
        preview = self.run_command("plan", "codex", code=1)
        self.assertIn("malformed or repeated sdd-init Main markers", preview)
        self.assertNotIn("Plan: ", preview)
        self.assertEqual(self.main.read_bytes(), existing)

    def test_unmarked_main_requires_a_reviewed_merge(self):
        existing = b"# Main Agent\n\nProject routing.\n\n# Project conventions\n\nProject checks.\n"
        self.main.write_bytes(existing)
        preview = self.run_command("plan", "codex", code=1, upgrade="merge")
        self.assertIn("no managed block", preview)
        self.assertEqual(self.main.read_bytes(), existing)
        self.assertFalse((self.root / ".codex").exists())

    def test_custom_role_reuse_and_invalid_or_duplicate_profile(self):
        role = self.root / ".github/agents/architect.md"
        role.parent.mkdir(parents=True)
        custom = (b'---\nname: architect\ndescription: "Customized"\ninclude-custom-instructions: false\n'
                  b'user-invocable: false\ntools: ["read", "search"]\n---\nRead the repository.\n')
        role.write_bytes(custom)
        self.assertIn("--reuse-role architect", self.run_command("plan", "copilot", code=1))
        self.assertFalse(self.main.exists())
        self.plan_and_apply("copilot", reuse_role=["architect"])
        self.assertEqual(role.read_bytes(), custom)
        self.assertFalse((role.parent / "architect.agent.md").exists())
        self.run_command("check", "copilot")
        duplicate = role.parent / "architect.agent.md"
        duplicate.write_bytes(custom)
        self.assertIn("Multiple profiles", self.run_command("check", "copilot", code=1))
        duplicate.unlink()
        role.write_bytes(custom.replace(b'"search"', b'"agent"'))
        self.assertIn("expected an explicit role tool allowlist", self.run_command("check", "copilot", code=1))
        role.write_bytes(b"---\ndescription: [\n---\nRead.\n")
        self.assertIn("invalid YAML", self.run_command("check", "copilot", code=1))

    def test_ci_choice_and_missing_or_modified_inputs_fail_check(self):
        self.plan_and_apply("codex")
        workflow = self.root / ".github/workflows/sdd-init-codex.yml"
        self.assertFalse(workflow.exists())
        preview = self.run_command("plan", "codex", ci_source=self.CI_SOURCE)
        self.assertIn("sdd-init project check --repo . --harness codex", preview)
        self.assertFalse(workflow.exists())
        self.run_command("check", "codex", code=1, ci_source=self.CI_SOURCE)
        self.plan_and_apply("codex", ci_source=self.CI_SOURCE)
        self.run_command("check", "codex", ci_source=self.CI_SOURCE)
        workflow.write_bytes(b"custom workflow")
        self.run_command("plan", "codex", code=1, ci_source=self.CI_SOURCE)
        self.run_command("check", "codex", code=1, ci_source=self.CI_SOURCE)
        self.assertEqual(workflow.read_bytes(), b"custom workflow")
        (self.root / repository.profile_path("codex", "tester")).unlink()
        self.assertIn("Missing role: tester", self.run_command("check", "codex", code=1))
        self.main.write_bytes(b"missing managed rule")
        self.assertIn("missing the current Main rules", self.run_command("check", "codex", code=1))
