#!/usr/bin/env python3
"""Install project SDD resources; no Spec/Status mutation commands."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import tomllib

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
_loader = importlib.util.spec_from_file_location("sdd_project_install", Path(__file__).with_name("project_install.py"))
transaction = importlib.util.module_from_spec(_loader)
_loader.loader.exec_module(transaction)


def out(message: str) -> None:
    print(message)


def fail(message: str) -> None:
    raise ValueError(message)


def require_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        fail(f"仓库目录不存在: {root}")
    return root


def inside(root: Path, dest: Path) -> Path:
    """Reject linked paths before reading or planning installation files."""
    return transaction.safe_path(root, dest.relative_to(root).as_posix())


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def git(root: Path, *args: str) -> bytes | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
        return r.stdout if r.returncode == 0 else None
    except FileNotFoundError:
        return None


# `sdd-init` is the ONLY global skill. It carries a compressed payload that
# contains repository-local skills; storing nested SKILL.md files unpacked under
# ~/.agents/skills/sdd-init would risk discovering them as global skills.
PROJECT_PAYLOAD = ASSETS / "repo-payload.zip"
PROJECT_SKILLS = {'sdd-doc', 'sdd-imp', 'sdd-test-loop', 'sdd-review-loop', 'sdd-commit', 'sdd-deploy'}
PROJECT_ROLE_MODELS = {
    'sdd-designer': 'gpt-6-astra',
    'sdd-coder': 'gpt-6.1-sol',
    'sdd-documenter': 'gpt-6.1-terra',
    'sdd-validator': 'gpt-6.1-terra',
    'sdd-delivery': 'gpt-6.1-terra',
}
PROJECT_ROLES = set(PROJECT_ROLE_MODELS)


def validate_role(data: bytes, name: str) -> None:
    """Validate role model defaults before any target write; leave effort unset."""
    try:
        role = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        fail(f"角色 {name} 配置无效: {exc}")
    if set(role) != {"name", "description", "model", "developer_instructions"}:
        fail(f"角色 {name} 必须且仅包含名称、说明、默认模型与职责指令，不允许推理强度或其他运行配置")
    if role["name"] != name:
        fail(f"角色文件与 name 不一致: {name}")
    if any(not isinstance(value, str) or not value.strip() for value in role.values()):
        fail(f"角色 {name} 字段必须是非空文本")
    if role["model"] != PROJECT_ROLE_MODELS[name]:
        fail(f"角色 {name} 默认模型必须为 {PROJECT_ROLE_MODELS[name]}")


def project_payload(root: Path, allow_update: bool) -> list[tuple[Path, bytes, bytes | None]]:
    if not PROJECT_PAYLOAD.is_file():
        fail("仅全局 sdd-init 能初始化仓库级 Skills；当前安装器缺少 repo-payload.zip")
    changes: list[tuple[Path, bytes, bytes | None]] = []
    with zipfile.ZipFile(PROJECT_PAYLOAD) as archive:
        members = archive.namelist()
        if len(members) != len(set(members)):
            fail("项目 Skill 包内存在重复路径")
        for member in members:
            if member.endswith("/"):
                continue
            rel = Path(member)
            parts = rel.parts
            is_skill = ((len(parts) == 4 and parts[0:2] == (".agents", "skills")
                        and parts[2] in PROJECT_SKILLS and parts[3] == "SKILL.md")
                        or (len(parts) == 5 and parts[0:2] == (".agents", "skills")
                        and parts[2] in PROJECT_SKILLS and parts[3:] == ("agents", "openai.yaml"))
                        or (parts == (".agents", "skills", "sdd-commit", "references", "git-remote.md")))
            is_shared = (len(parts) == 4 and parts[0:2] == (".agents", "sdd")
                         and parts[2] in ("scripts", "assets") and parts[3] in
                         ("govern.py", "code-review-rules_template.md", "blueprint_template.md", "spec_template.md", "status_template.md", "architecture-rule-catalog.md",
                          "prototype_reference_template.md", "quickstart_template.md", "plan_template.md",
                          "test_report_template.md", "issue_template.md", "review_template.md", "sequence_template.md", "contract_template.md"))
            is_shared = is_shared or parts == (".agents", "sdd", "scripts", "doc_check.py")
            is_shared = is_shared or (len(parts) == 4 and parts[:3] == (".agents", "sdd", "references")
                                      and parts[3] in ("delegation.md", "sdd-repository-governance.md", "document-writing.md", "doc-check.md", "architecture-rules.md", "observability-baseline.md",
                                                       "scenarios.md", "prototype.md", "visual-confirmation.md"))
            is_shared = is_shared or (len(parts) == 5 and parts[:4] == (".agents", "sdd", "assets", "observability")
                                      and parts[4] in ("README.md", "event-1.0.0.schema.json"))
            is_shared = is_shared or (parts[:4] == (".agents", "sdd", "assets", "observability")
                                      and parts[4:] in (("check.py",), ("java", "pom.xml"),
                                                        ("java", "src", "main", "java", "local", "sdd", "Example.java"),
                                                        ("java", "src", "main", "java", "local", "sdd", "IsolationProbe.java"),
                                                        ("java", "src", "main", "java", "local", "sdd", "BusinessDemo.java"),
                                                        ("java", "src", "main", "java", "local", "sdd", "BusinessDemoTest.java"),
                                                        ("language-status.json",), ("language-status.json",), ("language-status.json",), ("node", "package.json"), ("node", "package-lock.json"), ("node", "example.js"),
                                                        ("python", "example.py"), ("python", "requirements.lock"),
                                                        ("go", "main.go"), ("go", "go.mod"), ("go", "go.sum"),
                                                        ("rust", "Cargo.toml"), ("rust", "Cargo.lock"), ("rust", "src", "main.rs"),
                                                        ("android", "settings.gradle"), ("android", "build.gradle"), ("android", "app", "build.gradle"),
                                                        ("android", "app", "src", "main", "AndroidManifest.xml"),
                                                        ("android", "app", "src", "main", "java", "local", "sdd", "androidexample", "MainActivity.java")))
            is_role = (len(parts) == 3 and parts[:2] == (".codex", "agents")
                       and parts[2] in {name + ".toml" for name in PROJECT_ROLES})
            is_project_default = member in ('.agents/sdd/references/sdd-repository-governance.md', 'docs/index.md')
            if not (is_skill or is_shared or is_role or is_project_default):
                fail(f"项目 Skill 包包含非法路径: {member}")
            target = inside(root, root / rel)
            for parent in target.parents:
                if parent == root:
                    break
                if (parent.exists() or parent.is_symlink()) and not parent.is_dir():
                    fail(f"项目资源父路径不是目录: {parent}")
            data = archive.read(member)
            if is_role:
                validate_role(data, rel.stem)
            before = transaction.content(target)
            if target.exists() or target.is_symlink():
                if target.is_symlink() or not target.is_file():
                    fail(f"拒绝覆盖已有符号链接或非普通文件: {target}")
                # Project-owned navigation and rules are seeded once, even on upgrade.
                if is_project_default or before == data:
                    continue
                if not allow_update:
                    fail(f"项目 Skill/角色/工具文件已被修改: {target}；请审查后使用 init --update-skills 执行明确升级")
            changes.append((target, data, before))
        found = {x for x in members if x.startswith('.agents/skills/') and x.endswith('/SKILL.md')}
        expected = {f'.agents/skills/{s}/SKILL.md' for s in PROJECT_SKILLS}
        if found != expected:
            fail("项目 Skill 包不包含完整的六个仓库级 Skill")
        required = {f'.agents/skills/{name}/agents/openai.yaml' for name in PROJECT_SKILLS}
        required.update(f'.codex/agents/{name}.toml' for name in PROJECT_ROLES)
        required.update({'.agents/sdd/scripts/govern.py', '.agents/sdd/scripts/doc_check.py', '.agents/sdd/references/doc-check.md', '.agents/sdd/references/architecture-rules.md', '.agents/sdd/assets/status_template.md',
                         '.agents/sdd/references/visual-confirmation.md', '.agents/sdd/references/document-writing.md', '.agents/sdd/references/delegation.md', '.agents/sdd/references/sdd-repository-governance.md',
                         '.agents/skills/sdd-commit/references/git-remote.md',
                         '.agents/sdd/references/observability-baseline.md',
                         '.agents/sdd/references/scenarios.md', '.agents/sdd/references/prototype.md',
                         '.agents/sdd/assets/spec_template.md', '.agents/sdd/assets/blueprint_template.md',
                         '.agents/sdd/assets/code-review-rules_template.md',
                         '.agents/sdd/assets/prototype_reference_template.md',
                         '.agents/sdd/assets/quickstart_template.md', '.agents/sdd/assets/plan_template.md', '.agents/sdd/assets/test_report_template.md', '.agents/sdd/assets/issue_template.md', '.agents/sdd/assets/review_template.md',
                         '.agents/sdd/assets/sequence_template.md',
                         '.agents/sdd/assets/contract_template.md', '.agents/sdd/references/sdd-repository-governance.md', 'docs/index.md'})
        if not required.issubset(members):
            fail("项目包缺少角色、调用策略、模板或必要引用")
    return changes


def cmd_inspect(root: Path, _: argparse.Namespace) -> int:
    out(f"Repository: {root}")
    for rel in ["AGENTS.md", "docs/index.md", "docs/blueprint.md", "specs"]:
        out(f"{'EXISTS' if (root / rel).exists() else 'MISSING'}  {rel}")
    specs = sorted((root / "specs").glob("*/spec.md")) if (root / "specs").exists() else []
    for spec in specs:
        status = spec.with_name("status.md")
        out(f"CAPABILITY {spec.parent.name}: spec=present status={'present' if status.exists() else 'missing'}")
    candidates = [p for p in (root / "docs").rglob("*.md") if any(x in p.name.lower() for x in ("architecture", "design", "blueprint"))] if (root / "docs").is_dir() else []
    for p in candidates[:20]:
        out(f"POSSIBLE_EXISTING_ARCH {p.relative_to(root)} (请人工判断，禁止自动替换)")
    out(f"Git HEAD: {(git(root, 'rev-parse', '--short', 'HEAD') or b'none').decode().strip()}")
    out("这是只读盘点；安装与升级按实际任务授权执行。")
    return 0


def prepare_agents(original: str, allow_update: bool) -> str:
    """Prepare both independent managed blocks without changing project-owned bytes."""
    bom = "\ufeff" if original.startswith("\ufeff") else ""
    original = original[len(bom):]
    names = ("agent-communication", "sdd-contract-governance")
    spans = {}
    for name in names:
        opening, closing = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
        if original.count(opening) != original.count(closing) or original.count(opening) > 1:
            fail("AGENTS.md 治理片段不完整或重复")
        if opening in original:
            begin, end = original.index(opening), original.index(closing) + len(closing)
            if end <= begin:
                fail("AGENTS.md 治理片段顺序错误")
            spans[name] = (begin, end)
    ordered = sorted(spans.values())
    if len(ordered) == 2 and ordered[0][1] > ordered[1][0]:
        fail("AGENTS.md 治理片段嵌套或交叉")
    newline = "\r\n" if "\r\n" in original else "\n"
    templates = {
        "agent-communication": read(ASSETS / "communication-fragment.md").strip(),
        "sdd-contract-governance": read(ASSETS / "agents-fragment.md").strip(),
    }
    for name, (begin, end) in spans.items():
        if original[begin:end].replace("\r\n", "\n") != templates[name] and not allow_update:
            fail("已有不同版本的 AGENTS.md 治理片段；确认升级后使用 init --update-skills")
    # Replace only owned ranges. Navigation stays where it was; communication moves first.
    body = original
    for name, (begin, end) in sorted(spans.items(), key=lambda item: item[1][0], reverse=True):
        replacement = "" if name == "agent-communication" else templates[name].replace("\n", newline)
        body = body[:begin] + replacement + body[end:]
    if "sdd-contract-governance" not in spans:
        if not body:
            body = "# Project Agent Guidance" + newline + newline
        elif not body.endswith(newline + newline):
            body += newline + newline
        body += templates["sdd-contract-governance"].replace("\n", newline) + newline
    communication = templates["agent-communication"].replace("\n", newline)
    # Reuse existing separator when already at the front, ensuring byte-stable repeats.
    separator = "" if spans.get("agent-communication", (-1,))[0] == 0 else newline + newline
    return bom + communication + separator + body


def cmd_init(root: Path, args: argparse.Namespace) -> int:
    with transaction.project_lock(root):
        transaction.recover(root)
        return initialize(root, args)


def initialize(root: Path, args: argparse.Namespace) -> int:
    # Retired entrypoints must not silently coexist with the new workflow.
    retired = [root / ".agents/skills" / name for name in ("sdd-accept",)
               if (root / ".agents/skills" / name).exists()]
    retired.extend(root / ".codex/agents" / (name + ".toml")
                   for name in ("sdd-requirements", "sdd-architect", "sdd-planner", "sdd-implementer", "sdd-acceptor")
                   if (root / ".codex/agents" / (name + ".toml")).exists())
    retired_resources = (
        ".agents/skills/sdd-commit/references/providers.md",
        *(f".agents/sdd/assets/{name}.md" for name in
          ("issue", "draft-pr", "test-plan", "acceptance", "module-design")),
    )
    retired.extend(root / rel for rel in retired_resources
                   if (root / rel).exists() or (root / rel).is_symlink())
    # Navigation is project-owned: report incompatible links, never overwrite it.
    for rel in ("docs/index.md", ".agents/sdd/references/sdd-repository-governance.md"):
        entry = inside(root, root / rel)
        if entry.is_file():
            links = re.findall(r"\]\(([^)]+)\)", read(entry))
            obsolete = {"providers.md", "issue.md", "draft-pr.md", "test-plan.md",
                        "acceptance.md", "module-design.md"}
            if any("://" not in link and "sdd" in link
                   and link.split("#")[0].rsplit("/", 1)[-1] in obsolete
                   for link in links):
                retired.append(entry)
    if retired:
        fail("发现需迁移的 SDD 资源或导航，请保留项目正文并处理以下冲突后再安装：" + ", ".join(str(p) for p in retired))
    # Preflight local skill conflicts BEFORE touching the repo.
    skill_changes = project_payload(root, args.update_skills)
    override = inside(root, root / "AGENTS.override.md")
    if override.exists() or override.is_symlink():
        fail("根目录存在 AGENTS.override.md；请先处理覆盖关系再初始化，避免治理规则未生效")
    agents = inside(root, root / "AGENTS.md")
    if agents.is_symlink() or (agents.exists() and not agents.is_file()):
        fail("拒绝覆盖 AGENTS.md 符号链接或非普通文件")
    before = transaction.content(agents)
    original = before.decode("utf-8") if before is not None else ""
    candidate = prepare_agents(original, args.update_skills)
    changes = ([(agents, candidate.encode("utf-8"), before)] if candidate != original else []) + skill_changes
    transaction.apply(root, changes)
    for target, _, _ in changes:
        out(f"INSTALLED {target}")
    out("已安装六个项目 Skills、五个独立角色及其默认模型、共享模板与导航；保留既有正文和用户运行配置，不创建需求、架构或状态实体，不设置角色推理强度。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDD resource installer: inspect and init")
    p.add_argument("--root", default=".", help="要治理的仓库目录（默认当前目录）")
    subs = p.add_subparsers(dest="cmd", required=True)
    subs.add_parser("inspect", help="只读盘点，不修改任何文件")
    a = subs.add_parser("init", help="安装 Skills、模板与 AGENTS 导航；不创建或回填项目实体，不修改用户配置")
    a.add_argument("--update-skills", action="store_true", help="经用户批准后替换已有仓库级 Skill/共享工具；绝不修改 Spec/Blueprint/Status")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = require_root(args.root)
        return {"inspect": cmd_inspect, "init": cmd_init}[args.cmd](root, args)
    except (ValueError, OSError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
