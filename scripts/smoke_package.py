"""Verify a packaged skill and both project adapters in temporary Git repositories."""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
import tomllib

ROLES = {"architect", "analyst", "implementer", "tester", "devops", "uat-observer"}


def run(command):
    result = subprocess.run(
        command, text=True, encoding="utf-8", capture_output=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode:
        raise RuntimeError(f"{command!r}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def connect(command, repo, harness):
    options = ["--repo", str(repo), "--harness", harness]
    plan = run([*command, "plan", *options])
    fingerprint = re.search(r"^Plan: ([a-f0-9]{64})$", plan, re.MULTILINE).group(1)
    changes = run([*command, "apply", *options, "--expect", fingerprint])
    assert "Configuration check passed" in run([*command, "check", *options])
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="source", required=True)
    args = parser.parse_args()
    cli = ["uvx", "--from", args.source, "sdd-init"]
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        home = root / "home"
        home.mkdir()
        inspect = [*cli, "inspect", "--home", str(home)]
        install = [*cli, "install", "--home", str(home)]
        assert "Missing:" in run(inspect)
        assert not list(home.iterdir())
        assert "Installing:" in run(install)
        assert "Installing:" not in run(install)
        assert "Status: current" in run(inspect)
        assert not (home / ".codex").exists()

        skill = home / ".agents/skills/sdd-init"
        main_rules = ".agents/sdd-init/main.md"
        expected = {"SKILL.md", "references/repository-onboarding.md", "scripts/repository.py",
                    "assets/AGENTS.md", f"assets/{main_rules}"}
        expected.update(f"assets/.codex/agents/{role}.toml" for role in ROLES)
        expected.update(f"assets/.github/agents/{role}.agent.md" for role in ROLES)
        assert {p.relative_to(skill).as_posix() for p in skill.rglob("*") if p.is_file()} == expected
        entry = (skill / "SKILL.md").read_text("utf-8")
        assert "name: sdd-init" in entry
        for link in re.findall(r"\]\(([^)]+)\)", entry):
            assert (skill / link).is_file(), link

        repo = root / "repository"
        repo.mkdir()
        run(["git", "init", "-q", str(repo)])
        installed = ["uv", "run", "--script", str(skill / "scripts/repository.py")]
        assert "Written: AGENTS.md" in connect(installed, repo, "codex")
        assert "Written:" not in connect(installed, repo, "codex")
        assert "Written: AGENTS.md" not in connect([*cli, "project"], repo, "copilot")
        assert "Written:" not in connect([*cli, "project"], repo, "copilot")
        assert (repo / "AGENTS.md").read_text("utf-8") == (skill / "assets/AGENTS.md").read_text("utf-8")
        assert (repo / main_rules).read_bytes() == (skill / "assets" / main_rules).read_bytes()
        assert f"]({main_rules})" in (repo / "AGENTS.md").read_text("utf-8")
        assert not (repo / ".github/workflows").exists()

        for name in sorted(ROLES):
            codex = f".codex/agents/{name}.toml"
            copilot = f".github/agents/{name}.agent.md"
            for profile in (codex, copilot):
                assert (repo / profile).read_bytes() == (skill / "assets" / profile).read_bytes()
            role = tomllib.loads((repo / codex).read_text("utf-8"))
            assert role["name"] == name
            body = role["developer_instructions"]
            for section in ("工具参考（可选）", "正向交付", "逆向定位与验证", "交回条件"):
                assert re.search(rf"^{section}：\S.+$", body, re.MULTILINE), (name, section)
            assert "调用方" in body, name
            assert (role.get("sandbox_mode") == "read-only") == (name in {"architect", "analyst"})
            profile = (repo / copilot).read_text("utf-8")
            assert body.strip() in profile
            for other in (ROLES - {name}) | {"Main"}:
                for rendered in ((repo / codex).read_text("utf-8"), profile):
                    assert not re.search(rf"\b{re.escape(other)}\b", rendered, re.IGNORECASE), (name, other)
            assert "include-custom-instructions: false" in profile
            assert "user-invocable: false" in profile
            tools = ["read", "search"]
            if name not in {"architect", "analyst"}:
                if name != "uat-observer":
                    tools.append("edit")
                tools.append("execute")
            assert f"tools: {json.dumps(tools)}" in profile
            print(f"Verified packaged and installed profiles: {name}")

        print("UVX bootstrap, installed Skill CLI, both repository adapters and repeat checks passed.")


if __name__ == "__main__":
    main()
