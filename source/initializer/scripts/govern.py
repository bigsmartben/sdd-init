#!/usr/bin/env python3
"""Install project SDD resources; no Spec/Status mutation commands."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
from importlib.util import source_from_cache
import json
from pathlib import Path
import re
import subprocess
import sys
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


PROJECT_SKILLS = {
    'sdd-doc', 'sdd-spec', 'sdd-imp', 'sdd-bugfix', 'sdd-test-loop', 'sdd-review-code',
    'sdd-review-prompt', 'sdd-deliver',
}
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


def shared_bundle() -> Path:
    # A build can be exercised directly. A user install publishes shared resources
    # as a sibling of the skill search root so Codex cannot discover them globally.
    shared = SKILL / "shared"
    if not shared.exists():
        skills_dir = SKILL.parent
        shared = skills_dir.with_name(f"{skills_dir.name}-sdd-init-shared")
    if not shared.is_dir() or transaction.linked(shared):
        fail(f"缺少共享资源，请重新安装用户级 sdd-init: {shared}")
    manifest = json.loads(read(SKILL / "build-manifest.json"))
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), dict):
        fail("用户级安装缺少有效的构建清单")
    expected = {name.removeprefix("shared/"): digest for name, digest in manifest["files"].items()
                if name.startswith("shared/")}
    actual = {}
    for path in shared.rglob("*"):
        if transaction.linked(path):
            fail(f"共享资源包含链接: {path}")
        if path.is_file():
            relative = path.relative_to(shared)
            name = relative.as_posix()
            if name not in expected and relative.parent.name == "__pycache__" and relative.suffix == ".pyc":
                try:
                    if Path(source_from_cache(relative)).as_posix() in expected:
                        continue
                except (NotImplementedError, ValueError):
                    pass
            actual[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        fail(f"共享资源与发布清单不一致，请检查用户级安装: {shared}")
    skills = {name for name in actual if name.startswith("skills/") and name.endswith("/SKILL.md")}
    roles = {name for name in actual if name.startswith("agents/") and name.endswith(".toml")}
    required = {
        "sdd/scripts/govern.py", "sdd/scripts/doc_check.py",
        *(f"skills/sdd-deliver/references/{name}.md" for name in ("git-delivery", "git-remote", "deployment")),
        *(f"sdd/references/{name}.md" for name in (
            "doc-check", "architecture-rules", "visual-confirmation", "document-writing", "delegation",
            "sdd-repository-governance", "observability-baseline", "scenarios", "prototype",
        )),
        *(f"sdd/assets/{name}_template.md" for name in (
            "status", "spec", "blueprint", "code-review-rules", "prototype_reference", "quickstart",
            "plan", "test_report", "issue", "review", "sequence", "contract", "research",
        )),
        *(f"skills/{name}/agents/openai.yaml" for name in PROJECT_SKILLS),
    }
    if (skills != {f"skills/{name}/SKILL.md" for name in PROJECT_SKILLS}
            or roles != {f"agents/{name}.toml" for name in PROJECT_ROLES}
            or not required <= actual.keys()):
        fail("共享资源缺少或包含未声明的 Skill、角色、模板或必要引用")
    for name in sorted(PROJECT_ROLES):
        data = (shared / "agents" / f"{name}.toml").read_bytes()
        validate_role(data, name)
    return shared.resolve()


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


def prepare_agents(original: str) -> str:
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


def cmd_init(root: Path, _: argparse.Namespace) -> int:
    with transaction.project_lock(root):
        transaction.recover(root)
        return initialize(root)


def prepare_config(original: str) -> str:
    begin = "# sdd-init roles:start"
    end = "# sdd-init roles:end"
    newline = "\r\n" if "\r\n" in original else "\n"
    references = {name: {"config_file": f"../{transaction.WORKFLOW_LINK}/agents/{name}.toml"}
                  for name in sorted(PROJECT_ROLES)}
    lines = [begin]
    for name, role in references.items():
        lines.extend((
            f"[agents.{name}]",
            f'config_file = "{role["config_file"]}"',
        ))
    lines.append(end)
    block = newline.join(lines)
    markers = list(re.finditer(rf"(?m)^(?:{begin}|{end})\r?$", original))
    if markers:
        if len(markers) != 2 or markers[0][0].rstrip("\r") != begin:
            fail(".codex/config.toml 的 SDD 角色引用块不完整、重复或顺序错误")
        first, last = markers[0].start(), markers[1].start() + len(end)
        same_block = original[first:last].replace("\r\n", "\n") == block.replace("\r\n", "\n")
        remaining = original[:first] + original[last:]
        candidate = original if same_block else original[:first] + block + original[last:]
    else:
        remaining = original
        separator = (newline if original.endswith(("\r", "\n")) else newline * 2) if original else ""
        candidate = original + separator + block + newline

    try:
        previous = tomllib.loads(original)
        unmanaged = tomllib.loads(remaining)
        merged = tomllib.loads(candidate)
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 无法合并 SDD 角色引用: {error}")
    for name, reference in references.items():
        if name in unmanaged.get("agents", {}):
            fail(f".codex/config.toml 已有同名角色 {name}；请保留并处理冲突后重试")
        if merged.get("agents", {}).get(name) != reference:
            fail(f".codex/config.toml 的 SDD 角色引用不可用: {name}")
        previous.get("agents", {}).pop(name, None)
        merged["agents"].pop(name, None)
    for config in (previous, merged):
        if config.get("agents") == {}:
            config.pop("agents")
    if previous != merged:
        fail(".codex/config.toml 的角色引用块含其他配置，请保留并处理后重试")
    return candidate


def prepare_ignore(original: str) -> str:
    entries = (f"/{transaction.WORKFLOW_LINK}", "/.sdd-init.lock", "/.sdd-init-recovery/")
    lines = original.splitlines()
    last_negation = max((index for index, line in enumerate(lines) if line.startswith("!")), default=-1)
    if all(entry in lines[last_negation + 1:] for entry in entries):
        return original
    newline = "\r\n" if "\r\n" in original else "\n"
    separator = newline if original and not original.endswith(("\r", "\n")) else ""
    return original + separator + newline.join(entries) + newline


def initialize(root: Path) -> int:
    override = inside(root, root / "AGENTS.override.md")
    if override.exists():
        fail("根目录存在 AGENTS.override.md；请先处理覆盖关系再初始化，避免治理规则未生效")

    project_entries = [
        *(f".agents/skills/{name}" for name in sorted(PROJECT_SKILLS)),
        *(f".codex/agents/{name}.toml" for name in sorted(PROJECT_ROLES)),
    ]
    conflicts = [relative for relative in project_entries
                 if (root / relative).exists() or transaction.linked(root / relative)]
    if conflicts:
        fail("项目中已有同名 SDD Skill 或角色，请处理后重新运行 init: " + ", ".join(conflicts))

    shared = shared_bundle()
    if shared.is_relative_to(root):
        fail(f"共享资源必须位于目标仓库外: {shared}")
    link = transaction.workflow_path(root)
    linked_to = transaction.workflow_target(link)
    if linked_to is not None and linked_to != shared:
        fail(f"SDD 链接已指向其他目录，请核对后重建: {link} -> {linked_to}")
    if git(root, "ls-files", "--", transaction.WORKFLOW_LINK):
        fail(f"链接位置已纳入 Git，请先处理已跟踪路径: {link}")

    changes = []
    for relative, prepare in (
        ("AGENTS.md", prepare_agents),
        (".codex/config.toml", prepare_config),
        (".gitignore", prepare_ignore),
    ):
        target = inside(root, root / relative)
        before = transaction.content(target)
        original = before.decode("utf-8") if before is not None else ""
        candidate = prepare(original)
        if candidate != original:
            changes.append((target, candidate.encode("utf-8"), before))
    transaction.apply(root, changes, shared=shared if linked_to is None else None)
    for target, _, _ in changes:
        out(f"INSTALLED {target}")
    out(f"SDD WORKFLOW {link} -> {shared}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDD resource installer: inspect and init")
    p.add_argument("--root", default=".", help="要治理的仓库目录（默认当前目录）")
    subs = p.add_subparsers(dest="cmd", required=True)
    subs.add_parser("inspect", help="只读盘点，不修改任何文件")
    subs.add_parser("init", help="接入用户级共享资源并同步项目中的 SDD 托管块")
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
