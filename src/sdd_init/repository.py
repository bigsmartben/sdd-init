# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Plan, apply, and check a repository's sdd-init configuration."""

import argparse
from dataclasses import dataclass, field
from difflib import unified_diff
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import NamedTemporaryFile
import tomllib

import yaml


ROLES = ("architect", "analyst", "implementer", "tester", "devops", "uat-observer")
PROFILES = {"codex": (".codex/agents", ".toml"), "copilot": (".github/agents", ".agent.md")}
BEGIN = b"<!-- sdd-init:main:start -->"
END = b"<!-- sdd-init:main:end -->"
MAIN_RULES = ".agents/sdd-init/main.md"
MAIN_RULES_MARKER = b"<!-- sdd-init:main-rules -->\n"
CI_SOURCE = re.compile(
    r"git\+https://[A-Za-z0-9._/-]+@[0-9a-fA-F]{40}|https://[A-Za-z0-9._/-]+\.whl"
)


def git_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", os.fspath(path), "rev-parse", "--show-toplevel"],
        capture_output=True, encoding="utf-8", errors="replace",
    )
    if result.returncode:
        raise ValueError(f"Cannot locate Git repository: {path}\n{result.stderr.strip()}")
    return Path(result.stdout.strip()).resolve(strict=True)


def target_path(root: Path, relative: str) -> Path:
    path = root / relative
    for item in [path, *path.parents]:
        if item == root:
            break
        if item.is_symlink() or getattr(item, "is_junction", lambda: False)():
            raise ValueError(f"Linked configuration path: {item}")
        if item != path and item.exists() and not item.is_dir():
            raise ValueError(f"Configuration parent is not a directory: {item}")
    if path.resolve() != path:
        raise ValueError(f"Redirected configuration path: {path}")
    return path


def read_target(root: Path, relative: str) -> bytes | None:
    try:
        return target_path(root, relative).read_bytes()
    except FileNotFoundError:
        return None


def content_digest(content: bytes | None) -> str | None:
    return None if content is None else hashlib.sha256(content).hexdigest()


def normalized(content: bytes) -> bytes:
    return content.removeprefix(b"\xef\xbb\xbf").replace(b"\r\n", b"\n")


def block_bounds(content: bytes) -> tuple[int, int] | None:
    parts = {}
    for marker in (BEGIN, END):
        matches = list(re.finditer(rb"(?m)^" + re.escape(marker) + rb"(?=\r?$)", content))
        if matches:
            parts[marker] = matches
    if not parts:
        return None
    if (set(parts) != {BEGIN, END} or any(len(matches) != 1 for matches in parts.values())
            or parts[BEGIN][0].start() >= parts[END][0].start()):
        raise ValueError("AGENTS.md has malformed or repeated sdd-init Main markers")
    return parts[BEGIN][0].start(), parts[END][0].end()


def ready(content: bytes | None, template: bytes) -> bool:
    if content is None:
        return False
    content = normalized(content)
    if content.rstrip(b"\n") == template.rstrip(b"\n"):
        return True
    bounds = block_bounds(content)
    return bool(bounds and content[slice(*bounds)] == main_block(template))


def main_block(template: bytes, newline: bytes = b"\n") -> bytes:
    return newline.join((BEGIN, template.rstrip(b"\n").replace(b"\n", newline), END))


def merge_rules(current: bytes, template: bytes) -> bytes:
    bom = b"\xef\xbb\xbf" if current.startswith(b"\xef\xbb\xbf") else b""
    body = current.removeprefix(bom)
    newline = b"\r\n" if b"\r\n" in body else b"\n"
    block = main_block(template, newline)
    bounds = block_bounds(body)
    if bounds:
        start, end = bounds
        return bom + body[:start] + block + body[end:]
    separator = b"" if not body or body.endswith(newline * 2) else newline
    if body and not body.endswith(newline):
        separator += newline
    return bom + body + separator + block + newline


