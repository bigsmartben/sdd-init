"""Show the effective local instruction layers without calling a model or backend."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=("preview", "apply"))
parser.add_argument("--candidate", action="store_true", help="Assemble the candidate instead of the current prompt")
args = parser.parse_args()
root = Path(__file__).resolve().parent
config_file = root / ("prompt_layers.candidate.json" if args.candidate else "prompt_layers.json")
config = json.loads(config_file.read_text(encoding="utf-8"))
print(json.dumps([
    {"source": name, "text": (root / name).read_text(encoding="utf-8")}
    for name in [*config["common"], *config[args.mode]]
], ensure_ascii=False, indent=2))
