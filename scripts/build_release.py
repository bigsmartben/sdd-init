"""Build the Codex collaboration bundle from the maintained source tree."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ".codex/AGENTS.md",
    ".codex/agents/architect.toml",
    ".codex/agents/analyst.toml",
    ".codex/agents/implementer.toml",
    ".codex/agents/devops.toml",
    ".codex/agents/tester.toml",
    ".codex/agents/uat-observer.toml",
)


def build(output: Path) -> Path:
    output = output.resolve()
    for protected in (ROOT / "source", ROOT / "baselines"):
        if output.is_relative_to(protected):
            raise ValueError(f"Output overlaps maintained input: {output}")
    source = ROOT / "source/project"
    for name in FILES:
        if not (source / name).is_file():
            raise FileNotFoundError(source / name)
    output.mkdir(parents=True, exist_ok=False)
    for name in FILES:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/sdd-init")
    print(build(parser.parse_args().output))