def profile_name(harness: str, path: str, content: bytes) -> str:
    data = content.decode("utf-8-sig")
    if harness == "codex":
        profile = tomllib.loads(data)
        required = ("name", "description", "developer_instructions")
    else:
        lines = data.splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            raise ValueError(f"{path}: expected YAML frontmatter")
        end = lines.index("---", 1)
        try:
            profile = yaml.safe_load("\n".join(lines[1:end]))
        except yaml.YAMLError as error:
            raise ValueError(f"{path}: invalid YAML frontmatter: {error}") from error
        if not any(line.strip() for line in lines[end + 1:]):
            raise ValueError(f"{path}: empty prompt")
        required = ("description",)
    if not isinstance(profile, dict) or any(
        not isinstance(profile.get(key), str) or not profile[key].strip() for key in required
    ):
        raise ValueError(f"{path}: missing or invalid profile fields {', '.join(required)}")
    if harness == "copilot":
        name = Path(path).name.removesuffix(".md").removesuffix(".agent")
        if "name" in profile and profile["name"] != name:
            raise ValueError(f"{path}: display name must match role {name!r}")
        if name in ROLES:
            tools = profile.get("tools")
            allowed = {"read", "search"}
            if name not in {"architect", "analyst"}:
                allowed.add("execute")
                if name != "uat-observer":
                    allowed.add("edit")
            if (not isinstance(tools, list) or not tools
                    or any(not isinstance(tool, str) or tool not in allowed for tool in tools)):
                raise ValueError(f"{path}: expected an explicit role tool allowlist from {', '.join(sorted(allowed))}")
            if profile.get("include-custom-instructions") is not False or profile.get("user-invocable") is not False:
                raise ValueError(f"{path}: set include-custom-instructions and user-invocable to false")
        return name
    return profile["name"]


def profile_path(harness: str, name: str) -> str:
    folder, suffix = PROFILES[harness]
    return f"{folder}/{name}{suffix}"


def workflow(harness: str, source: str) -> bytes:
    if not CI_SOURCE.fullmatch(source):
        raise ValueError("CI source must be an HTTPS wheel URL or a git+https URL pinned to a full commit SHA")
    return f"""name: sdd-init ({harness})
on: [push, pull_request, workflow_dispatch]
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: astral-sh/setup-uv@v6
      - name: Check repository configuration
        env:
          SDD_INIT_SOURCE: {json.dumps(source)}
        run: uvx --from "$SDD_INIT_SOURCE" sdd-init project check --repo . --harness {harness}
""".encode()


@dataclass
class Plan:
    root: Path
    harness: str
    version: str
    before: dict[str, bytes | None] = field(default_factory=dict)
    changes: dict[str, bytes] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    status: dict[str, str] = field(default_factory=dict)
    alternatives: dict[str, bytes] = field(default_factory=dict)

    def read(self, path: str) -> bytes | None:
        self.before[path] = read_target(self.root, path)
        return self.before[path]

    def write(self, path: str, content: bytes) -> None:
        if self.before[path] != content:
            self.changes[path] = content

    def fingerprint(self) -> str:
        state = [str(self.root), self.harness, self.version,
                 {p: content_digest(data) for p, data in self.before.items()},
                 {p: content_digest(data) for p, data in self.changes.items()}]
        return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()


def plan_rules(plan: Plan, template: bytes, args) -> None:
    path = "AGENTS.md"
    current = plan.read(path)
    if current is not None:
        current.decode("utf-8-sig")
    if current is None:
        plan.status[path] = "create"
        plan.write(path, template)
        return
    managed = False
    try:
        normalized_current = normalized(current)
        managed = block_bounds(normalized_current) is not None
        current_ready = ready(current, template)
        if (not current_ready and not managed
                and re.search(rb"(?m)^# Main Agent(?:\s|$)", normalized_current)):
            raise ValueError("Existing Main heading has no managed block. Review a merge candidate or replace.")
        merged = merge_rules(current, template) if not current_ready else current
    except ValueError as error:
        current_ready = False
        merged = None
        plan.status[path] = str(error)
    if current_ready:
        plan.status[path] = "current"
    elif args.upgrade == "replace":
        plan.status[path] = "replace"
        plan.write(path, template)
    elif args.upgrade == "merge" and args.merged_file:
        approved = args.merged_file.read_bytes()
        approved.decode("utf-8-sig")
        if not block_bounds(normalized(approved)) or not ready(approved, template):
            raise ValueError("Reviewed merge must contain the current managed Main block")
        plan.status[path] = "reviewed merge"
        plan.write(path, approved)
    elif merged is not None and (managed or args.upgrade == "merge"):
        plan.status[path] = "update managed Main block in place" if managed else "merge"
        plan.write(path, merged)
    else:
        plan.status.setdefault(path, "awaiting upgrade choice")
        plan.blockers.append("Choose merge or replace after reviewing AGENTS.md differences")
        if merged is not None:
            plan.alternatives["merge"] = merged
        plan.alternatives["replace"] = template


