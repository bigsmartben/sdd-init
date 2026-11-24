"""Build the user-level sdd-init skill and its repository assets."""
import argparse
import json
from pathlib import Path
import shutil
import tomllib

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("architect", "analyst", "implementer", "tester", "devops", "uat-observer")


def copilot_profile(source: Path) -> str:
    role = tomllib.loads(source.read_text("utf-8"))
    # JSON strings and lists are valid YAML frontmatter values.
    frontmatter = [
        "---",
        f'name: {json.dumps(role["name"])}',
        f'description: {json.dumps(role["description"], ensure_ascii=False)}',
        "include-custom-instructions: true",
    ]
    if role.get("sandbox_mode") == "read-only":
        frontmatter.append('tools: ["read", "search"]')
    frontmatter.extend(("---", "", role["developer_instructions"].strip(), ""))
    return "\n".join(frontmatter)


def build(output: Path) -> Path:
    output = output.resolve()
    for protected in (ROOT / "source", ROOT / "baselines"):
        if output.is_relative_to(protected):
            raise ValueError(f"Output overlaps maintained input: {output}")
    source = ROOT / "source/project/.codex"
    initializer = ROOT / "source/initializer"
    roles = {name: source / f"agents/{name}.toml" for name in ROLES}
    inputs = {
        "SKILL.md": initializer / "SKILL.md",
        "references/repository-onboarding.md": initializer / "references/repository-onboarding.md",
        "scripts/repository.py": ROOT / "src/sdd_init/repository.py",
        "assets/AGENTS.md": source / "agentsmd_template.md",
        **{f"assets/.codex/agents/{name}.toml": role for name, role in roles.items()},
    }
    for path in inputs.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    output.mkdir(parents=True, exist_ok=False)
    for name, path in inputs.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    copilot = output / "assets/.github/agents"
    copilot.mkdir(parents=True)
    for name, role in roles.items():
        (copilot / f"{name}.agent.md").write_text(copilot_profile(role), encoding="utf-8", newline="\n")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/sdd-init")
    print(build(parser.parse_args().output))
