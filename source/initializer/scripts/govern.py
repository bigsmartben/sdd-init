#!/usr/bin/env python3
"""Minimal Architecture + Spec + Status governance helper for Codex.

No external dependencies. Completion and commit are separate commands.
This tool verifies document structure, IDs and recorded snapshot freshness; it does
NOT determine whether an implementation actually meets architectural semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile
import tomllib

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
SLUG = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
AC = re.compile(r"\bAC-\d{3,}\b")
ARC = re.compile(r"\bARC-\d{3,}\b")
ROW = re.compile(r"^(\|\s*((?:AC|ARC)-\d{3,})\s*\|\s*)(PASS|FAIL|UNVERIFIED|STALE)(\s*\|\s*)([^|]*?)(\s*\|\s*)([^|]*?)(\s*\|\s*)$", re.M)
MARK_START = "<!-- sdd-contract-governance:start -->"
BAD_WORDS = ("（待补充", "（待明确", "（待定义", "TODO", "TBD")


def out(message: str) -> None:
    print(message)


def fail(message: str) -> None:
    raise ValueError(message)


def require_root(raw: str) -> Path:
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        fail(f"仓库目录不存在: {root}")
    return root


def require_name(name: str) -> str:
    if not SLUG.fullmatch(name):
        fail("能力名只能使用小写英文、数字、中横线；例如 payment-processing")
    return name


def inside(root: Path, dest: Path) -> Path:
    """Reject symlinked output directories that escape the selected repo."""
    resolved = dest.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        fail(f"拒绝仓库外路径: {dest} -> {resolved}")
    return dest


def paths(root: Path, name: str) -> tuple[Path, Path]:
    folder = root / "specs" / require_name(name)
    return inside(root, folder / "spec.md"), inside(root, folder / "status.md")


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def create(path: Path, data: str) -> bool:
    """Strictly create-only; never replaces existing files, including symlinks."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as f:
            f.write(data)
        out(f"CREATED {path}")
        return True
    except FileExistsError:
        out(f"KEEP    {path}")
        return False


def overwrite(path: Path, data: str) -> None:
    if path.is_symlink():
        fail(f"不覆盖符号链接: {path}")
    if not path.is_file():
        fail(f"文件不存在: {path}")
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(data)
    out(f"UPDATED {path}")


def blueprint_template() -> str:
    return read(ASSETS / "blueprint.md").replace(
        "../references/observability-baseline.md",
        "../.agents/sdd/references/observability-baseline.md")


def spec_template(name: str) -> str:
    return read(ASSETS / "spec.md").replace("{CAPABILITY}", name).replace(
        "../references/governance.md", "../../.agents/sdd/references/governance.md")


def ac_ids(spec: str) -> list[str]:
    ids = re.findall(r"^\|\s*(AC-\d{3,})\s*\|", spec, flags=re.M)
    return ids


def arc_refs(spec: str) -> list[str]:
    return sorted(set(ARC.findall(spec)))


def make_status(name: str, ids: list[str], arcs: list[str] | None = None,
                iteration: str = "-", state: str = "NOT_STARTED") -> str:
    rows = "\n".join(f"| {id_} | UNVERIFIED | - | - |" for id_ in ids)
    arch_rows = "\n".join(f"| {id_} | UNVERIFIED | - | - |" for id_ in (arcs or []))
    if not rows:
        rows = "（尚无有效 AC；待 Spec 确认后由实施迭代初始化验收记录）"
    if not arch_rows:
        arch_rows = "（当前规格未引用正式 ARC；如适用请在 Spec 中引用）"
    text = (read(ASSETS / "status.md")
            .replace("{CAPABILITY}", name).replace("{ROWS}", rows)
            .replace("{ARC_ROWS}", arch_rows))
    text = text.replace("- Iteration: -", f"- Iteration: {iteration}")
    text = text.replace("- State: NOT_STARTED", f"- State: {state}")
    return text


GATES = {"review": "Review", "test": "Test"}