def project_profiles(plan: Plan) -> dict[str, list[str]]:
    folder, suffix = PROFILES[plan.harness]
    directory = target_path(plan.root, folder)
    profiles = {name: [] for name in ROLES}
    for path in sorted(directory.rglob("*.md" if plan.harness == "copilot" else f"*{suffix}")):
        relative = path.relative_to(plan.root).as_posix()
        filename = path.name.removesuffix(".md").removesuffix(".agent") if plan.harness == "copilot" else path.stem
        if plan.harness == "copilot" and path.parent != directory:
            continue  # A nested profile has its own scoped identifier.
        try:
            content = plan.read(relative)
            if content is None:
                raise ValueError("Profile disappeared during inspection")
            role = profile_name(plan.harness, relative, content)
        except (ValueError, OSError) as error:
            if filename in profiles:
                profiles[filename].append(relative)
                plan.blockers.append(f"{relative}: {error}")
            continue
        if role in profiles:
            profiles[role].append(relative)
        elif filename in profiles:
            profiles[filename].append(relative)
            plan.blockers.append(f"{relative}: declares {role!r}, expected {filename!r}")
    return profiles


def handle_profiles(plan: Plan, assets: Path, reuse: list[str], check: bool) -> None:
    profiles = project_profiles(plan)
    for role, found in profiles.items():
        relative = profile_path(plan.harness, role)
        expected = (assets / relative).read_bytes()
        if profile_name(plan.harness, relative, expected) != role:
            raise ValueError(f"Invalid bundled role: {relative}")
        if not found:
            plan.read(relative)
            plan.status[relative] = "missing" if check else "create"
            if check:
                plan.blockers.append(f"Missing role: {role} ({relative})")
            else:
                plan.write(relative, expected)
            continue
        if len(found) > 1:
            plan.blockers.append(f"Multiple profiles for {role}: {', '.join(found)}")
        for path in found:
            actual = plan.before.get(path)
            if actual is not None and normalized(actual) == normalized(expected):
                plan.status[path] = f"{role}: current"
            elif check or role in reuse:
                plan.status[path] = f"{role}: existing custom profile"
            else:
                plan.status[path] = f"{role}: custom profile requires review"
                plan.alternatives[path] = expected
                plan.blockers.append(f"Review {path} and use --reuse-role {role} to keep an effective profile")


def make_plan(root: Path, assets: Path, args) -> Plan:
    template = normalized((assets / "AGENTS.md").read_bytes()).rstrip(b"\n") + b"\n"
    main_rules = normalized((assets / MAIN_RULES).read_bytes())
    if not main_rules.startswith(MAIN_RULES_MARKER) or MAIN_RULES.encode() not in template:
        raise ValueError("Bundled Main rules or entry is invalid")
    plan = Plan(root, args.harness, content_digest(main_rules))
    for name in ROLES:
        if not re.search(rb"(?m)^- \*\*" + name.encode() + rb"\*\*", main_rules):
            raise ValueError(f"Main route is missing role: {name}")
    checking = args.action == "check"
    if checking:
        if not ready(plan.read("AGENTS.md"), template):
            plan.blockers.append("AGENTS.md is missing the current Main rules")
        else:
            plan.status["AGENTS.md"] = "current"
    else:
        plan_rules(plan, template, args)
    current_rules = plan.read(MAIN_RULES)
    if current_rules is not None and normalized(current_rules) == main_rules:
        plan.status[MAIN_RULES] = "current"
    elif checking:
        plan.blockers.append(f"Missing or mismatched Main rules: {MAIN_RULES}")
    elif current_rules is None or normalized(current_rules).startswith(MAIN_RULES_MARKER):
        plan.status[MAIN_RULES] = "create" if current_rules is None else "update"
        plan.write(MAIN_RULES, main_rules)
    else:
        plan.blockers.append(f"Existing file conflicts with bundled Main rules: {MAIN_RULES}")
        plan.alternatives[MAIN_RULES] = main_rules
    other = "copilot" if args.harness == "codex" else "codex"
    other_folder = PROFILES[other][0]
    other_path = target_path(root, other_folder)
    plan.status[other_folder] = "present" if other_path.is_dir() else "absent"
    handle_profiles(plan, assets, args.reuse_role, checking)
    if args.ci_source:
        path = f".github/workflows/sdd-init-{args.harness}.yml"
        current = plan.read(path)
        expected = workflow(args.harness, args.ci_source)
        if current is not None and normalized(current) != normalized(expected):
            plan.blockers.append(f"Existing CI workflow requires manual integration: {path}")
            plan.alternatives[path] = expected
        elif current is None and checking:
            plan.blockers.append(f"Missing selected CI workflow: {path}")
        elif current is None:
            plan.write(path, expected)
            plan.status[path] = "create"
        else:
            plan.status[path] = "current"
    return plan


