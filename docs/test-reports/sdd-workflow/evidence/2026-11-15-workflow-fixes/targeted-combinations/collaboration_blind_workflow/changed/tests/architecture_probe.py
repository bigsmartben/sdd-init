"""Architecture evidence only; temporary file databases, no network or product edits."""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage, ui


def hashes():
    paths = sorted((ROOT / "src").glob("*.py"))
    paths += sorted((ROOT / "checks").glob("*.py"))
    paths += [ROOT / "runtime.json", ROOT / "tests/test_order.py", Path(__file__).resolve()]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


before = hashes()
candidate = json.loads((ROOT / "docs/test-reports/order/bugfix-candidate.json").read_text())
manifest_matches = all(before.get(path) == digest for path, digest in candidate["files"].items())
rows = []
with tempfile.TemporaryDirectory(prefix="architecture-review-") as directory:
    path = Path(directory) / "orders.sqlite"
    connection = storage.connect(path)
    order_service.create_order(connection, "normal")
    accepted = order_service.submit_order(connection, "normal")
    other = storage.connect(path)
    persisted = order_service.read_status(other, "normal")
    other.close()
    rows.append({"check": "CHK-002", "case": "second_connection_commit", "accepted": accepted, "status": persisted, "pass": accepted is True and persisted == "submitted"})
    order_service.create_order(connection, "cancelled")
    order_service.cancel_order(connection, "cancelled")
    statements = []
    connection.set_trace_callback(statements.append)
    accepted = order_service.submit_order(connection, "cancelled")
    connection.set_trace_callback(None)
    connection.close()
    connection = storage.connect(path)
    status = order_service.read_status(connection, "cancelled")
    writes = [s for s in statements if s.lstrip().upper().startswith(("UPDATE", "INSERT", "DELETE", "REPLACE"))]
    rows.append({"check": "CHK-005", "case": "cancelled_no_write_reopened", "accepted": accepted, "status": status, "sql": statements, "writes": writes, "pass": accepted is False and status == "cancelled" and not writes})
    ui.mark_paid(connection, "normal")
    other = storage.connect(path)
    paid = order_service.read_status(other, "normal")
    other.close()
    rows.append({"check": "CHK-001", "case": "paid_behavior_only", "status": paid, "pass": paid == "paid", "limit": "Behavior result does not prove compliant write ownership"})
    connection.close()
    readonly = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        result = order_service.submit_order(readonly, "normal")
        rows.append({"check": "CHK-002", "case": "readonly_write_failure", "pass": False, "unexpected_return": result})
    except sqlite3.OperationalError as error:
        rows.append({"check": "CHK-002", "case": "readonly_write_failure", "pass": True, "exception": type(error).__name__, "message": str(error)})
    finally:
        readonly.close()

    class CommitFailure:
        def __init__(self, connection):
            self.connection = connection

        def execute(self, *args):
            return self.connection.execute(*args)

        def commit(self):
            raise sqlite3.OperationalError("controlled commit failure")

    connection = storage.connect(path)
    try:
        result = order_service.submit_order(CommitFailure(connection), "normal")
        rows.append({"check": "CHK-002", "case": "controlled_commit_failure", "pass": False, "unexpected_return": result})
    except sqlite3.OperationalError as error:
        rows.append({"check": "CHK-002", "case": "controlled_commit_failure", "pass": True, "exception": type(error).__name__, "message": str(error), "limit": "Controlled connection proxy; not a physical disk failure experiment"})
    finally:
        connection.rollback()
        connection.close()

after = hashes()
print(json.dumps({"candidate_id": candidate["candidate_id"], "manifest_matches": manifest_matches, "python": sys.version, "sqlite": sqlite3.sqlite_version, "before_sha256": before, "after_sha256": after, "snapshot_unchanged": before == after, "temporary_data_cleaned": not Path(directory).exists(), "observations": rows}, ensure_ascii=False, indent=2))
raise SystemExit(0 if manifest_matches and before == after and all(row["pass"] for row in rows) else 1)