def gate_info(text: str, gate: str) -> tuple[str, str, str]:
    prefix = GATES[gate]
    fields = []
    for field in ("Gate", "Evidence", "Snapshot"):
        match = re.search(rf"(?m)^- {prefix} {field}:\s*(.*?)\s*$", text)
        fields.append(match.group(1) if match else "MISSING")
    return tuple(fields)


def update_gate(text: str, gate: str, result: str, evidence: str, stamp: str) -> str:
    prefix = GATES[gate]
    for field, value in (("Gate", result), ("Evidence", evidence), ("Snapshot", stamp)):
        pattern = rf"(?m)^(- {prefix} {field}:)\s*.*$"
        if not re.search(pattern, text):
            fail(f"Status 缺失 {prefix} {field} 字段；请使用当前模板补齐")
        text = re.sub(pattern, lambda match: f"{match.group(1)} {value}", text, count=1)
    return text


def evidence_value(value: str) -> str:
    value = value.strip()
    if not value or "|" in value or "\n" in value or "\r" in value:
        fail("验收证据必须非空，不能包含换行或 Markdown 表格分隔符")
    return value


def state_of(text: str) -> str:
    m = re.search(r"(?m)^- State:\s*([A-Z_]+)\s*$", text)
    return m.group(1) if m else "INVALID"


def iteration_of(text: str) -> str:
    m = re.search(r"(?m)^- Iteration:\s*(.*?)\s*$", text)
    return m.group(1) if m else "-"


def status_rows(text: str) -> dict[str, tuple[str, str, str]]:
    result = {}
    for m in ROW.finditer(text):
        if m.group(2) in result:
            fail(f"status 存在重复验收项 {m.group(2)}")
        result[m.group(2)] = (m.group(3), m.group(5).strip(), m.group(7).strip())
    return result


def git(root: Path, *args: str) -> bytes | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=False)
        return r.stdout if r.returncode == 0 else None
    except FileNotFoundError:
        return None


def snapshot(root: Path) -> str | None:
    """Fingerprint the Git working-tree content, independent of HEAD identity.

    Read cached index object IDs for unchanged files, overlay dirty working-tree
    files and untracked files. Exclude runtime status and installed skill files.
    A commit with identical file content does NOT invalidate verified evidence.
    This is a conservative repository-wide snapshot, not a semantic test.
    """
    indexed = git(root, "ls-files", "--stage", "-z")
    dirty = git(root, "diff", "--name-only", "-z", "--")
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z")
    filemode = git(root, "config", "--bool", "core.filemode")
    trust_filemode = filemode is None or filemode.strip() != b"false"
    if indexed is None or dirty is None or untracked is None:
        return None

    def skip(name: str) -> bool:
        return (bool(re.fullmatch(r"specs/[^/]+/status\.md", name))
                or name.startswith(".agents/skills/") or name.startswith(".git/"))

    entries: dict[str, str] = {}
    for raw in indexed.split(b"\0"):
        if not raw:
            continue
        metadata, sep, raw_name = raw.partition(b"\t")
        if not sep:
            return None
        parts = metadata.split()
        if len(parts) != 3 or parts[2] != b"0":
            return None  # unresolved merge conflict
        name = raw_name.decode("utf-8", "surrogateescape")
        if not skip(name):
            entries[name] = parts[0].decode() + ":" + parts[1].decode()

    modified = {x.decode("utf-8", "surrogateescape") for x in
                (dirty + untracked).split(b"\0") if x}
    for name in modified:
        if skip(name):
            continue
        path = root / name
        if not path.exists() and not path.is_symlink():
            entries.pop(name, None)
            continue
        # git hash-object --path honors clean filters and works with SHA256 repos.
        blob = git(root, "hash-object", f"--path={name}", "--", name)
        if blob is None:
            return None
        if path.is_symlink():
            mode = "120000"
        elif not trust_filemode:
            # Windows and other filemode-insensitive filesystems use the index
            # mode; os.access(X_OK) does not describe Git's executable bit there.
            mode = entries.get(name, "100644:").partition(":")[0]
        else:
            mode = "100755" if os.access(path, os.X_OK) else "100644"
        entries[name] = mode + ":" + blob.decode().strip()

    h = hashlib.sha256()
    for name, identity in sorted(entries.items()):
        h.update(name.encode("utf-8", "surrogateescape") + b"\0")
        h.update(identity.encode() + b"\0")
    return h.hexdigest()[:20]


