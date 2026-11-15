#!/usr/bin/env python3
"""Install project SDD resources; no Spec/Status mutation commands."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"


def load_tool(path: Path):
    spec = importlib.util.spec_from_file_location(f"sdd_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


transaction = load_tool(Path(__file__).with_name("project_install.py"))
release = load_tool(Path(__file__).with_name("release.py"))


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
    if transaction.linked(path) or not path.is_file():
        fail(f"文件不存在: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"文件不是有效 UTF-8: {path}") from error


def git(root: Path, *args: str) -> bytes | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
        return r.stdout if r.returncode == 0 else None
    except FileNotFoundError:
        return None


PROJECT_SKILLS = set(transaction.PROJECT_SKILLS)
PROJECT_ROLE_MODELS = {
    'sdd-architect': 'gpt-6-astra',
    'sdd-product-manager': 'gpt-6-astra',
    'sdd-coder': 'gpt-6.1-sol',
    'sdd-devops': 'gpt-6.1-terra',
    'sdd-doc-consistency': 'gpt-6.1-terra',
}
PROJECT_ROLES = set(PROJECT_ROLE_MODELS)
RETIRED_SKILLS = {
    "sdd-spec", "sdd-imp", "sdd-review-code", "sdd-review-loop", "sdd-review-prompt",
    "sdd-doc", "sdd-commit", "sdd-deploy",
}
RETIRED_ROLES = {"sdd-delivery", "sdd-designer", "sdd-documenter", "sdd-validator"}
FRAGMENTS = {"agent-communication": "communication-fragment.md", "sdd-contract-governance": "agents-fragment.md"}


def validate_role(data: bytes, name: str) -> None:
    """Validate the shared role fields and default model before any target write."""
    try:
        role = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        fail(f"角色 {name} 配置无效: {exc}")
    fields = {"name", "description", "developer_instructions", "model"}
    if set(role) != fields:
        fail(f"角色 {name} 的字段必须为: {', '.join(sorted(fields))}")
    if role["name"] != name:
        fail(f"角色文件与 name 不一致: {name}")
    if any(not isinstance(value, str) or not value.strip() for value in role.values()):
        fail(f"角色 {name} 字段必须是非空文本")
    if role["model"] != PROJECT_ROLE_MODELS[name]:
        fail(f"角色 {name} 默认模型必须为 {PROJECT_ROLE_MODELS[name]}")


def skill_name(path: Path) -> str | None:
    frontmatter = re.match(r"\A\ufeff?---\n(.+?)\n---(?:\n|$)", read(path), re.DOTALL)
    if frontmatter:
        name = re.search(r"""(?m)^name:[ \t]*(["']?)([\w-]+)\1[ \t]*(?:#[^\n]*)?$""", frontmatter[1])
        if name:
            return name[2]
    return None


def shared_path() -> Path:
    # A build can be exercised directly. A user install publishes shared resources
    # as a sibling of the skill search root so Codex cannot discover them globally.
    shared = SKILL / "shared"
    if not shared.exists() and not transaction.linked(shared):
        shared = release.shared_directory(SKILL.parent)
    return shared


def shared_bundle(shared: Path) -> tuple[str, str, dict[str, str]]:
    recovery = release.recovery_directory(SKILL.parent)
    if recovery.exists() or transaction.linked(recovery):
        fail(f"共享安装有未完成的事务: {recovery}；先运行用户级 sdd-init recover 检查并恢复")
    if not shared.is_dir() or transaction.linked(shared):
        fail(f"缺少共享资源，请重新安装用户级 sdd-init: {shared}")
    try:
        files = release.verified(SKILL, shared=None if shared == SKILL / "shared" else shared,
                                 installed=True)
    except ValueError as error:
        fail(f"安装资源与清单不一致: {error}")
    actual = release.shared_files(files)
    skills = {name for name in actual if name.endswith("/SKILL.md")}
    roles = {name for name in actual if name.startswith("agents/") and name.endswith(".toml")}
    required = {
        "sdd/scripts/govern.py", "sdd/scripts/doc_check.py",
        *(f"sdd/references/{name}.md" for name in (
            "doc-check", "architecture-rules", "visual-confirmation", "document-writing", "delegation", "task-receipt",
            "sdd-repository-governance", "observability-baseline", "scenarios", "prototype", "implementation",
            "delivery", "release-evidence", "git-delivery", "git-remote", "deployment", "traffic", "recovery",
        )),
        *(f"sdd/assets/{name}_template.md" for name in (
            "status", "spec", "blueprint", "code-review-rules", "review-matrix", "prototype_reference", "quickstart",
            "plan", "test_report", "issue", "review", "sequence", "contract", "research", "delivery_record",
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
    for name in sorted(PROJECT_SKILLS):
        if skill_name(shared / "skills" / name / "SKILL.md") != name:
            fail(f"Skill 入口的 name 与分发目录不一致: {name}")
    fragments = {name: read(ASSETS / path).strip() for name, path in FRAGMENTS.items()}
    checker = load_tool(shared / "sdd/scripts/doc_check.py")
    for fragment in fragments.values():
        for line in fragment.splitlines():
            for dest in checker.inline_links(line):
                relative, _, anchor = dest.partition("#") if dest else ("", "", "")
                prefixes = {transaction.WORKFLOW_LINK + "/": "",
                            **{f".agents/skills/{name}/": f"skills/{name}/" for name in PROJECT_SKILLS}}
                target = next((replacement + relative[len(prefix):]
                               for prefix, replacement in prefixes.items() if relative.startswith(prefix)), None)
                if target not in actual:
                    fail(f"托管导航引用无效: {dest}")
                if anchor and anchor not in checker.anchor_set(checker.visible_lines(read(shared / target))[0]):
                    fail(f"托管导航锚点不存在: {dest}")
    return release.content_id(files), release.content_id(actual), fragments


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
    shared = shared_path()
    out(f"Shared source: {shared}")
    recovery = root / transaction.RECOVERY
    pending = recovery.exists() or transaction.linked(recovery)
    if pending:
        out(f"PENDING {recovery}; run recover or retry init after reviewing conflicts")
        try:
            transaction.load(root, transaction.safe_path(root, transaction.RECOVERY))
        except (ValueError, OSError, KeyError, TypeError) as error:
            raise ValueError(f"恢复记录需人工核对: {recovery}: {error}") from error
    _, version, fragments = shared_bundle(shared)
    out(f"Shared version: sha256:{version}")
    out(f"Shared skill entries: {', '.join(sorted(PROJECT_SKILLS))}")
    out(f"Shared role definitions: {', '.join(sorted(PROJECT_ROLES))}")
    link, linked_to = check_project(root, shared)
    out(f"Project link: {link} -> {linked_to or '(missing)'}")
    links = transaction.plan_links(root, shared)
    for path, before, target in links:
        out(f"Project entry: {path.relative_to(root).as_posix()} -> "
            f"{before['target'] if before else '(missing)'}"
            + (" (legacy; remove on init)" if target is None and before else ""))
    files = plan_files(root, version, fragments)
    current = read_state(files[3][2])
    out(f"Project recorded shared version: {current.get('shared_version', 'none')}")
    doc_index = root / "docs/index.md"
    out(f"Project documentation index: {doc_index}" if doc_index.is_file()
        else "Project documentation index: resolve the project's own entry from its guidance")
    config = files[1][2]
    roles = sorted(set(tomllib.loads(config.decode('utf-8')).get('agents', {})) & PROJECT_ROLES) if config else []
    out(f"Registered roles: {', '.join(roles) or 'none'}")
    changes = [path.relative_to(root).as_posix() for path, data, before in files if data != before]
    changes.extend(path.relative_to(root).as_posix() for path, before, target in links
                   if (before["target"] if before else None) != (str(target) if target else None))
    out(f"Project changes on init: {', '.join(changes) or 'none'}")
    if not pending:
        out("Next: run init to apply the project plan" if changes
            else "Project connection is current")
    return 0


def prepare_agents(original: str, templates: dict[str, str], remembered: dict[str, str]) -> str:
    """Prepare both independent managed blocks without changing project-owned bytes."""
    bom = "\ufeff" if original.startswith("\ufeff") else ""
    original = original[len(bom):]
    spans = {}
    history = json.loads(read(ASSETS / "managed-agents-history.json"))
    for name in FRAGMENTS:
        opening, closing = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
        starts = list(re.finditer(rf"(?m)^{re.escape(opening)}\r?$", original))
        ends = list(re.finditer(rf"(?m)^{re.escape(closing)}\r?$", original))
        if (len(starts) != len(ends) or len(starts) > 1
                or len(starts) != original.count(opening) or len(ends) != original.count(closing)):
            fail("AGENTS.md 治理片段不完整或重复")
        if starts:
            begin, end = starts[0].start(), ends[0].start() + len(closing)
            if ends[0].start() <= begin:
                fail("AGENTS.md 治理片段顺序错误")
            spans[name] = (begin, end)
    ordered = sorted(spans.values())
    if len(ordered) == 2 and ordered[0][1] > ordered[1][0]:
        fail("AGENTS.md 治理片段嵌套或交叉")
    newline = "\r\n" if "\r\n" in original else "\n"
    for name, (begin, end) in spans.items():
        digest = release.digest(original[begin:end].replace("\r\n", "\n").encode())
        if (digest != remembered.get(name) and digest not in history[FRAGMENTS[name]]
                and original[begin:end].replace("\r\n", "\n") != templates[name]):
            fail(f"AGENTS.md 的 {name} 托管块含定制或来源不明；请保留并核对片段后重试")
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
        with release.user_lock(SKILL.parent, shared_read=True):
            return initialize(root)


def cmd_recover(root: Path, _: argparse.Namespace) -> int:
    with transaction.project_lock(root):
        if not transaction.recover(root):
            out(f"No pending project recovery: {root}")
    return 0


def role_reference(name: str) -> str:
    return f"../{transaction.WORKFLOW_LINK}/agents/{name}.toml"


def legacy_role_reference(name: str) -> str:
    return f"../{transaction.LEGACY_WORKFLOW_LINK}/agents/{name}.toml"


def prepare_config(original: str) -> str:
    begin = "# sdd-init roles:start"
    end = "# sdd-init roles:end"
    newline = "\r\n" if "\r\n" in original else "\n"
    references = {name: {"config_file": role_reference(name)} for name in sorted(PROJECT_ROLES)}
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
        old_block = original[first:last]
        same_block = old_block.replace("\r\n", "\n") == block.replace("\r\n", "\n")
        old_lines = old_block.splitlines()[1:-1]
        if not old_lines or len(old_lines) % 2:
            fail(".codex/config.toml 的 SDD 角色引用块含定制；请保留并核对后重试")
        for header, setting in zip(old_lines[::2], old_lines[1::2]):
            name = header.removeprefix("[agents.").removesuffix("]")
            known = {f'config_file = "{role_reference(name)}"',
                     f'config_file = "{legacy_role_reference(name)}"'}
            # The old project-local form is recognized after its role file
            # has been moved out of discovery (checked during preflight).
            if name in PROJECT_ROLES:
                known.add(f'config_file = "agents/{name}.toml"')
            if name not in PROJECT_ROLES | RETIRED_ROLES or header != f"[agents.{name}]" or setting not in known:
                fail(f".codex/config.toml 的 SDD 角色引用块含定制 ({header})；请保留并核对后重试")
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
    retired_paths = {reference(name) for name in RETIRED_ROLES
                     for reference in (role_reference, legacy_role_reference)}
    for name, role in unmanaged.get("agents", {}).items():
        reference = role.get("config_file") if isinstance(role, dict) else None
        if isinstance(reference, str):
            normalized = reference.replace("\\", "/")
            if normalized.startswith(f"../{transaction.LEGACY_WORKFLOW_LINK}/"):
                fail(f".codex/config.toml 的项目角色 {name} 定制引用旧共享路径；请保留并迁移引用")
            if normalized in retired_paths:
                fail(f".codex/config.toml 的项目角色 {name} 引用已退役的共享角色；请保留并迁移引用")
    # Migrate only exact legacy references generated inside our managed block.
    previous_roles = previous.get("agents", {})
    for legacy_role in RETIRED_ROLES:
        legacy_references = [{"config_file": reference(legacy_role)}
                             for reference in (role_reference, legacy_role_reference)]
        if legacy_role not in unmanaged.get("agents", {}) and previous_roles.get(legacy_role) in legacy_references:
            previous_roles.pop(legacy_role)
    for config in (previous, merged):
        if config.get("agents") == {}:
            config.pop("agents")
    if previous != merged:
        fail(".codex/config.toml 的角色引用块含其他配置，请保留并处理后重试")
    return candidate


def prepare_ignore(original: str) -> str:
    entries = (f"/{transaction.WORKFLOW_LINK}", *(f"/{path}" for path in transaction.SKILL_LINKS),
               f"/{transaction.LOCK}", f"/{transaction.RECOVERY}/", f"/{transaction.STATE}")
    lines = original.splitlines()
    last_negation = max((index for index, line in enumerate(lines) if line.startswith("!")), default=-1)
    missing = [entry for entry in entries if entry not in lines[last_negation + 1:]]
    if not missing:
        return original
    newline = "\r\n" if "\r\n" in original else "\n"
    separator = newline if original and not original.endswith(("\r", "\n")) else ""
    return original + separator + newline.join(missing) + newline


def check_project(root: Path, shared: Path) -> tuple[Path, Path | None]:
    override = inside(root, root / "AGENTS.override.md")
    if override.exists():
        fail("根目录存在 AGENTS.override.md；请先处理覆盖关系再初始化，避免治理规则未生效")

    links = transaction.plan_links(root, shared)
    link, snapshot, _ = links[0]
    linked_to = Path(snapshot["target"]) if snapshot else None
    tracked = git(root, "ls-files", "--", *transaction.INSTALL_LINKS, transaction.LOCK,
                  transaction.RECOVERY, transaction.STATE)
    if tracked:
        fail(f"本机链接或安装元数据已纳入 Git: {tracked.decode('utf-8', errors='replace').strip()}")

    names = PROJECT_SKILLS | RETIRED_SKILLS | {"sdd-init"}
    conflicts = set()
    skill_root = transaction.safe_path(root, ".agents/skills")
    managed = {path for path, _, _ in links}
    # A project skill can be nested or declare a different name from its
    # directory. Preserve any linked entry that would need external inspection.
    pending = [skill_root] if skill_root.is_dir() else []
    while pending:
        for path in pending.pop().iterdir():
            if path in managed or path.name.startswith("."):
                continue
            if path.parent == skill_root and path.name.casefold() in names:
                conflicts.add(path)
            elif transaction.linked(path):
                if path.name.casefold() == "skill.md" or not path.is_file():
                    conflicts.add(path)
            elif path.is_dir():
                pending.append(path)
            elif path.name.casefold() == "skill.md":
                name = skill_name(path)
                if name and name.casefold() in names:
                    conflicts.add(path)
    agents = transaction.safe_path(root, ".codex/agents")
    if agents.exists() and not agents.is_dir():
        fail(f"角色目录被遮蔽: {agents}")
    for path in (agents.iterdir() if agents.is_dir() else ()):
        if path.suffix.casefold() != ".toml":
            continue
        if path.stem.casefold() in PROJECT_ROLES or transaction.linked(path):
            conflicts.add(path)
        elif path.is_file():
            try:
                name = tomllib.loads(read(path)).get("name")
            except ValueError:
                continue
            if isinstance(name, str) and name.casefold() in PROJECT_ROLES:
                conflicts.add(path)
    if conflicts:
        fail("项目中已有同名、旧入口或无法核对的 Skill／角色，请保留并处理后重新运行 init: "
             + ", ".join(sorted(path.relative_to(root).as_posix() for path in conflicts)))
    return link, linked_to


def read_state(data: bytes | None) -> dict:
    if data is None:
        return {}
    try:
        state = json.loads(data)
        if (not isinstance(state, dict) or set(state) != {"schema_version", "shared_version", "agents_blocks"}
                or state["schema_version"] != 1 or state["agents_blocks"].keys() != FRAGMENTS.keys()
                or not all(re.fullmatch(r"[a-f0-9]{64}", value)
                           for value in [state["shared_version"], *state["agents_blocks"].values()])):
            raise ValueError("Invalid project installation state")
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError(f"无效的项目安装元数据: {transaction.STATE}；请保留文件并核对来源") from error
    return state


def plan_files(root: Path, shared_version: str, fragments: dict[str, str]) -> list[tuple[Path, bytes, bytes | None]]:
    paths = [transaction.safe_path(root, name) for name in transaction.FILES]
    before = [transaction.content(path) for path in paths]
    old_state = read_state(before[3])
    texts = []
    for path, data in zip(paths[:3], before[:3]):
        try:
            texts.append((data or b"").decode("utf-8"))
        except UnicodeDecodeError as error:
            raise ValueError(f"文件不是有效 UTF-8: {path}") from error
    agents, config, ignore = texts
    state = {"schema_version": 1, "shared_version": shared_version,
             "agents_blocks": {name: release.digest(fragment.encode()) for name, fragment in fragments.items()}}
    proposed = (prepare_agents(agents, fragments, old_state.get("agents_blocks", {})),
                prepare_config(config), prepare_ignore(ignore), json.dumps(state, indent=2, sort_keys=True) + "\n")
    return [(path, data.encode("utf-8"), prior) for path, data, prior in zip(paths, proposed, before)]


def initialize(root: Path) -> int:
    shared = shared_path()
    link, _ = check_project(root, shared)
    links = transaction.plan_links(root, shared)
    version, shared_version, fragments = shared_bundle(shared)
    files = plan_files(root, shared_version, fragments)

    def check_bundle():
        if shared_path() != shared or shared_bundle(shared)[0] != version:
            fail(f"共享版本在预检后变化；请重新检查安装计划: {shared}")

    def guard():
        check_project(root, shared)
        if transaction.plan_links(root, shared) != links:
            fail(f"工作流链接在预检后变化: {link}")
        check_bundle()

    def verify():
        if check_project(root, shared)[1] != shared or not link.samefile(shared):
            fail(f"工作流链接不可用: {link}")
        for path, _, target in transaction.plan_links(root, shared):
            if target is None:
                if transaction.workflow_target(path) is not None:
                    fail(f"旧工作流链接尚未迁出: {path}")
            elif transaction.workflow_target(path) != target or not path.samefile(target):
                fail(f"工作流入口链接不可用: {path}")
        check_bundle()
        for target, data, _ in files:
            if transaction.content(inside(root, target)) != data:
                fail(f"安装写后核验检测到外部修改: {target}")
        config_dir = root / ".codex"
        for name in PROJECT_ROLES:
            reference = config_dir / role_reference(name)
            if not reference.samefile(shared / "agents" / f"{name}.toml"):
                fail(f"角色引用不可达: {name}")

    transaction.apply(root, files, links=links, guard=guard, verify=verify)
    for target, data, before in files:
        status = "ADDED" if before is None else "PRESERVED" if data == before else "UPDATED"
        out(f"{status} {target.relative_to(root).as_posix()}")
    for path, before, target in links:
        if target is not None or before is not None:
            status = "REMOVED" if target is None else "ADDED" if before is None else "PRESERVED"
            out(f"{status} {path.relative_to(root).as_posix()}")
    out(f"SDD WORKFLOW {link} -> {shared}")
    out(f"Shared version: sha256:{shared_version}")
    out(f"Project skills: {', '.join(sorted(PROJECT_SKILLS))}")
    out(f"Registered roles: {', '.join(sorted(PROJECT_ROLES))}")
    out("VERIFIED project anchor, six directory skill links, managed navigation, configuration and local metadata")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDD resource installer")
    p.add_argument("--root", default=".", help="要治理的仓库目录（默认当前目录）")
    subs = p.add_subparsers(dest="cmd", required=True)
    subs.add_parser("inspect", help="只读盘点，不修改任何文件")
    subs.add_parser("init", help="接入用户级共享资源并同步项目中的 SDD 托管块")
    subs.add_parser("recover", help="恢复未完成的项目安装操作")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = require_root(args.root)
        return {"inspect": cmd_inspect, "init": cmd_init, "recover": cmd_recover}[args.cmd](root, args)
    except (ValueError, OSError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
