"""Run isolated file-backed order integration checks without external calls.

Exit 1 for failures, 3 for blockers without failures, or 0 for all passed.
Each local case owns a temporary SQLite file, removed after connections close.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from checks import acceptance
from src import order_service, storage, ui


def hashes():
    paths = sorted((ROOT / "src").rglob("*.py"))
    paths += [Path(__file__).resolve(), ROOT / "checks/acceptance.py"]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths}


def metadata():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True, check=False)
    return {"head": head.stdout.strip() if head.returncode == 0 else None,
            "head_error": head.stderr.strip() if head.returncode else None,
            "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
            "source_sha256": hashes()}


class Case:
    def __init__(self, case_id, basis):
        self.row = {"case_id": case_id, "basis": basis, "result": "PASS",
                    "observations": []}

    def observe(self, step, actual, expected, exception_type=None, passed=None):
        ok = actual == expected if passed is None else passed
        self.row["observations"].append({"step": step, "actual": actual,
                                          "expected": expected,
                                          "exception_type": exception_type,
                                          "matches": ok})
        if not ok:
            self.row["result"] = "FAIL"

    def raises(self, step, action, expected_type):
        try:
            returned = action()
        except Exception as error:
            self.observe(step, {"message": str(error)},
                         {"exception_family": expected_type.__name__},
                         type(error).__name__, isinstance(error, expected_type))
        else:
            self.observe(step, {"returned": returned},
                         {"exception_family": expected_type.__name__}, passed=False)


def status(connection, order_id="ORDER-1"):
    return order_service.read_status(connection, order_id)


def reopened(path, order_id="ORDER-1"):
    connection = storage.connect(path)
    try:
        return status(connection, order_id)
    finally:
        connection.close()


def pending(case, connection, path):
    order_service.create_order(connection, "ORDER-1")
    case.observe("created status", status(connection), "pending")
    connection.close()
    case.observe("status after close and reopen", reopened(path), "pending")


def submit(case, connection, path, cancelled=False):
    order_service.create_order(connection, "ORDER-1")
    case.observe("created status", status(connection), "pending")
    if cancelled:
        order_service.cancel_order(connection, "ORDER-1")
        case.observe("cancelled status before submit", status(connection), "cancelled")
        case.observe("cancel persisted before submit", reopened(path), "cancelled")
    accepted = order_service.submit_order(connection, "ORDER-1")
    case.observe("submit result", accepted, not cancelled,
                 passed=accepted is (not cancelled))
    expected = "cancelled" if cancelled else "submitted"
    case.observe("status after submit", status(connection), expected)
    connection.close()
    case.observe("status after close and reopen", reopened(path), expected)


def paid(case, connection, path):
    order_service.create_order(connection, "ORDER-1")
    case.observe("created status", status(connection), "pending")
    ui.mark_paid(connection, "ORDER-1")
    case.observe("status after mark_paid", status(connection), "paid")
    connection.close()
    case.observe("status after close and reopen", reopened(path), "paid")


def set_status(case, connection, path):
    order_service.create_order(connection, "ORDER-1")
    order_service.set_status(connection, "ORDER-1", "paid")
    case.observe("status after set_status", status(connection), "paid")
    connection.close()
    case.observe("status after close and reopen", reopened(path), "paid")


def invalid(case, connection, path, order_id):
    case.raises("create invalid order ID", lambda: order_service.create_order(connection, order_id),
                ValueError)
    case.observe("rows after rejected create",
                 connection.execute("SELECT order_id, status FROM orders").fetchall(), [])
    connection.close()
    check = storage.connect(path)
    try:
        case.observe("persisted rows after reopen",
                     check.execute("SELECT order_id, status FROM orders").fetchall(), [])
    finally:
        check.close()


OPERATIONS = {
    "read": lambda connection, key: order_service.read_status(connection, key),
    "cancel": lambda connection, key: order_service.cancel_order(connection, key),
    "submit": lambda connection, key: order_service.submit_order(connection, key),
    "set_status": lambda connection, key: order_service.set_status(connection, key, "paid"),
    "mark_paid": lambda connection, key: ui.mark_paid(connection, key),
    "create": lambda connection, key: order_service.create_order(connection, key),
}


def missing(case, connection, path, operation):
    order_service.create_order(connection, "ORDER-1")
    case.raises("operation on missing order", lambda: OPERATIONS[operation](connection, "MISSING"),
                ValueError)
    connection.close()
    case.observe("existing order remains persisted", reopened(path), "pending")
    check = storage.connect(path)
    try:
        case.raises("missing order remains absent", lambda: status(check, "MISSING"), ValueError)
    finally:
        check.close()


def closed(case, connection, path, operation):
    order_service.create_order(connection, "ORDER-1")
    connection.close()
    key = "NEW-ORDER" if operation == "create" else "ORDER-1"
    case.raises("write on closed connection", lambda: OPERATIONS[operation](connection, key),
                sqlite3.Error)
    case.observe("original persisted status", reopened(path), "pending")
    if operation == "create":
        check = storage.connect(path)
        try:
            case.raises("failed create remains absent", lambda: status(check, key), ValueError)
        finally:
            check.close()


def isolation(case, connection, path):
    for key in ("ORDER-1", "ORDER-2", "ORDER-3"):
        order_service.create_order(connection, key)
    order_service.cancel_order(connection, "ORDER-1")
    case.observe("second order submit result",
                 order_service.submit_order(connection, "ORDER-2"), True)
    ui.mark_paid(connection, "ORDER-3")
    expected = {"ORDER-1": "cancelled", "ORDER-2": "submitted", "ORDER-3": "paid"}
    case.observe("independent states before close",
                 {key: status(connection, key) for key in expected}, expected)
    connection.close()
    case.observe("independent states after reopen",
                 {key: reopened(path, key) for key in expected}, expected)


def local_cases():
    cases = [("INT-01", "pending creation persistence", pending),
             ("AC-1", "Spec AC-1", submit),
             ("AC-2", "Spec AC-2", lambda c, db, p: submit(c, db, p, True)),
             ("INT-02", "existing mark_paid persistence", paid),
             ("INT-03", "set_status persistence", set_status)]
    for suffix, value in (("EMPTY", ""), ("NONE", None), ("INTEGER", 1)):
        cases.append(("INVALID-" + suffix, "nonempty string order ID",
                      lambda c, db, p, value=value: invalid(c, db, p, value)))
    for operation in ("read", "cancel", "submit", "set_status", "mark_paid"):
        cases.append(("MISSING-" + operation.upper(), "missing order raises ValueError",
                      lambda c, db, p, op=operation: missing(c, db, p, op)))
    for operation in ("create", "cancel", "submit", "set_status", "mark_paid"):
        cases.append(("CLOSED-" + operation.upper(), "database exceptions propagate",
                      lambda c, db, p, op=operation: closed(c, db, p, op)))
    cases.append(("INT-04", "multiple order isolation", isolation))
    return cases


def run_local(case_id, basis, action):
    case = Case(case_id, basis)
    with tempfile.TemporaryDirectory(prefix="order-integration-") as directory:
        path = Path(directory) / "orders.sqlite"
        connection = None
        try:
            connection = storage.connect(path)
            action(case, connection, path)
        except Exception as error:
            case.observe("unexpected scenario exception", {"message": str(error)},
                         "scenario completes", type(error).__name__, False)
        finally:
            if connection is not None:
                connection.close()
    return case.row


def external_case():
    case = Case("AC-3", "Spec AC-3: authorized real external service receipt")
    try:
        facts = acceptance.run("AC-3")
    except (OSError, KeyError, ValueError) as error:
        facts = {"reason": "External configuration could not be read",
                 "exception_type": type(error).__name__, "message": str(error)}
    case.row.update(result="BLOCKED", actual=facts,
                    expected="Receipt verified against an authorized real external test service",
                    exception_type=facts.get("exception_type"),
                    recovery="Authorized endpoint and call permission required; this script performs no external calls")
    return case.row


def main():
    cases = local_cases()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=[row[0] for row in cases] + ["AC-3"])
    args = parser.parse_args()
    before = metadata()
    results = [run_local(*row) for row in cases if args.case in (None, row[0])]
    if args.case in (None, "AC-3"):
        results.append(external_case())
    after = hashes()
    if before["source_sha256"] != after:
        results.append({"case_id": "SOURCE-STABILITY", "result": "FAIL",
                        "actual": after, "expected": before["source_sha256"],
                        "reason": "Sources changed during execution; rerun on a stable version"})
    summary = {state: sum(row["result"] == state for row in results)
               for state in ("PASS", "FAIL", "BLOCKED")}
    print(json.dumps({"environment": before, "results": results, "summary": summary},
                     ensure_ascii=False, indent=2))
    return 1 if summary["FAIL"] else 3 if summary["BLOCKED"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