def git_checked(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(["git", "-C", str(root), *args],
                                capture_output=True, check=False)
    except FileNotFoundError:
        fail("缺少 Git，不能完成要求的迭代 Commit")
    if result.returncode != 0:
        fail(f"Git 命令失败: git {' '.join(args)}; {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def pending_paths(root: Path) -> set[str]:
    """Collect staged, unstaged and untracked paths; ignore ignored files."""
    raw = git_checked(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    names: set[str] = set()
    items = raw.split(b"\0")
    i = 0
    while i < len(items):
        item = items[i]
        i += 1
        if not item:
            continue
        status = item[:2]
        name = item[3:].decode("utf-8", "surrogateescape")
        names.add(name)
        if b"R" in status or b"C" in status:
            if i < len(items) and items[i]:
                names.add(items[i].decode("utf-8", "surrogateescape"))
            i += 1
    return names


def approved_paths(root: Path, requested: list[str]) -> set[str]:
    """Explicitly provided repository-relative files or folder prefixes."""
    approved: set[str] = set()
    for item in requested:
        item = item.strip().replace("\\", "/").rstrip("/")
        if not item or item == "." or Path(item).is_absolute() or ".." in Path(item).parts:
            fail(f"拒绝模糊或越界提交范围: {item!r}")
        if item == ".git" or item.startswith(".git/"):
            fail("不能将 .git 纳入提交范围")
        inside(root, root / item)
        approved.add(item)
    return approved


def within_scope(path: str, scope: set[str]) -> bool:
    return any(path == allowed or path.startswith(allowed + "/") for allowed in scope)



# `sdd-init` is the ONLY global skill. It carries a compressed payload that
# contains repository-local skills; storing nested SKILL.md files unpacked under
# ~/.agents/skills/sdd-init would risk discovering them as global skills.
PROJECT_PAYLOAD = ASSETS / "repo-payload.zip"
PROJECT_SKILLS = {'sdd-doc', 'sdd-imp', 'sdd-test-loop', 'sdd-review-loop', 'sdd-commit'}
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


def project_payload(root: Path, allow_update: bool) -> list[tuple[Path, bytes]]:
    if not PROJECT_PAYLOAD.is_file():
        fail("仅全局 sdd-init 能初始化仓库级 Skills；当前安装器缺少 repo-payload.zip")
    changes: list[tuple[Path, bytes]] = []
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
                        or (parts == (".agents", "skills", "sdd-commit", "references", "providers.md")))
            is_shared = (len(parts) == 4 and parts[0:2] == (".agents", "sdd")
                         and parts[2] in ("scripts", "assets") and parts[3] in
                         ("govern.py", "blueprint.md", "spec.md", "status.md", "architecture-rule-catalog.md",
                          "draft-pr.md", "prototype-reference.md", "acceptance.md",
                          "experiment.md", "sequence.md", "sequence-flows.md", "module-design.md", "contract.md", "test-plan.md"))
            is_shared = is_shared or (len(parts) == 4 and parts[:3] == (".agents", "sdd", "references")
                                      and parts[3] in ("delegation.md", "governance.md", "document-writing.md", "observability-baseline.md",
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
            is_project_default = member in ('.agents/governance/repository.md', 'docs/index.md')
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
            if target.exists() or target.is_symlink():
                if target.is_symlink() or not target.is_file():
                    fail(f"拒绝覆盖已有符号链接或非普通文件: {target}")
                # Project-owned navigation and rules are seeded once, even on upgrade.
                if is_project_default or target.read_bytes() == data:
                    continue
                if not allow_update:
                    fail(f"项目 Skill/角色/工具文件已被修改: {target}；请审查后使用 init --update-skills 执行明确升级")
            changes.append((target, data))
        found = {x for x in members if x.startswith('.agents/skills/') and x.endswith('/SKILL.md')}
        expected = {f'.agents/skills/{s}/SKILL.md' for s in PROJECT_SKILLS}
        if found != expected:
            fail("项目 Skill 包不包含完整的五个仓库级 Skill")
        required = {f'.agents/skills/{name}/agents/openai.yaml' for name in PROJECT_SKILLS}
        required.update(f'.codex/agents/{name}.toml' for name in PROJECT_ROLES)
        required.update({'.agents/sdd/references/visual-confirmation.md', '.agents/sdd/references/document-writing.md', '.agents/sdd/references/delegation.md', '.agents/sdd/references/governance.md',
                         '.agents/skills/sdd-commit/references/providers.md',
                         '.agents/sdd/references/observability-baseline.md',
                         '.agents/sdd/references/scenarios.md', '.agents/sdd/references/prototype.md',
                         '.agents/sdd/assets/spec.md', '.agents/sdd/assets/blueprint.md',
                         '.agents/sdd/assets/draft-pr.md', '.agents/sdd/assets/prototype-reference.md',
                         '.agents/sdd/assets/acceptance.md', '.agents/sdd/assets/experiment.md',
                         '.agents/sdd/assets/sequence.md', '.agents/sdd/assets/sequence-flows.md',
                         '.agents/sdd/assets/module-design.md', '.agents/sdd/assets/contract.md',
                         '.agents/sdd/assets/test-plan.md', '.agents/governance/repository.md', 'docs/index.md'})
        if not required.issubset(members):
            fail("项目包缺少角色、调用策略、模板或必要引用")
    return changes


def install_project_payload(root: Path, changes: list[tuple[Path, bytes]]) -> None:
    for target, data in changes:
        target.parent.mkdir(parents=True, exist_ok=True)
        exists = target.exists()
        target.write_bytes(data)
        out(f"{'UPDATED' if exists else 'CREATED'} {target}")


def cmd_inspect(root: Path, _: argparse.Namespace) -> int:
    out(f"Repository: {root}")
    for rel in ["AGENTS.md", "architecture/blueprint.md", "specs"]:
        out(f"{'EXISTS' if (root / rel).exists() else 'MISSING'}  {rel}")
    specs = sorted((root / "specs").glob("*/spec.md")) if (root / "specs").exists() else []
    for spec in specs:
        status = spec.with_name("status.md")
        out(f"CAPABILITY {spec.parent.name}: spec=present status={'present' if status.exists() else 'missing'}")
    candidates = [p for p in (root / "docs").rglob("*.md") if any(x in p.name.lower() for x in ("architecture", "design", "blueprint"))] if (root / "docs").is_dir() else []
    for p in candidates[:20]:
        out(f"POSSIBLE_EXISTING_ARCH {p.relative_to(root)} (请人工判断，禁止自动替换)")
    out(f"Git HEAD: {(git(root, 'rev-parse', '--short', 'HEAD') or b'none').decode().strip()}")
    out("这是只读盘点；初始化现有仓库前需先获得用户批准。")
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
    # Retired entrypoints must not silently coexist with the new workflow.
    retired = [root / ".agents/skills" / name for name in ("sdd-accept",)
               if (root / ".agents/skills" / name).exists()]
    retired.extend(root / ".codex/agents" / (name + ".toml")
                   for name in ("sdd-requirements", "sdd-architect", "sdd-planner", "sdd-implementer", "sdd-acceptor")
                   if (root / ".codex/agents" / (name + ".toml")).exists())
    if retired:
        fail("发现旧流程 Skill/角色，请在单独迁移范围内处理后再安装：" + ", ".join(str(p) for p in retired))
    # Preflight local skill conflicts BEFORE touching the repo.
    skill_changes = project_payload(root, args.update_skills)
    override = inside(root, root / "AGENTS.override.md")
    if override.exists() or override.is_symlink():
        fail("根目录存在 AGENTS.override.md；请先处理覆盖关系再初始化，避免治理规则未生效")
    agents = inside(root, root / "AGENTS.md")
    if agents.is_symlink() or (agents.exists() and not agents.is_file()):
        fail("拒绝覆盖 AGENTS.md 符号链接或非普通文件")
    original = agents.read_bytes().decode("utf-8") if agents.exists() else ""
    candidate = prepare_agents(original, args.update_skills)
    if candidate != original:
        agents.write_bytes(candidate.encode("utf-8"))
        out("UPDATED AGENTS.md" if original else "CREATED AGENTS.md")
    else:
        out("KEEP    AGENTS.md")
    install_project_payload(root, skill_changes)
    out("已安装五个项目 Skills、五个独立角色及其默认模型、共享模板与导航；保留既有正文和用户运行配置，不创建需求、架构或状态实体，不设置角色推理强度。安装不代表人工验收通过。")
    return 0


def cmd_start(root: Path, args: argparse.Namespace) -> int:
    name = require_name(args.name)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", args.iteration):
        fail("迭代编号仅允许英文、数字、点、下划线、中横线")
    spec, status = paths(root, name)
    original = read(status)
    state = state_of(original)
    if state == "IN_PROGRESS":
        if iteration_of(original) == args.iteration:
            out("已在本迭代执行，保留当前所有证据；不重置")
            return 0
        fail(f"已有执行中迭代 {iteration_of(original)}；需先处理/结束，不自动覆盖")
    if state not in ("NOT_STARTED", "COMPLETED", "BLOCKED"):
        fail(f"不支持重置状态 {state}")
    # BLOCKED reset is explicit and discards only previous runtime checkpoint.
    data = make_status(name, ac_ids(read(spec)), arc_refs(read(spec)), args.iteration, "IN_PROGRESS")
    branch_raw = git(root, "branch", "--show-current")
    if branch_raw and branch_raw.strip():
        data = data.replace("- Branch: -", "- Branch: " + branch_raw.decode("utf-8", "replace").strip(), 1)
    overwrite(status, data)
    out("新迭代已启动；旧状态由 Git/PR 保留（如需）；Spec 不变。")
    return 0


def cmd_record(root: Path, args: argparse.Namespace) -> int:
    name = require_name(args.name)
    spec, status = paths(root, name)
    item = args.ac if args.ac is not None else args.arc
    valid = ac_ids(read(spec)) if args.ac is not None else arc_refs(read(spec))
    if item not in valid:
        fail(f"契约项 {item} 不在当前 Spec 的有效 AC/ARC 引用中")
    original = read(status)
    if state_of(original) not in ("IN_PROGRESS", "COMPLETED"):
        fail("只有 IN_PROGRESS 或已完成迭代的显式复核可记录验收；先 start")
    if args.result in ("PASS", "FAIL"):
        evidence_value(args.evidence)
    stamp = snapshot(root)
    if args.result == "PASS" and not stamp:
        fail("当前仓库无 Git HEAD，无法绑定验证快照；请先建立 Git 基线")
    if args.result == "UNVERIFIED":
        evidence, stamp = "-", "-"
    else:
        evidence, stamp = args.evidence.strip(), stamp or "-"
    matches = 0

    def replace(m: re.Match) -> str:
        nonlocal matches
        if m.group(2) != item:
            return m.group(0)
        matches += 1
        return f"{m.group(1)}{args.result}{m.group(4)}{evidence}{m.group(6)}{stamp}{m.group(8)}"

    updated = ROW.sub(replace, original)
    if matches != 1:
        fail("Status 中未找到唯一对应 AC 行；请先核对 Spec/Status 结构")
    overwrite(status, updated)
    return 0


def cmd_attest(root: Path, args: argparse.Namespace) -> int:
    name = require_name(args.name)
    spec_path, status_path = paths(root, name)
    status = read(status_path)
    if state_of(status) not in ("IN_PROGRESS", "COMPLETED"):
        fail("只有 IN_PROGRESS 或 COMPLETED 的显式审查可登记 Loop Gate")
    stamp = snapshot(root)
    if args.result == "PASS" and not stamp:
        fail("当前无法建立 Git 内容快照，不能将 Gate 标记 PASS")
    evidence = evidence_value(args.evidence) if args.result != "UNVERIFIED" else "-"
    which = "ARC" if args.gate == "review" else "AC"
    wanted = arc_refs(read(spec_path)) if which == "ARC" else ac_ids(read(spec_path))
    rows = status_rows(status)
    if args.result == "PASS":
        for item in wanted:
            value = rows.get(item)
            if not value or value[0] != "PASS" or value[1] in ("-", "") or value[2] != stamp:
                fail(f"Gate 尚不能通过：{item} 缺少当前快照上的 PASS 证据")
        if args.gate == "review" and not wanted:
            out("NOTICE 当前 Spec 未关联 ARC；独立架构复核须确认不存在遗漏的适用全局约束")
    new_status = update_gate(status, args.gate, args.result, evidence, stamp or "-")
    overwrite(status_path, new_status)
    return 0


def validate(root: Path, name: str, strict: bool, require_gates: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    blueprint = root / "architecture" / "blueprint.md"
    if not blueprint.is_file():
        errors.append("缺少 architecture/blueprint.md")
        arch_data = ""
    else:
        arch_data = read(blueprint)
        if any(w in arch_data for w in BAD_WORDS):
            warnings.append("架构蓝图仍含待确认占位内容；不应宣称治理已完成")
    arch_ids = set(ARC.findall(arch_data))
    spec_path, status_path = paths(root, name)
    if not spec_path.is_file():
        errors.append(f"{name}: 缺少 spec.md")
        return errors, warnings
    spec = read(spec_path)
    if any(w in spec for w in BAD_WORDS):
        warnings.append(f"{name}: Spec 仍含待确认占位内容")
    expected = ac_ids(spec)
    if not expected:
        errors.append(f"{name}: 规格缺少 AC 验收表格")
    if len(expected) != len(set(expected)):
        errors.append(f"{name}: Spec 存在重复 AC 编号")
    refs = set(ARC.findall(spec))
    for ref in sorted(refs - arch_ids):
        errors.append(f"{name}: Spec 引用的 {ref} 在架构蓝图不存在")
    if not status_path.is_file():
        errors.append(f"{name}: 缺少 status.md")
        return errors, warnings
    status = read(status_path)
    try:
        rows = status_rows(status)
    except ValueError as e:
        errors.append(str(e))
        return errors, warnings
    if state_of(status) not in ("NOT_STARTED", "IN_PROGRESS", "BLOCKED", "COMPLETED"):
        errors.append(f"{name}: Status.State 无效")
    applicable_arcs = refs
    required = set(expected) | applicable_arcs
    for id_ in sorted(required - set(rows)):
        errors.append(f"{name}: Status 缺少 {id_}，需要对齐当前 Spec；不得继承旧 PASS")
    for id_ in sorted(set(rows) - required):
        errors.append(f"{name}: Status 含有过期 {id_}，需要对齐当前 Spec")
    current = snapshot(root)
    for id_, (result, evidence, verified) in sorted(rows.items()):
        if result == "PASS":
            if evidence in ("", "-"):
                errors.append(f"{name}/{id_}: PASS 没有验证证据")
            if not current or verified != current:
                warnings.append(f"{name}/{id_}: STALE，验证快照已改变或无法确认；需要重新验证")
        elif result != "PASS":
            warnings.append(f"{name}/{id_}: {result}，尚未通过验收")
    # Review/Test are explicitly invoked independent audits, not implicit imp steps.
    for gate, label in (("review", "架构审查"), ("test", "需求验收")):
        result, evidence, verified = gate_info(status, gate)
        if result == "MISSING":
            errors.append(f"{name}: 缺少 {label} Gate 字段，需要对齐最新版 Status 模板")
        elif result == "PASS":
            if evidence in ("", "-", "MISSING"):
                errors.append(f"{name}: {label} Gate PASS 缺少证据")
            if verified != current or not current:
                if require_gates:
                    warnings.append(f"{name}: {label} Gate STALE，需在最新代码快照上复核")
        elif result == "FAIL":
            # An actual observed failure must not be ignored simply because an
            # audit is not required for normal implementation completion.
            warnings.append(f"{name}: {label} Gate FAIL，已有显式审查失败待处理")
        elif result in ("UNVERIFIED", "STALE"):
            if require_gates:
                warnings.append(f"{name}: {label} Gate {result}，显式审查尚未通过")
        else:
            errors.append(f"{name}: {label} Gate 状态无效：{result}")
    if state_of(status) == "COMPLETED" and any(value[0] != "PASS" for value in rows.values()):
        errors.append(f"{name}: COMPLETED 却有未 PASS 的 AC/ARC")
    if require_gates and any(gate_info(status, gate)[0] != "PASS" for gate in GATES):
        warnings.append(f"{name}: 显式 Loop Gate 尚未全部 PASS")
    if strict and not arch_ids:
        warnings.append("架构蓝图未定义任何正式 ARC 约束 ID；请确认是否遗漏不变量")
    return errors, warnings


def cmd_check(root: Path, args: argparse.Namespace) -> int:
    names = list(dict.fromkeys(require_name(name) for name in args.name)) if args.name else sorted(p.parent.name for p in (root / "specs").glob("*/spec.md"))
    if not names:
        out("未发现 Spec；需求正文由 sdd-doc 按已确认内容写入。")
        return 1 if args.strict else 0
    errors, warnings = [], []
    for name in names:
        e, w = validate(root, name, args.strict, args.require_gates)
        errors += e
        warnings += w
    for message in errors:
        out(f"ERROR {message}")
    for message in warnings:
        out(f"WARN  {message}")
    out(f"Checked {len(names)} capability(s): {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (args.strict and warnings) else 0


def cmd_finish(root: Path, args: argparse.Namespace) -> int:
    """Verify completion evidence and persist Status."""
    name = require_name(args.name)
    _, status_path = paths(root, name)
    original = read(status_path)
    if state_of(original) != "IN_PROGRESS":
        fail("只有 IN_PROGRESS 的当前迭代可结束")
    errors, warnings = validate(root, name, True, False)
    if errors or warnings:
        for msg in errors + warnings:
            out(f"BLOCKED {msg}")
        fail("AC/ARC 实施验证或证据未达标，不能声明 COMPLETED")
    updated = original.replace("- State: IN_PROGRESS", "- State: COMPLETED", 1)
    overwrite(status_path, updated)
    out(f"COMPLETED {name}/{iteration_of(original)}: Status 已更新。")
    return 0


def cmd_commit(root: Path, args: argparse.Namespace) -> int:
    """Explicit-only commit; never invoked by finish or by implementation code."""
    name = require_name(args.name)
    spec_path, status_path = paths(root, name)
    current_status = read(status_path)
    if state_of(current_status) != "COMPLETED":
        fail("只有 Status=COMPLETED 的迭代可由用户显式提交；请先完成实现验收")
    iteration = iteration_of(current_status)
    if not iteration or iteration == "-":
        fail("缺少有效迭代编号")
    subject = f"sdd({name}): complete {iteration}"
    history = git(root, "log", "--format=%s", "HEAD")
    if history is None:
        fail("尚无有效 Git HEAD，不能提交")
    if subject in history.decode("utf-8", "replace").splitlines() or f"governance({name}): complete {iteration}" in history.decode("utf-8", "replace").splitlines():
        fail("本迭代已经提交过 Git Commit，拒绝重复提交")
    errors, warnings = validate(root, name, True, False)
    if errors or warnings:
        for msg in errors + warnings:
            out(f"BLOCKED {msg}")
        fail("证据不完整或当前代码快照已变化，不能 Commit")

    scope = approved_paths(root, args.include)
    scope.update({spec_path.relative_to(root).as_posix(), status_path.relative_to(root).as_posix()})
    all_pending = pending_paths(root)
    selected = sorted(path for path in all_pending if within_scope(path, scope))
    staged_raw = git_checked(root, "diff", "--cached", "--name-only", "-z")
    pre_staged = {x.decode("utf-8", "surrogateescape") for x in staged_raw.split(b"\0") if x}
    if pre_staged:
        fail("当前已有暂存区变更；请先审查并清空暂存区，避免误提交: " + ", ".join(sorted(pre_staged)))
    omitted = sorted(path for path in all_pending if not within_scope(path, scope))
    if omitted:
        fail("存在未批准范围内的仓库变更；请隔离后重新验证再提交: " + ", ".join(omitted[:20]))
    if not selected:
        fail("没有本轮可提交的变更；未创建空 Commit")
    try:
        git_checked(root, "add", "-A", "--", *selected)
        staged_actual_raw = git_checked(root, "diff", "--cached", "--name-only", "-z")
        staged_actual = {x.decode("utf-8", "surrogateescape") for x in staged_actual_raw.split(b"\0") if x}
        if staged_actual != set(selected) or any(not within_scope(x, scope) for x in staged_actual):
            fail("暂存文件集合与批准范围不一致")
        git_checked(root, "commit", "-m", subject)
    except ValueError:
        # Restore only the index. Working tree and COMPLETED status remain intact.
        git(root, "reset", "-q", "--", *selected)
        raise
    sha = git_checked(root, "rev-parse", "--short", "HEAD").decode().strip()
    out(f"COMMITTED {name}/{iteration}: {sha}；本次仅本地 Commit，无 Push/Merge/Publish。")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDD resource installer; legacy Spec/Status commands are not workflow gates")
    p.add_argument("--root", default=".", help="要治理的仓库目录（默认当前目录）")
    subs = p.add_subparsers(dest="cmd", required=True)
    subs.add_parser("inspect", help="只读盘点，不修改任何文件")
    a = subs.add_parser("init", help="安装 Skills、模板与 AGENTS 导航；不创建或回填项目实体，不修改用户配置")
    a.add_argument("--update-skills", action="store_true", help="经用户批准后替换已有仓库级 Skill/共享工具；绝不修改 Spec/Blueprint/Status")
    a = subs.add_parser("start", help="新迭代重置 Status，不影响 Spec")
    a.add_argument("--name", required=True)
    a.add_argument("--iteration", required=True)
    a = subs.add_parser("record", help="在真正完成验证后登记某个 AC/ARC 的证据与 Git 快照")
    a.add_argument("--name", required=True)
    id_group = a.add_mutually_exclusive_group(required=True)
    id_group.add_argument("--ac", help="本能力 Spec 的验收 ID")
    id_group.add_argument("--arc", help="本能力 Spec 引用的架构不变量 ID")
    a.add_argument("--result", choices=["PASS", "FAIL", "UNVERIFIED"], required=True)
    a.add_argument("--evidence", default="")
    a = subs.add_parser("attest", help="存量 Status 证据登记，不代表新流程人工验收通过")
    a.add_argument("--name", required=True)
    a.add_argument("--gate", choices=["review", "test"], required=True)
    a.add_argument("--result", choices=["PASS", "FAIL", "UNVERIFIED"], required=True)
    a.add_argument("--evidence", default="")
    a = subs.add_parser("check", help="检查 SSOT 链接、Status AC/ARC 和证据快照新鲜度")
    a.add_argument("--name", action="append", help="指定能力名；可重复指定以批量检查多个 Spec；缺省检查全部")
    a.add_argument("--strict", action="store_true", help="当前要求的验收未完成、快照失效或模板占位均视为失败")
    a.add_argument("--require-gates", action="store_true", help="显式要求 review/test 两个独立 Loop Gate 也 PASS（默认不要求）")
    a = subs.add_parser("finish", help="完成验收后更新 Status")
    a.add_argument("--name", required=True)
    a = subs.add_parser("commit", help="交付本轮已完成的需求变更")
    a.add_argument("--name", required=True)
    a.add_argument("--include", action="append", default=[], help="本轮确认的相对路径，可重复；自动包含 Spec 与 Status")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = require_root(args.root)
        if args.cmd not in ("init", "inspect"):
            out("本命令处理 Spec/Status 记录，不替代实际验证。")
        return {
            "inspect": cmd_inspect,
            "init": cmd_init,
            "start": cmd_start,
            "record": cmd_record,
            "attest": cmd_attest,
            "check": cmd_check,
            "finish": cmd_finish,
            "commit": cmd_commit,
        }[args.cmd](root, args)
    except (ValueError, OSError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
