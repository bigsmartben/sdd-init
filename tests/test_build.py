from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import stat
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

WORKFLOW = ".agents/sdd-workflow"
LEGACY_WORKFLOW = ".agents/skills/sdd-workflow"
PROJECT_SKILLS = (
    "sdd-architecture", "sdd-bugfix", "sdd-deliver", "sdd-develop", "sdd-refactor", "sdd-test-loop",
)
ROOT = Path(__file__).resolve().parent.parent
INSTALL_FIXTURES = ROOT / "tests/fixtures/install"
spec = importlib.util.spec_from_file_location("build_release", ROOT / "scripts/build_release.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def project_entries(root):
    """Installation may create only its stable one-byte lock during preflight."""
    lock = root / ".sdd-init.lock"
    if lock.exists():
        assert lock.read_bytes() == b"\0", lock
    return [p for p in root.iterdir() if p != lock]


def project_files(root):
    """Snapshot local files without following symlinks or Windows junctions."""
    project_entries(root)
    files, pending = [], [root]
    while pending:
        for path in pending.pop().iterdir():
            if path == root / ".sdd-init.lock":
                continue
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                continue
            if path.is_dir():
                pending.append(path)
            elif path.is_file():
                files.append(path)
    return sorted(files)


def refresh_manifest(build):
    manifest = build / "build-manifest.json"
    files = {path.relative_to(build).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in builder.source_files(build) if path != manifest}
    manifest.write_text(json.dumps({"schema_version": 1, "files": files}), encoding="utf-8")


def legacy_fragment(name):
    return (INSTALL_FIXTURES / f"legacy-{name}.md").read_text(encoding="utf-8").strip()


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def test_payload_and_shared_resources_match_canonical_source(self):
        output = builder.build(self.folder / "skill")
        project = ROOT / "source/project"
        for source, target in ((".agents/skills", "skills"), (".agents/sdd", "sdd")):
            canonical = project / source
            shared = output / "shared" / target
            expected = {p.relative_to(canonical): p.read_bytes() for p in builder.source_files(canonical)}
            self.assertEqual({p.relative_to(shared): p.read_bytes() for p in builder.source_files(shared)}, expected)
        self.assertFalse((output / "assets/repo-payload.zip").exists())
        self.assertFalse((output / "assets/spec_template.md").exists())
        self.assertEqual((output / "scripts/release.py").read_bytes(),
                         (ROOT / "src/sdd_init/release.py").read_bytes())
        path = "shared/roles/codex/review-prompt.toml"
        data = (output / path).read_bytes()
        role = tomllib.loads(data.decode("utf-8"))
        self.assertEqual(role["name"], "review-prompt")
        contract = output / "shared/roles/shared/review-prompt.md"
        copilot = output / "shared/roles/copilot/review-prompt.agent.md"
        self.assertTrue(contract.is_file())
        self.assertIn("roles/shared/review-prompt.md", role["developer_instructions"])
        self.assertIn(".agents/sdd-workflow/roles/shared/review-prompt.md", role["developer_instructions"])
        contract_text = contract.read_text(encoding="utf-8")
        self.assertIn(".agents/sdd-workflow/roles/shared/review-prompt.md", contract_text)
        self.assertIn("review-prompt/prompt-review.md", contract_text)
        self.assertNotIn("model:", copilot.read_text(encoding="utf-8"))
        self.assertIn("roles/shared/review-prompt.md", copilot.read_text(encoding="utf-8"))
        manifest = json.loads((output / "build-manifest.json").read_bytes())
        self.assertEqual(manifest["files"][path], hashlib.sha256(data).hexdigest())
        self.assertFalse((output / "assets/user-agents/review-prompt.toml").exists())

    def test_build_is_reproducible_and_does_not_overwrite(self):
        first = builder.build(self.folder / "first")
        second = builder.build(self.folder / "second")
        contents = lambda p: {f.relative_to(p): f.read_bytes() for f in builder.source_files(p)}
        self.assertEqual(contents(first), contents(second))
        with self.assertRaises(FileExistsError):
            builder.build(first)
        with self.assertRaises(ValueError):
            builder.build(ROOT / "source/not-an-output")

    def test_init_connects_cleaned_project_and_preserves_project_configuration(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        index = target / "docs/index.md"
        index.parent.mkdir()
        index_body = b"# Project\n[Previous template](../.agents/sdd/assets/spec_template.md)\n"
        index.write_bytes(index_body)
        rules = target / "docs/repository-governance.md"
        rules.write_bytes(b"# Existing project rules\n")
        agents = target / "AGENTS.md"
        project_rules = b"# Existing project guidance\r\n"
        agents.write_bytes(project_rules)
        config = target / ".codex/config.toml"
        config.parent.mkdir()
        project_config = b'model = "main-model"\r\n[mcp_servers.custom]\r\nurl = "https://example.invalid/mcp"\r\n'
        config.write_bytes(project_config + (
            b"\r\n# sdd-init roles:start\r\n[agents.sdd-coder]\r\n"
            b'config_file = "agents/sdd-coder.toml"\r\n'
            b"# sdd-init roles:end\r\n"
        ))
        (target / "architecture").mkdir()
        contract = target / "architecture/blueprint.md"
        contract.write_bytes(b"# Existing architecture\n")
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(contract.read_bytes(), b"# Existing architecture\n")
        self.assertIn(project_rules, agents.read_bytes())
        self.assertIn(WORKFLOW.encode(), agents.read_bytes())
        self.assertNotIn(b"/sdd-commit/SKILL.md", agents.read_bytes())
        self.assertTrue(config.read_bytes().startswith(project_config))
        self.assertIn(f'config_file = "../{WORKFLOW}/roles/codex/sdd-coder.toml"'.encode(), config.read_bytes())
        self.assertTrue((target / WORKFLOW).samefile(skill / "shared"))
        self.assertEqual(index.read_bytes(), index_body)
        self.assertEqual(rules.read_bytes(), b"# Existing project rules\n")
        before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_new_install_has_only_current_skills_and_no_project_entities(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({p.name for p in (target / ".agents/skills").iterdir()}, set(PROJECT_SKILLS))
        links = {WORKFLOW: skill / "shared",
                 **{f".agents/skills/{name}": skill / "shared/skills" / name for name in PROJECT_SKILLS}}
        for relative, shared in links.items():
            path = target / relative
            self.assertTrue(path.is_dir(), relative)
            self.assertTrue(path.samefile(shared), relative)
            if sys.platform == "win32":
                self.assertEqual(path.lstat().st_reparse_tag, 0xA0000003, relative)
            else:
                self.assertTrue(path.is_symlink(), relative)
        self.assertFalse((target / LEGACY_WORKFLOW).exists())
        for name in ("specs", "architecture", ".codex/agents", ".agents/sdd", "plan.md", "docs/index.md", "docs/code-review-rules.md", "docs/review-matrix.md"):
            self.assertFalse((target / name).exists(), name)
        for name in ("spec_template.md", "blueprint_template.md", "plan_template.md", "quickstart_template.md", "prototype_reference_template.md",
                     "test_report_template.md", "issue_template.md", "review_template.md", "review-matrix_template.md", "sequence_template.md", "contract_template.md",
                     "delivery_record_template.md"):
            self.assertTrue((target / WORKFLOW / "sdd/assets" / name).is_file(), name)
        assets = target / WORKFLOW / "sdd/assets"
        self.assertEqual(
            {p.name for p in assets.glob("*.md")},
            {"spec_template.md", "blueprint_template.md", "status_template.md",
             "plan_template.md", "quickstart_template.md", "prototype_reference_template.md",
             "test_report_template.md", "issue_template.md", "review_template.md", "review-matrix_template.md", "sequence_template.md", "contract_template.md",
             "architecture-rule-catalog.md", "code-review-rules_template.md", "research_template.md",
             "delivery_record_template.md"})
        checker = target / WORKFLOW / "sdd/scripts/doc_check.py"
        checked = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(checker), "--root", str(target),
             "--format", "json", "AGENTS.md"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        guidance = (target / "AGENTS.md").read_text(encoding="utf-8")
        for retired in ("sdd-documenter", "sdd-review-prompt", "review-repo-prompt", "sdd-workflow-review"):
            self.assertNotIn(retired, guidance)
        manifest = json.loads((skill / "build-manifest.json").read_bytes())
        for name in manifest["files"]:
            self.assertTrue({"sdd-review-prompt", "review-repo-prompt", "sdd-workflow-review",
                             "prompt_review_template.md"}.isdisjoint(Path(name).parts), name)
        self.assertFalse((target / WORKFLOW / "sdd/assets/issue.md").exists())
        for retired in ("draft-pr.md", "test-plan.md", "acceptance.md", "module-design.md"):
            self.assertFalse((target / WORKFLOW / "sdd/assets" / retired).exists(), retired)

    def test_project_review_assets_survive_install_reinstall_and_upgrade(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        assets = {
            "docs/code-review-rules.md": "# Code Review Rules\n\nCR-001 用户确认的项目规则。\n".encode("utf-8"),
            "docs/review-matrix.md": "# Review Matrix\n\nRM-017 项目自有矩阵及有效例外。\n".encode("utf-8"),
            "docs/blueprint.md": b"# Blueprint\r\n\r\n[Review Matrix](review-matrix.md)\r\n",
        }
        for name, content in assets.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                   "--root", str(target), "init"]
        for version in range(3):
            if version == 2:
                # Upgrade shared knowledge while preserving the project's normative assets.
                template = skill / "shared/sdd/assets/review-matrix_template.md"
                template.write_bytes(template.read_bytes() + b"\n<!-- candidate revision -->\n")
                refresh_manifest(skill)
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name, content in assets.items():
                self.assertEqual((target / name).read_bytes(), content, name)
            self.assertTrue((target / WORKFLOW / "sdd/assets/code-review-rules_template.md").is_file())
            self.assertEqual((target / WORKFLOW / "sdd/assets/review-matrix_template.md").read_bytes(),
                             (skill / "shared/sdd/assets/review-matrix_template.md").read_bytes())

    def test_main_block_install_preserves_project_content_and_repeats(self):
        skill = builder.build(self.folder / "skill")
        navigation = (skill / "assets/agents-fragment.md").read_text(encoding="utf-8").strip()
        source = (ROOT / "source/project/.agents/sdd/references/visual-confirmation.md").read_bytes()
        for newline in ("\n", "\r\n"):
            for kind in ("new", "existing", "positioned"):
                with self.subTest(newline=repr(newline), kind=kind):
                    target = self.folder / (kind + str(len(newline)))
                    target.mkdir()
                    prefix = "# 用户约定" + newline + "保留全部正文。" + newline
                    suffix = newline + "末尾规则，无结束换行"
                    old = {
                        "new": None,
                        "existing": prefix + suffix,
                        "positioned": prefix + navigation.replace("\n", newline) + suffix,
                    }[kind]
                    agents = target / "AGENTS.md"
                    if old is not None:
                        agents.write_bytes(old.encode("utf-8"))
                    command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
                    result = subprocess.run(command, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    installed = agents.read_bytes().decode("utf-8")
                    self.assertNotIn("<!-- agent-communication:", installed)
                    self.assertEqual(installed.count("**Align — 意图对齐**"), 1)
                    self.assertEqual(installed.count("<!-- sdd-contract-governance:start -->"), 1)
                    if old is not None:
                        self.assertIn(prefix, installed)
                        self.assertIn(suffix, installed)
                        self.assertLess(installed.index(prefix), installed.index(suffix))
                        nav = navigation.replace("\n", newline)
                        if kind == "positioned":
                            self.assertEqual(installed, prefix + nav + suffix)
                        else:
                            self.assertIn(prefix + suffix, installed)
                    self.assertEqual((target / WORKFLOW / "sdd/references/visual-confirmation.md").read_bytes(), source)
                    before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
                    result = subprocess.run(command, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_main_alignment_and_legacy_communication_upgrade(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
        def run():
            return subprocess.run(command, capture_output=True)
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        agents = target / "AGENTS.md"
        rule = target / WORKFLOW / "sdd/references/visual-confirmation.md"
        source = (ROOT / "source/project/.agents/sdd/references/visual-confirmation.md").read_bytes()
        current = (skill / "assets/agents-fragment.md").read_text(encoding="utf-8").strip()
        self.assertIn(current, agents.read_text(encoding="utf-8"))
        self.assertFalse((skill / "assets/communication-fragment.md").exists())
        confirmation_link = f"[意图对齐]({WORKFLOW}/sdd/references/visual-confirmation.md#意图对齐)"
        self.assertIn("**Align — 意图对齐**", current)
        self.assertIn("已有确认持续沿用，仅目标实质变化、约束冲突或缺少必要授权时重新对齐", current)
        self.assertIn(confirmation_link, current)
        self.assertIn("需求与方案分开讨论、分别确认", rule.read_text(encoding="utf-8"))
        self.assertEqual(rule.read_bytes(), source)
        old = legacy_fragment("communication")
        body = "# 用户正文\r\n保持这些规则。\n"
        agents.write_bytes((body + old + "\n" + current).encode("utf-8"))
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = agents.read_text(encoding="utf-8")
        self.assertIn(body.replace("\r\n", "\n"), installed)
        self.assertNotIn("<!-- agent-communication:", installed)
        self.assertIn(current, installed)
        self.assertEqual(rule.read_bytes(), source)
        before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_bom_preserved_at_start_on_install_and_upgrade(self):
        skill = builder.build(self.folder / "skill")
        for upgrade in (False, True):
            target = self.folder / str(upgrade)
            target.mkdir()
            body = "# 原项目正文\r\n保留。\n尾部"
            original = "\ufeff" + body
            if upgrade:
                original += "\r\n" + (skill / "assets/agents-fragment.md").read_text(encoding="utf-8").strip().replace("\n", "\r\n")
            agents = target / "AGENTS.md"
            agents.write_bytes(original.encode("utf-8"))
            command = [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"), "--root", str(target), "init"]
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = agents.read_bytes()
            self.assertTrue(data.startswith(b"\xef\xbb\xbf" + body.encode("utf-8")))
            self.assertEqual(data.count(b"\xef\xbb\xbf"), 1)
            self.assertIn(body.encode("utf-8"), data)
            result = subprocess.run(command, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agents.read_bytes(), data)

    def test_legacy_two_block_state_is_replaced(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        target.mkdir()
        old_agents = ("# Project-owned guidance\r\n" + legacy_fragment("communication")
                      + "\r\n" + legacy_fragment("navigation").replace("\n", "\r\n")
                      + "\r\n# Project-owned ending\r\n")
        (target / "AGENTS.md").write_bytes(old_agents.encode("utf-8"))
        (target / ".sdd-init-state.json").write_text(json.dumps({
            "schema_version": 1, "shared_version": "0" * 64,
            "agents_blocks": {"agent-communication": "0" * 64,
                              "sdd-contract-governance": "0" * 64},
        }), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        current = (target / "AGENTS.md").read_bytes()
        self.assertTrue(current.startswith(b"# Project-owned guidance\r\n"))
        self.assertTrue(current.endswith(b"# Project-owned ending\r\n"))
        self.assertNotIn(b"agent-communication", current)
        self.assertEqual(current.count(b"<!-- sdd-contract-governance:start -->"), 1)
        state = json.loads((target / ".sdd-init-state.json").read_bytes())
        self.assertEqual(set(state["agents_blocks"]), {"sdd-contract-governance"})

    def test_blocked_payload_parent_fails_before_agents_write(self):
        skill = builder.build(self.folder / "skill")
        for parent in (".agents", ".agents/skills"):
            target = self.folder / parent.replace("/", "-")
            blocker = target / parent
            blocker.parent.mkdir(parents=True)
            blocker.write_bytes(b"user-owned file")
            (target / "AGENTS.md").write_bytes(b"existing body\r\n")
            before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
            result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                     "--root", str(target), "init"], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_managed_block_errors_and_override_leave_project_unchanged(self):
        skill = builder.build(self.folder / "skill")
        cstart, cend = "<!-- agent-communication:start -->", "<!-- agent-communication:end -->"
        nstart, nend = "<!-- sdd-contract-governance:start -->", "<!-- sdd-contract-governance:end -->"
        malformed = [cstart, cend, cend + cstart, cstart + cend + cstart + cend,
                     nstart, nend, nstart + nend + nstart + nend,
                     cstart + nstart + nend + cend, cstart + nstart + cend + nend]
        for i, content in enumerate(malformed + ["override-with-marker"]):
            target = self.folder / f"invalid-{i}"
            target.mkdir()
            (target / "AGENTS.md").write_text(content, encoding="utf-8")
            if content.startswith("override"):
                (target / "AGENTS.override.md").write_text(nstart if content.endswith("marker") else "custom", encoding="utf-8")
            before = {p.relative_to(target): p.read_bytes() for p in project_files(target)}
            result = subprocess.run([sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                                     "--root", str(target), "init"], capture_output=True)
            self.assertNotEqual(result.returncode, 0, content)
            self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in project_files(target)})

    def test_init_leaves_files_outside_the_current_workflow_scope(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "project"
        files = {
            ".agents/sdd/assets/test-plan.md": b"# Project notes\n",
            ".agents/skills/sdd-accept/SKILL.md": b"# Existing workflow notes\n",
            ".codex/agents/project-architect.toml": b'name = "project-architect"\n',
        }
        for relative, content in files.items():
            entry = target / relative
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_bytes(content)
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        for relative, content in files.items():
            self.assertEqual((target / relative).read_bytes(), content)

    def test_distribution_is_generic_and_reference_paths_resolve(self):
        skill = builder.build(self.folder / "skill")
        target = self.folder / "unrelated-project"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        for base in (skill, target):
            for path in base.rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                for marker in ("hanxue-live", "dc-contract.md", "examples/classroom", "课堂应用",
                               "本仓路径映射", "ARC-006/010/011", "docs/governance/repository.md"):
                    self.assertNotIn(marker, text, (path, marker))
        for path in (target / WORKFLOW).rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#")[0]).is_file(), (path, link))

    def test_unregistered_shared_file_rejected_before_writing(self):
        skill = builder.build(self.folder / "skill")
        extra = skill / "shared/sdd/references/unapproved.md"
        extra.write_text("unexpected", encoding="utf-8")
        target = self.folder / "project"
        target.mkdir()
        agents = target / "AGENTS.md"
        agents.write_bytes(b"existing rules")
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
             "--root", str(target), "init"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("清单不一致", result.stderr)
        self.assertEqual(project_entries(target), [agents])
        self.assertEqual(agents.read_bytes(), b"existing rules")

    def test_missing_required_shared_resources_fail_before_writing(self):
        skill = builder.build(self.folder / "skill")
        for index, relative in enumerate((
            "skills/sdd-deliver/SKILL.md", "skills/sdd-deliver/agents/openai.yaml",
            "sdd/references/delivery.md", "sdd/references/release-evidence.md",
            "sdd/references/git-delivery.md", "sdd/references/git-remote.md",
            "sdd/references/deployment.md", "sdd/references/traffic.md", "sdd/references/recovery.md",
            "sdd/assets/delivery_record_template.md",
            "skills/sdd-bugfix/SKILL.md", "skills/sdd-bugfix/agents/openai.yaml",
            "skills/sdd-develop/SKILL.md", "skills/sdd-develop/agents/openai.yaml",
            "skills/sdd-architecture/SKILL.md", "skills/sdd-architecture/agents/openai.yaml",
            "skills/sdd-test-loop/SKILL.md", "skills/sdd-test-loop/agents/openai.yaml",
            "skills/sdd-refactor/SKILL.md", "skills/sdd-refactor/agents/openai.yaml",
            "sdd/scripts/govern.py", "sdd/scripts/doc_check.py", "sdd/references/doc-check.md",
            "sdd/assets/status_template.md", "sdd/assets/code-review-rules_template.md", "sdd/assets/review-matrix_template.md",
            "sdd/assets/spec_template.md", "sdd/assets/quickstart_template.md",
            "sdd/assets/plan_template.md", "sdd/assets/sequence_template.md",
            "sdd/assets/test_report_template.md", "sdd/assets/issue_template.md",
            "sdd/assets/review_template.md", "sdd/assets/research_template.md", "sdd/references/document-writing.md",
            "sdd/references/visual-confirmation.md", "sdd/references/implementation.md", "sdd/references/task-receipt.md",
        )):
            with self.subTest(missing=relative):
                path = skill / "shared" / relative
                original = path.read_bytes()
                path.unlink()
                refresh_manifest(skill)
                target = self.folder / f"missing-{index}"
                target.mkdir()
                result = subprocess.run(
                    [sys.executable, "-B", "-X", "utf8", str(skill / "scripts/govern.py"),
                     "--root", str(target), "init"], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(project_entries(target), [])
                path.write_bytes(original)
                refresh_manifest(skill)


if __name__ == "__main__":
    unittest.main()
