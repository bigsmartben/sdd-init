"""Verify a packaged CLI against a temporary home."""
import argparse
import re
from pathlib import Path
import subprocess
import tempfile
import tomllib


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="source", required=True)
    args = parser.parse_args()
    cli = ["uvx", "--from", args.source, "sdd-init"]
    with tempfile.TemporaryDirectory() as directory:
        home = Path(directory)
        for command in ("inspect", "install", "install", "inspect"):
            subprocess.run([*cli, command, "--home", directory], check=True)
            if command == "inspect" and not (home / ".codex").exists():
                assert not list(home.iterdir())
        assert (home / ".codex/AGENTS.md").is_file()
        roles = {p.stem: tomllib.loads(p.read_text("utf-8")) for p in (home / ".codex/agents").glob("*")}
        assert set(roles) == {"architect", "analyst", "implementer", "tester", "devops", "uat-observer"}
        expected = {".codex/AGENTS.md", *(f".codex/agents/{name}.toml" for name in roles)}
        assert {p.relative_to(home).as_posix() for p in home.rglob("*") if p.is_file()} == expected
        source = Path(__file__).resolve().parents[1] / "source/project"
        for name in expected:
            assert (home / name).read_text("utf-8") == (source / name).read_text("utf-8"), name
        for name, role in roles.items():
            assert role["name"] == name
            body = role["developer_instructions"]
            for section in ("工具参考（可选）", "正向交付", "逆向定位与验证", "交回条件"):
                assert re.search(rf"^{section}：\S.+$", body, re.MULTILINE), (name, section)
            assert "调用方" in body, name
            for other in (set(roles) - {name}) | {"Main"}:
                assert not re.search(rf"\b{re.escape(other)}\b", body, re.IGNORECASE), (name, other)
            print(f"Verified installed role: {name}")
        assert {name for name, role in roles.items() if role["sandbox_mode"] == "read-only"} == {"architect", "analyst"}


if __name__ == "__main__":
    main()
