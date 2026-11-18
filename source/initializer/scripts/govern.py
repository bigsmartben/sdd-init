#!/usr/bin/env python3
"""Install project SDD resources; no Spec/Status mutation commands."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import unquote

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
PROJECT_ROLES = set(transaction.PROJECT_ROLES)
RETIRED_SKILLS = {
    "sdd-spec", "sdd-imp", "sdd-review-code", "sdd-review-loop", "sdd-review-prompt",
    "sdd-doc", "sdd-commit", "sdd-deploy",
}
RETIRED_ROLES = {"sdd-delivery", "sdd-designer", "sdd-documenter", "sdd-validator"}
FRAGMENTS = {"sdd-contract-governance": "agents-fragment.md"}
# LF-normalized hashes of the unmarked Copilot adapters shipped in v0.8.5.
LEGACY_COPILOT_DIGESTS = {
    "review-prompt": "eeb09087ab37b2674898f66364d270803ae99e6b809dc2599c3e03ecba57d838",
    "sdd-architect": "e29b6aad2e1af3af1539122ed6c821f4edb7f1960f88153d767995541e064b8f",
    "sdd-coder": "a1a1de56d2024ed5f4e2e2035825284d06f3c76336df4c5c8ef83e752117326d",
    "sdd-devops": "2fe274a93de5666ebc4a0f3084a9af77e0f12bfb0ed3d7b1451d39b7edd85d97",
    "sdd-doc-consistency": "5eeb26b09c70b52530a7d5642e1843a96d8948a6edb8ce6d3528323c1ff6c03e",
    "sdd-product-manager": "7d75f7a8de736cf48662e2959de2e7f51f9bd3597209fc8a4e36ca34b08131f9",
}
COPILOT_OWNERSHIP = re.compile(rb"(?m)^<!-- sdd-init managed role ([a-z0-9-]+) sha256:([0-9a-f]{64}) -->\n\Z")


def validate_role(data: bytes, name: str) -> None:
    """Validate the shared role contract before any target write."""
    try:
        role = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        fail(f"角色 {name} 配置无效: {exc}")
    fields = {"name", "description", "developer_instructions"}
    if set(role) != fields:
        fail(f"角色 {name} 的字段必须为: {', '.join(sorted(fields))}")
    if role["name"] != name:
        fail(f"角色文件与 name 不一致: {name}")
    if any(not isinstance(value, str) or not value.strip() for value in role.values()):
        fail(f"角色 {name} 字段必须是非空文本")


def skill_name(path: Path, *, follow_link: bool = False) -> str | None:
    text = path.read_text(encoding="utf-8") if follow_link else read(path)
    name = re.search(r"""(?m)^name:[ \t]*(["']?)([\w-]+)\1[ \t]*(?:#[^\n]*)?$""", frontmatter(text))
    return name[2] if name else None


def frontmatter(text: str) -> str:
    match = re.match(r"\A\ufeff?---\n(.+?)\n---(?:\n|$)", text, re.DOTALL)
    return match[1] if match else ""


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
    roles = {name for name in actual if name.startswith("roles/codex/") and name.endswith(".toml")}
    copilot_roles = {
        name for name in actual if name.startswith("roles/copilot/") and name.endswith(".agent.md")
    }
    required = {
        "sdd/scripts/govern.py", "sdd/scripts/doc_check.py",
        *(f"agents/{name}.toml" for name in PROJECT_ROLES),
        *(f"roles/shared/{name}.md" for name in PROJECT_ROLES),
        *(f"roles/copilot/{name}.agent.md" for name in PROJECT_ROLES),
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
            or roles != {f"roles/codex/{name}.toml" for name in PROJECT_ROLES}
            or copilot_roles != {f"roles/copilot/{name}.agent.md" for name in PROJECT_ROLES}
            or not required <= actual.keys()):
        fail("共享资源缺少或包含未声明的 Skill、角色、模板或必要引用")
    for name in sorted(PROJECT_ROLES):
        data = (shared / "roles/codex" / f"{name}.toml").read_bytes()
        validate_role(data, name)
        validate_role((shared / "agents" / f"{name}.toml").read_bytes(), name)
        contract = read(shared / "roles/shared" / f"{name}.md")
        if not contract.strip():
            fail(f"共享角色正文为空: {name}")
        copilot = read(shared / "roles/copilot" / f"{name}.agent.md")
        if skill_name(shared / "roles/copilot" / f"{name}.agent.md") != name:
            fail(f"Copilot 角色 name 与分发文件不一致: {name}")
        if re.search(r"(?m)^(model|reasoning-effort)[ \t]*:", copilot):
            fail(f"Copilot 角色不得预设模型或推理强度: {name}")
        if re.findall(r"(?m)^target[ \t]*:[ \t]*(.*)$", frontmatter(copilot)) != ["vscode"]:
            fail(f"Copilot 角色必须限定在本地 VS Code 会话（target: vscode）: {name}")
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


def detect_project_harnesses(root: Path) -> dict[str, list[str]]:
    detected: dict[str, list[str]] = {"codex": [], "copilot": []}
    codex_config = root / ".codex/config.toml"
    codex_agents = root / ".codex/agents"
    if codex_config.exists():
        detected["codex"].append(".codex/config.toml")
    if codex_agents.is_dir() and any(codex_agents.glob("*.toml")):
        detected["codex"].append(".codex/agents/*.toml")
    copilot_instructions = root / ".github/copilot-instructions.md"
    copilot_agents = root / ".github/agents"
    if copilot_instructions.is_file():
        detected["copilot"].append(".github/copilot-instructions.md")
    if copilot_agents.is_dir() and any(copilot_agents.glob("*.agent.md")):
        detected["copilot"].append(".github/agents/*.agent.md")
    return detected


def selected_harnesses(root: Path, requested: str) -> tuple[dict[str, list[str]], set[str]]:
    detected = detect_project_harnesses(root)
    if requested in ("auto", "both"):
        return detected, {"codex", "copilot"}
    return detected, {requested}


def role_path(base: Path, reference: str) -> Path:
    # Keep the project link in the path so preflight can match paths it will replace.
    reference = reference.replace("\\", "/")
    if os.name == "nt":
        if reference[:8].casefold() == "//?/unc/":
            reference = "//" + reference[8:]
        elif re.match(r"^//\?/[A-Za-z]:/", reference):
            reference = reference[4:]
    return Path(os.path.abspath(base / reference))


def codex_config(root: Path) -> tuple[Path, str, dict]:
    path = transaction.safe_path(root, ".codex/config.toml")
    original = read(path) if path.exists() else ""
    try:
        agents = tomllib.loads(original).get("agents", {})
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 无法核对角色迁移依赖: {error}")
    return path, original, agents if isinstance(agents, dict) else {}


def codex_references(roles: dict, base: Path) -> dict[str, Path]:
    return {name: role_path(base, role["config_file"]) for name, role in roles.items()
            if isinstance(role, dict) and isinstance(role.get("config_file"), str) and role["config_file"]}


def inspect_project_roles(root: Path) -> None:
    config_path, _, roles = codex_config(root)
    references = codex_references(roles, config_path.parent)
    codex = {name for name, path in references.items() if name in PROJECT_ROLES and path.is_file()}
    missing = (PROJECT_ROLES & references.keys()) - codex
    copilot = {name for name in PROJECT_ROLES
               if (root / ".github/agents" / f"{name}.agent.md").is_file()}
    out(f"Installed roles (codex): {', '.join(sorted(codex)) or 'none'}")
    out(f"Installed roles (copilot): {', '.join(sorted(copilot)) or 'none'}")
    if missing:
        out(f"Unresolved role files (codex): {', '.join(sorted(missing))}")


def cmd_inspect(root: Path, args: argparse.Namespace) -> int:
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
    detected, harnesses = selected_harnesses(root, args.harness)
    out(f"Detected harness markers: " + "; ".join(
        f"{name}={', '.join(markers) if markers else 'none'}" for name, markers in detected.items()))
    out(f"Harness adapters planned: {', '.join(sorted(harnesses))}")
    inspect_project_roles(root)
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
    links = plan_project_links(root, shared, harnesses)
    link, existing, _ = links[0]
    description = (existing["target"] or "(existing file or directory)") if existing else "(missing)"
    out(f"Project link: {link} -> {description}")
    for path, before, target in links:
        out(f"Project entry: {path.relative_to(root).as_posix()} -> "
            f"{(before['target'] or '(existing file or directory)') if before else '(missing)'}"
            + (" (remove on init)" if target is None and before else ""))
    files, current = plan_files(root, version, fragments, harnesses)
    out(f"Project recorded shared version: {current.get('shared_version', 'none')}")
    doc_index = root / "docs/index.md"
    out(f"Project documentation index: {doc_index}" if doc_index.is_file()
        else "Project documentation index: resolve the project's own entry from its guidance")
    changes = [path.relative_to(root).as_posix() for path, data, before in files if data != before]
    changes.extend(path.relative_to(root).as_posix() for path, before, target in links
                   if not transaction.link_is_current(before, target))
    out(f"Project changes on init: {', '.join(changes) or 'none'}")
    if not pending:
        out("Next: run init to apply the project plan" if changes
            else "Project connection is current")
    return 0


def prepare_agents(original: str, templates: dict[str, str]) -> str:
    """Inject the Main block without changing project-owned bytes."""
    bom = "\ufeff" if original.startswith("\ufeff") else ""
    original = original[len(bom):]
    spans = []
    for name in (*FRAGMENTS, "agent-communication"):
        opening, closing = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
        starts = list(re.finditer(rf"(?m)^{re.escape(opening)}\r?$", original))
        ends = list(re.finditer(rf"(?m)^{re.escape(closing)}\r?$", original))
        if (len(starts) != len(ends) or original.count(f"<!-- {name}:") != len(starts) + len(ends)
                or len(starts) != original.count(opening) or len(ends) != original.count(closing)):
            fail("AGENTS.md 治理片段不完整或重复")
        for start, end in zip(starts, ends):
            if end.start() <= start.start():
                fail("AGENTS.md 治理片段顺序错误")
            spans.append((start.start(), end.start() + len(closing), name))
    spans.sort()
    if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
        fail("AGENTS.md 治理片段嵌套或重叠，无法确定覆盖范围")
    newline = "\r\n" if "\r\n" in original else "\n"
    parts, previous, installed = [], 0, False
    for begin, end, name in spans:
        parts.append(original[previous:begin])
        if name == "sdd-contract-governance" and not installed:
            parts.append(templates[name].replace("\n", newline))
            installed = True
        previous = end
    parts.append(original[previous:])
    body = "".join(parts)
    if not installed:
        if not body:
            body = "# Project Agent Guidance" + newline + newline
        elif not body.endswith(newline + newline):
            body += newline + newline
        body += templates["sdd-contract-governance"].replace("\n", newline) + newline
    return bom + body


def cmd_init(root: Path, args: argparse.Namespace) -> int:
    with transaction.project_lock(root):
        transaction.recover(root)
        _, harnesses = selected_harnesses(root, args.harness)
        with release.user_lock(SKILL.parent, shared_read=True):
            return initialize(root, harnesses)


def cmd_recover(root: Path, _: argparse.Namespace) -> int:
    with transaction.project_lock(root):
        if not transaction.recover(root):
            out(f"No pending project recovery: {root}")
    return 0


def role_reference(name: str) -> str:
    return f"../{transaction.WORKFLOW_LINK}/roles/codex/{name}.toml"


def legacy_role_reference(name: str) -> str:
    return f"../{transaction.LEGACY_WORKFLOW_LINK}/agents/{name}.toml"


def assignment_end(lines: list[str], index: int) -> int:
    line = lines[index]
    quoted, escaped, offset = None, False, 0
    for offset, char in enumerate(line):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\" and quoted == '"':
                escaped = True
            elif char == quoted:
                quoted = None
        elif char in ("'", '"'):
            quoted = char
        elif char == "=":
            break
    else:
        fail(".codex/config.toml 的角色配置无法安全定位")
    value = line[offset + 1:]
    while True:
        try:
            tomllib.loads("value = " + value)
        except tomllib.TOMLDecodeError as error:
            index += 1
            if index >= len(lines):
                raise ValueError(f".codex/config.toml 的角色配置无法安全定位: {error}") from error
            value += lines[index]
        else:
            return index + 1


def remove_conflicting_role_sections(original: str, role_names: set[str] | None = None) -> str:
    """Remove same-name role tables while preserving unrelated TOML text."""
    role_names = PROJECT_ROLES if role_names is None else role_names
    if not role_names:
        return original
    names = "|".join(re.escape(name) for name in sorted(role_names))
    target = re.compile(rf"^\s*\[\[?\s*agents\s*\.\s*(?:({names})|\"({names})\"|'({names})')(?=\s*[.\]])")
    header = re.compile(r"^\s*\[\[?[^\]\r\n]+\]\]?\s*(?:#.*)?$")
    agents_header = re.compile(r"^\s*\[\s*(?:agents|\"agents\"|'agents')\s*\]\s*(?:#.*)?$")
    inline = re.compile(rf"^\s*(?:({names})|\"({names})\"|'({names})')\s*(?:\.|=)")
    dotted = re.compile(rf"^\s*(?:agents|\"agents\"|'agents')\s*\.\s*"
                        rf"(?:({names})|\"({names})\"|'({names})')\s*(?:\.|=)")
    in_target = in_agents = False
    at_root = True
    result, lines, index = [], original.splitlines(keepends=True), 0
    while index < len(lines):
        line = lines[index]
        if header.match(line.rstrip("\r\n")):
            in_target = bool(target.match(line))
            in_agents = bool(agents_header.match(line.rstrip("\r\n")))
            at_root = False
        if not in_target and ((in_agents and inline.match(line)) or (at_root and dotted.match(line))):
            index = assignment_end(lines, index)
            continue
        elif not in_target:
            result.append(line)
        index += 1
    return "".join(result)


def migrate_legacy_role_references(root: Path, original: str, config: dict) -> tuple[str, dict]:
    anchors = (root / transaction.LEGACY_WORKFLOW_LINK, root / transaction.WORKFLOW_LINK)
    current = f"../{transaction.WORKFLOW_LINK}/"
    expected = copy.deepcopy(config)
    replacements, removed = {}, set()
    for name, role in config.get("agents", {}).items():
        if name in PROJECT_ROLES:
            continue
        reference = role.get("config_file") if isinstance(role, dict) else None
        if not isinstance(reference, str):
            continue
        path = role_path(root / ".codex", reference)
        anchor = next((anchor for anchor in anchors if path.is_relative_to(anchor)), None)
        if anchor is None:
            continue
        original_suffix = suffix = path.relative_to(anchor).as_posix()
        if suffix.startswith("agents/") and suffix.endswith(".toml"):
            codex_adapter = "roles/codex/" + suffix.removeprefix("agents/")
            if (shared_path() / codex_adapter).is_file():
                suffix = codex_adapter
        destination = (shared_path() / suffix).resolve()
        if not destination.is_relative_to(shared_path().resolve()):
            fail(f"项目角色 {name} 的旧共享引用越界: {reference}")
        if not destination.is_file():
            removed.add(name)
            expected["agents"].pop(name)
            continue
        if anchor == anchors[1] and suffix == original_suffix:
            continue
        replacement = current + suffix
        if reference != replacement:
            replacements[reference] = replacement
            expected["agents"][name]["config_file"] = replacement
    if not replacements and not removed:
        return original, config
    original = remove_conflicting_role_sections(original, removed)
    pattern = re.compile(r'''(?m)^([^#\r\n]*?\bconfig_file[ \t]*=[ \t]*)("(?:[^"\\\r\n]|\\.)*"|'[^'\r\n]*')([^\r\n]*)(\r?)$''')
    def replace(match):
        value = tomllib.loads("path = " + match[2])["path"]
        replacement = replacements.get(value)
        if replacement is None:
            return match[0]
        literal = f"'{replacement}'" if match[2].startswith("'") and "'" not in replacement else json.dumps(
            replacement, ensure_ascii=False,
        )
        return match[1] + literal + match[3] + match[4]
    migrated = pattern.sub(replace, original)
    try:
        actual = tomllib.loads(migrated)
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 的旧角色引用无法迁移: {error}")
    if actual != expected:
        fail(".codex/config.toml 的旧角色引用无法安全定位")
    return migrated, actual


def replace_non_table_agents(original: str, config: dict) -> tuple[str, dict]:
    if isinstance(config.get("agents", {}), dict):
        return original, config
    root, result, lines, index = True, [], original.splitlines(keepends=True), 0
    assignment = re.compile(r'''^[ \t]*(?:agents|"agents"|'agents')[ \t]*=''')
    while index < len(lines):
        line = lines[index]
        if re.match(r"^[ \t]*\[", line):
            root = False
        if root and assignment.match(line):
            index = assignment_end(lines, index)
            continue
        result.append(line)
        index += 1
    remaining = "".join(result)
    expected = copy.deepcopy(config)
    expected.pop("agents")
    try:
        actual = tomllib.loads(remaining)
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 的 agents 配置无法安全替换: {error}")
    if actual != expected:
        fail(".codex/config.toml 的 agents 配置无法安全定位")
    return remaining, actual


def expand_inline_agents(original: str, config: dict) -> tuple[str, dict]:
    assignment = re.compile(r'''^[ \t]*(?:agents|"agents"|'agents')[ \t]*=[ \t]*\{''')
    header = re.compile(r"^[ \t]*\[\[?[^\]\r\n]+\]\]?[ \t]*(?:#.*)?$")
    lines, items, at_root = [], None, True
    for line in original.splitlines(keepends=True):
        if header.match(line.rstrip("\r\n")):
            at_root = False
        match = assignment.match(line) if at_root else None
        if not match:
            lines.append(line)
            continue
        start, index, stack, quote, escaped = match.end(), match.end(), ["}"], None, False
        parts = []
        while index < len(line):
            char = line[index]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\" and quote[0] == '"':
                    escaped = True
                elif line.startswith(quote, index):
                    index += len(quote) - 1
                    quote = None
            elif char in ("'", '"'):
                quote = char * 3 if line.startswith(char * 3, index) else char
                index += len(quote) - 1
            elif char in "{[":
                stack.append("}" if char == "{" else "]")
            elif char in "}]":
                if not stack or stack.pop() != char:
                    fail(".codex/config.toml 的 agents 内联表无法安全定位")
                if not stack:
                    if line[start:index].strip():
                        parts.append(line[start:index].strip())
                    suffix = line[index + 1:]
                    if suffix.strip() and not suffix.lstrip().startswith("#"):
                        fail(".codex/config.toml 的 agents 内联表尾部无效")
                    if suffix.lstrip().startswith("#"):
                        lines.append(suffix.lstrip())
                    items = parts
                    break
            elif char == "," and len(stack) == 1:
                parts.append(line[start:index].strip())
                start = index + 1
            index += 1
        if items is None:
            fail(".codex/config.toml 的 agents 内联表不完整")
    if items is None:
        return original, config
    newline = "\r\n" if "\r\n" in original else "\n"
    remaining = "".join(lines)
    if items:
        separator = (newline if remaining.endswith(("\r", "\n")) else newline * 2) if remaining else ""
        remaining += separator + "[agents]" + newline + newline.join(items) + newline
    try:
        actual = tomllib.loads(remaining)
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 的 agents 内联表无法安全展开: {error}")
    expected = copy.deepcopy(config)
    if not items and expected.get("agents") == {}:
        expected.pop("agents")
    if actual != expected:
        fail(".codex/config.toml 的 agents 内联表无法安全展开")
    return remaining, actual


def config_role_block(original: str) -> tuple[str, tuple[int, int] | None]:
    begin = "# sdd-init roles:start"
    end = "# sdd-init roles:end"
    markers = list(re.finditer(rf"(?m)^(?:{begin}|{end})\r?$", original))
    if not markers:
        return original, None
    if len(markers) != 2 or markers[0][0].rstrip("\r") != begin:
        fail(".codex/config.toml 的 SDD 角色引用块不完整、重复或顺序错误")
    first, last = markers[0].start(), markers[1].start() + len(end)
    return original[:first] + original[last:], (first, last)


def prepare_config(root: Path, original: str) -> str:
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
    remaining, span = config_role_block(original)
    if span:
        first, last = span
        candidate = original[:first] + block + original[last:]
    else:
        remaining = original
        separator = (newline if original.endswith(("\r", "\n")) else newline * 2) if original else ""
        candidate = original + separator + block + newline

    try:
        unmanaged = tomllib.loads(remaining)
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 无法合并 SDD 角色引用: {error}")
    original_remaining = remaining
    remaining, unmanaged = expand_inline_agents(remaining, unmanaged)
    migrated, unmanaged = replace_non_table_agents(remaining, unmanaged)
    for name in PROJECT_ROLES & unmanaged.get("agents", {}).keys():
        role = unmanaged["agents"][name]
        base = root / ".codex"
        references_to_shared = {role_path(base, reference) for reference in (
            role_reference(name), legacy_role_reference(name), f"../{transaction.WORKFLOW_LINK}/agents/{name}.toml",
        )}
        if (not isinstance(role, dict) or set(role) != {"config_file"}
                or not isinstance(role["config_file"], str)
                or role_path(base, role["config_file"]) not in references_to_shared):
            fail(f"非受管 Codex 角色注册冲突: {name}；保留 .codex/config.toml，未执行覆盖")
    migrated, unmanaged = migrate_legacy_role_references(root, migrated, unmanaged)
    has_conflicts = any(name in unmanaged.get("agents", {}) for name in PROJECT_ROLES)
    if has_conflicts or migrated != original_remaining:
        remaining = migrated
        remaining = remove_conflicting_role_sections(remaining)
        separator = (newline if remaining.endswith(("\r", "\n")) else newline * 2) if remaining else ""
        candidate = remaining + separator + block + newline
    try:
        merged = tomllib.loads(candidate)
    except tomllib.TOMLDecodeError as error:
        fail(f".codex/config.toml 无法覆盖同名 SDD 角色引用: {error}")
    for name, reference in references.items():
        if merged.get("agents", {}).get(name) != reference:
            fail(f".codex/config.toml 的 SDD 角色引用不可用: {name}")
        unmanaged.get("agents", {}).pop(name, None)
        merged["agents"].pop(name, None)
    for config in (unmanaged, merged):
        if config.get("agents") == {}:
            config.pop("agents")
    if unmanaged != merged:
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


def role_reference_will_break(reference: Path, links: list[tuple[Path, dict | None, Path | None]]) -> bool:
    return any(reference.is_relative_to(path) and (target is None or not (target / reference.relative_to(path)).is_file())
               for path, _, target in links)


def check_copilot_role_references(root: Path, shared: Path, links: list[tuple[Path, dict | None, Path | None]]) -> None:
    directory = root / ".github/agents"
    if not directory.is_dir() or transaction.linked(directory) or transaction.linked(directory.parent):
        return
    checker = load_tool(shared / "sdd/scripts/doc_check.py")
    for agent in sorted(directory.glob("*.md")):
        if not agent.is_file() or transaction.linked(agent):
            continue
        for line in agent.read_text(encoding="utf-8", errors="replace").splitlines():
            references = list(checker.inline_links(line))
            references.extend(re.findall(r"`([^`]+)`", line))
            for reference in references:
                if not reference or "://" in reference:
                    continue
                reference = unquote(reference.partition("#")[0])
                base = root if reference.replace("\\", "/").startswith(".agents/") else agent.parent
                if role_reference_will_break(role_path(base, reference), links):
                    fail(f"未选择 Copilot，但角色 {agent.name} 的引用将失效: {reference}；"
                         "请先迁移该引用，或使用 --harness both 刷新受管适配。未执行写入")


def plan_project_links(root: Path, shared: Path, harnesses: set[str]) -> list[tuple[Path, dict | None, Path | None]]:
    config_path, config_text, registrations = codex_config(root)
    links = transaction.plan_links(root, shared)
    names = PROJECT_SKILLS | RETIRED_SKILLS | {"sdd-init"}
    conflicts = set()
    skill_root = transaction.safe_path(root, ".agents/skills")
    managed = {path for path, _, _ in links}
    pending = [skill_root] if skill_root.is_dir() else []
    while pending:
        for path in pending.pop().iterdir():
            if path in managed or path.name.startswith("."):
                continue
            if path.parent == skill_root and path.name.casefold() in names:
                conflicts.add(path)
            elif transaction.linked(path):
                entry = path / "SKILL.md" if path.is_dir() else path
                if entry.name.casefold() == "skill.md" and entry.is_file():
                    name = skill_name(entry, follow_link=True)
                    if name and name.casefold() in names:
                        conflicts.add(path)
            elif path.is_dir():
                pending.append(path)
            elif path.name.casefold() == "skill.md":
                name = skill_name(path)
                if name and name.casefold() in names:
                    conflicts.add(path)
    if "codex" in harnesses:
        unmanaged_text, span = config_role_block(config_text)
        owned_roles = tomllib.loads(config_text[span[0]:span[1]]).get("agents", {}) if span else {}
        if not isinstance(owned_roles, dict):
            fail(".codex/config.toml 的托管角色不是配置表，无法核对归属")
        owned_files = {path for name, path in codex_references(owned_roles, config_path.parent).items()
                       if name in PROJECT_ROLES}
        unmanaged_roles = tomllib.loads(unmanaged_text).get("agents", {})
        unmanaged_files = set(codex_references(unmanaged_roles, config_path.parent).values()) if isinstance(
            unmanaged_roles, dict,
        ) else set()
        agents = transaction.safe_path(root, ".codex/agents")
        if agents.exists() and not agents.is_dir():
            fail(f"角色目录被遮蔽: {agents}")
        for path in (agents.iterdir() if agents.is_dir() else ()):
            if path.suffix.casefold() != ".toml":
                continue
            collision = path.stem.casefold() in PROJECT_ROLES
            if not collision and path.is_file() and not transaction.linked(path):
                try:
                    name = tomllib.loads(path.read_text(encoding="utf-8")).get("name")
                except ValueError:
                    continue
                collision = isinstance(name, str) and name.casefold() in PROJECT_ROLES
            if collision:
                relative = f"agents/{path.name}"
                if path not in owned_files or path in unmanaged_files:
                    fail(f"非受管 Codex 角色文件冲突: .codex/agents/{path.name}；保留原文件，未执行覆盖")
                conflicts.add(path)
    links.extend((path, transaction.link_snapshot(path), None) for path in sorted(conflicts))
    if "codex" not in harnesses:
        legacy = root / transaction.LEGACY_WORKFLOW_LINK
        old_role_dir = root / transaction.WORKFLOW_LINK / "agents"
        for name, reference in codex_references(registrations, config_path.parent).items():
            if (reference.is_relative_to(legacy) or reference.is_relative_to(old_role_dir)
                    or role_reference_will_break(reference, links)):
                fail(f"未选择 Codex，但角色 {name} 依赖待迁移的路径: {reference}；"
                     "请使用 --harness both 完成角色迁移，未执行写入")
    if "copilot" not in harnesses:
        check_copilot_role_references(root, shared, links)
    return links


def read_state(data: bytes | None) -> dict:
    if data is None:
        return {}
    try:
        state = json.loads(data)
        required = {"schema_version", "shared_version", "agents_blocks"}
        if (not isinstance(state, dict) or not required <= state.keys()
                or set(state) - required - {"copilot_roles", "copilot_adapters"}
                or state["schema_version"] != 1
                or set(state["agents_blocks"]) not in (set(FRAGMENTS), set(FRAGMENTS) | {"agent-communication"})
                or not all(re.fullmatch(r"[a-f0-9]{64}", value)
                           for value in [state["shared_version"], *state["agents_blocks"].values()])):
            raise ValueError("Invalid project installation state")
        roles = state.get("copilot_roles", {})
        if (not isinstance(roles, dict) or not set(roles) <= set(PROJECT_ROLES)
                or not all(re.fullmatch(r"[a-f0-9]{64}", value) for value in roles.values())):
            raise ValueError("Invalid Copilot role ownership metadata")
        adapters = state.get("copilot_adapters", [])
        if (not isinstance(adapters, list)
                or not all(isinstance(path, str) and path in transaction.COPILOT_ROLE_FILES for path in adapters)
                or len(adapters) != len(set(adapters))):
            raise ValueError("Invalid Copilot adapter ownership")
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError(f"无效的项目安装元数据: {transaction.STATE}") from error
    return state


def is_managed_copilot_adapter(name: str, data: bytes) -> bool:
    normalized = data.replace(b"\r\n", b"\n")
    marker = COPILOT_OWNERSHIP.search(normalized)
    if marker:
        return (marker[1].decode("ascii") == name
                and release.digest(normalized[:marker.start()]) == marker[2].decode("ascii"))
    return release.digest(normalized) == LEGACY_COPILOT_DIGESTS.get(name)


def plan_files(root: Path, shared_version: str, fragments: dict[str, str],
               harnesses: set[str]) -> tuple[list[tuple[Path, bytes, bytes | None]], dict]:
    names = ["AGENTS.md"]
    if "codex" in harnesses:
        names.append(".codex/config.toml")
    names.extend((".gitignore", transaction.STATE))
    paths = [transaction.safe_path(root, name) for name in names]
    before = [transaction.content(path) for path in paths]
    texts = []
    for path, data in zip(paths[:-1], before[:-1]):
        try:
            texts.append((data or b"").decode("utf-8"))
        except UnicodeDecodeError as error:
            raise ValueError(f"文件不是有效 UTF-8: {path}") from error
    try:
        current = read_state(before[-1])
    except ValueError as error:
        out(f"Project installation state will be replaced: {error}")
        current = {}
    owned = set(current.get("copilot_adapters", []))
    copilot_roles = dict(current.get("copilot_roles", {}))
    copilot_files = []
    if "copilot" in harnesses:
        shared = shared_path()
        for name in sorted(PROJECT_ROLES):
            source = shared / "roles/copilot" / f"{name}.agent.md"
            relative = f".github/agents/{name}.agent.md"
            target = transaction.safe_path(root, relative)
            desired, prior = source.read_bytes(), transaction.content(target)
            owned_digest = copilot_roles.get(name)
            if prior is not None:
                if prior == desired:
                    copilot_roles[name] = release.digest(desired)
                elif owned_digest is not None:
                    if release.digest(prior) != owned_digest:
                        fail(f"保留已修改的 Copilot 角色；归属校验失败: {relative}")
                elif relative not in owned and not is_managed_copilot_adapter(name, prior):
                    fail(f"非受管 Copilot 角色冲突: {relative}；保留原文件，未执行覆盖")
            copilot_files.append((target, desired, prior))
            copilot_roles[name] = release.digest(desired)
            owned.add(relative)
    agents = texts[0]
    offset = 1
    config = texts[offset] if "codex" in harnesses else None
    offset += "codex" in harnesses
    ignore = texts[offset]
    state = {"schema_version": 1, "shared_version": shared_version,
             "agents_blocks": {name: release.digest(fragment.encode()) for name, fragment in fragments.items()},
             "copilot_roles": copilot_roles}
    if owned:
        state["copilot_adapters"] = sorted(owned)
    proposed = [prepare_agents(agents, fragments)]
    if config is not None:
        proposed.append(prepare_config(root, config))
    proposed.extend((prepare_ignore(ignore), json.dumps(state, indent=2, sort_keys=True) + "\n"))
    files = [(path, data.encode("utf-8"), prior) for path, data, prior in zip(paths, proposed, before)]
    files.extend(copilot_files)
    override = transaction.safe_path(root, "AGENTS.override.md")
    previous = transaction.content(override)
    if previous is not None:
        try:
            data = previous.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(f"文件不是有效 UTF-8: {override}") from error
        files.append((override, prepare_agents(data, fragments).encode("utf-8"), previous))
    return files, current


def initialize(root: Path, harnesses: set[str]) -> int:
    shared = shared_path()
    config_path = transaction.safe_path(root, ".codex/config.toml")
    config_before = transaction.content(config_path)
    links = plan_project_links(root, shared, harnesses)
    link = links[0][0]
    version, shared_version, fragments = shared_bundle(shared)
    files, _ = plan_files(root, shared_version, fragments, harnesses)

    def check_bundle():
        if shared_path() != shared or shared_bundle(shared)[0] != version:
            fail(f"共享版本在预检后变化；请重新检查安装计划: {shared}")

    def guard():
        if transaction.content(config_path) != config_before:
            fail(f"File changed after preflight; preserve file: {config_path}")
        if plan_project_links(root, shared, harnesses) != links:
            fail(f"工作流链接在预检后变化: {link}")
        check_bundle()

    def verify():
        for path, _, target in plan_project_links(root, shared, harnesses):
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
        if "codex" in harnesses:
            for name in PROJECT_ROLES:
                reference = config_dir / role_reference(name)
                if not reference.samefile(shared / "roles/codex" / f"{name}.toml"):
                    fail(f"Codex 角色引用不可达: {name}")
        if "copilot" in harnesses:
            for name in PROJECT_ROLES:
                target = root / ".github/agents" / f"{name}.agent.md"
                if target.read_bytes() != (shared / "roles/copilot" / f"{name}.agent.md").read_bytes():
                    fail(f"Copilot 角色配置不可达: {name}")

    transaction.apply(root, files, links=links, guard=guard, verify=verify)
    for target, data, before in files:
        status = "ADDED" if before is None else "PRESERVED" if data == before else "UPDATED"
        out(f"{status} {target.relative_to(root).as_posix()}")
    for path, before, target in links:
        if target is not None or before is not None:
            status = ("REMOVED" if target is None else "ADDED" if before is None
                      else "PRESERVED" if transaction.link_is_current(before, target) else "UPDATED")
            out(f"{status} {path.relative_to(root).as_posix()}")
    out(f"SDD WORKFLOW {link} -> {shared}")
    out(f"Shared version: sha256:{shared_version}")
    out(f"Project skills: {', '.join(sorted(PROJECT_SKILLS))}")
    out(f"Configured harnesses: {', '.join(sorted(harnesses))}")
    out(f"Installed role names: {', '.join(sorted(PROJECT_ROLES))}")
    out("VERIFIED project anchor, six directory skill links, role adapters, managed navigation and local metadata")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDD resource installer")
    p.add_argument("--root", default=".", help="要治理的仓库目录（默认当前目录）")
    p.add_argument("--harness", choices=("auto", "both", "codex", "copilot"), default="auto",
                   help="要接入的 Harness；auto 默认准备 Codex 与 Copilot 双端")
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
