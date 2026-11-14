"""Capture raw subprocess evidence and exit codes for independent integration."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
paths = ['src/order_service.py', 'src/storage.py', 'src/ui.py', 'checks/acceptance.py', 'specs/order/spec.md', 'docs/contracts/order.md', 'runtime.json', 'docs/test-reports/order-integration/contract_checks.py']
def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in paths}
before = hashes()
expected = '3148af600d21e5f6e56b3a2d91a49b19e4abcc129aa71e2e8f484db7d089bfbb'
if before['src/order_service.py'] != expected:
    raise SystemExit('Candidate hash mismatch; do not execute')
commands = [(case, [sys.executable, '-B', 'checks/acceptance.py', '--scenario', case]) for case in ('AC-1', 'AC-2', 'AC-3')]
commands += [('contracts', [sys.executable, '-B', 'docs/test-reports/order-integration/contract_checks.py']), ('runtime', [sys.executable, '-B', 'checks/runtime_details.py'])]
runs = []
for name, command in commands:
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (OUT / (name + '.stdout.txt')).write_text(result.stdout, encoding='utf-8')
    (OUT / (name + '.stderr.txt')).write_text(result.stderr, encoding='utf-8')
    runs.append(dict(name=name, command=command, timestamp_utc=started, exit_code=result.returncode, stdout=name+'.stdout.txt', stderr=name+'.stderr.txt'))
after = hashes()
record = dict(batch='order-integration-20261115', executor='/root/integration', cwd=str(ROOT), python=sys.version, executable=sys.executable, platform=platform.platform(), sqlite=sqlite3.sqlite_version, runtime=json.loads((ROOT/'runtime.json').read_text()), candidate_verified=before['src/order_service.py'] == expected, before_sha256=before, after_sha256=after, unchanged=before == after, runs=runs)
(OUT / 'execution.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(record, ensure_ascii=False, indent=2))