def show_diff(path: str, before: bytes | None, after: bytes, label: str = "") -> None:
    old = (before or b"").decode("utf-8-sig", errors="replace").splitlines()
    new = after.decode("utf-8-sig", errors="replace").splitlines()
    for line in unified_diff(old, new, f"{path} (current)", f"{path} ({label or 'proposed'})", lineterm=""):
        print(line)


def print_plan(plan: Plan) -> None:
    print(f"Repository: {plan.root}\nHarness: {plan.harness}\nMain template: sha256:{plan.version}")
    for path, status in plan.status.items():
        print(f"{path}: {status}")
    for path, content in plan.changes.items():
        show_diff(path, plan.before[path], content)
    for key, content in plan.alternatives.items():
        path = "AGENTS.md" if key in {"merge", "replace"} else key
        show_diff(path, plan.before.get(path), content, key if key != path else "bundled")
    for error in plan.blockers:
        print(f"Pending: {error}")


def write_change(plan: Plan, relative: str, content: bytes) -> None:
    target = target_path(plan.root, relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=target.parent, delete=False) as stream:
        stage = Path(stream.name)
    try:
        stage.write_bytes(content)
        existing = read_target(plan.root, relative)
        if existing != plan.before[relative]:
            raise ValueError(f"{relative} changed after preview. Inspect and replan.")
        if existing is None:
            os.link(stage, target)  # Fail if another process created it after the check.
        else:
            os.chmod(stage, target.stat().st_mode)
            os.replace(stage, target)
    finally:
        stage.unlink(missing_ok=True)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("action", choices=("plan", "apply", "check"))
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--harness", choices=tuple(PROFILES), required=True)
    parser.add_argument("--upgrade", choices=("merge", "replace"))
    parser.add_argument("--merged-file", type=Path, help="Reviewed complete merge candidate")
    parser.add_argument("--reuse-role", choices=ROLES, action="append", default=[])
    parser.add_argument("--ci-source", help="Selected UVX source for the GitHub Actions workflow")
    parser.add_argument("--expect", help="Fingerprint of the reviewed plan")


def run(assets: Path, args) -> int:
    if args.merged_file and args.upgrade != "merge":
        raise ValueError("--merged-file requires --upgrade merge")
    if args.action == "check" and (args.merged_file or args.upgrade or args.reuse_role or args.expect):
        raise ValueError("check accepts only repository, harness, and optional CI source")
    if args.action != "apply" and args.expect:
        raise ValueError("--expect is only valid with apply")
    root = git_root(args.repo)
    plan = make_plan(root, assets, args)
    if args.action != "apply" or plan.blockers:
        print_plan(plan)
    if plan.blockers:
        return 1
    if args.action == "plan":
        print(f"Plan: {plan.fingerprint()}")
    elif args.action == "apply":
        if args.expect != plan.fingerprint():
            raise ValueError("Missing or stale --expect. Review a new plan before writing.")
        for relative, content in plan.changes.items():
            write_change(plan, relative, content)
            print(f"Written: {relative}")
        print("Applied. Run check and verify native discovery and calls in the current host.")
    else:
        print("Configuration check passed. Native discovery and invocation are separate acceptance steps.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    try:
        sys.exit(run(Path(__file__).resolve().parents[1] / "assets", parser.parse_args()))
    except (OSError, ValueError) as error:
        sys.exit(f"sdd-init: {error}")
