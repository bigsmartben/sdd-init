"""Run local order contract integration cases against real file-backed SQLite.

Usage: python -B tests/order_regression.py [--case O-01 ...]
AC-1/2/3 remain in checks/acceptance.py. No network or mocks are used.
"""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage, ui


ORDER_ID = "ORDER-1"
MISSING_ID = "MISSING"


@contextmanager
def database():
    """Each case owns its file and closes every connection even after failure."""
    with tempfile.TemporaryDirectory(prefix="order-regression-") as directory:
        path = Path(directory) / "orders.sqlite"
        connections = []

        def connect():
            connection = storage.connect(path)
            connections.append(connection)
            return connection

        try:
            yield connect
        finally:
            for connection in reversed(connections):
                connection.close()


def attempt(action, errors):
    """Capture actual exception types without suppressing case diagnostics."""
    try:
        action()
    except Exception as error:
        errors.append({"type": type(error).__name__, "message": str(error)})
        return type(error).__name__
    return None


def rows(connection):
    # Read-only observation checks that failed calls neither add nor alter rows.
    return [list(row) for row in connection.execute(
        "SELECT order_id, status FROM orders ORDER BY order_id"
    ).fetchall()]


def reopened_status(connection, connect):
    connection.close()
    return order_service.read_status(connect(), ORDER_ID)


def create_pending(connect, errors):
    connection = connect()
    order_service.create_order(connection, ORDER_ID)
    return {"persisted_status": reopened_status(connection, connect)}


def invalid_id(value):
    def run(connect, errors):
        connection = connect()
        exception = attempt(lambda: order_service.create_order(connection, value), errors)
        before_close = rows(connection)
        connection.close()
        return {"exception": exception, "rows": before_close, "persisted_rows": rows(connect())}
    return run


def duplicate_create(connect, errors):
    connection = connect()
    order_service.create_order(connection, ORDER_ID)
    order_service.cancel_order(connection, ORDER_ID)
    exception = attempt(lambda: order_service.create_order(connection, ORDER_ID), errors)
    status = order_service.read_status(connection, ORDER_ID)
    return {"exception": exception, "status": status,
            "persisted_status": reopened_status(connection, connect)}


def repeated_cancel(connect, errors):
    connection = connect()
    order_service.create_order(connection, ORDER_ID)
    order_service.cancel_order(connection, ORDER_ID)
    first = reopened_status(connection, connect)
    connection = connect()
    order_service.cancel_order(connection, ORDER_ID)
    return {"first_persisted_status": first,
            "repeat_persisted_status": reopened_status(connection, connect)}


def mark_paid(initial_status):
    def run(connect, errors):
        connection = connect()
        order_service.create_order(connection, ORDER_ID)
        if initial_status == "submitted":
            order_service.submit_order(connection, ORDER_ID)
        elif initial_status == "cancelled":
            order_service.cancel_order(connection, ORDER_ID)
        before = order_service.read_status(connection, ORDER_ID)
        ui.mark_paid(connection, ORDER_ID)
        return {"initial_status": before,
                "persisted_status": reopened_status(connection, connect)}
    return run


OPERATIONS = {
    "read": order_service.read_status,
    "cancel": order_service.cancel_order,
    "submit": order_service.submit_order,
    "set_status": lambda connection, order_id: order_service.set_status(connection, order_id, "paid"),
    "mark_paid": ui.mark_paid,
}


def missing_order(operation):
    def run(connect, errors):
        connection = connect()
        order_service.create_order(connection, ORDER_ID)
        exception = attempt(lambda: OPERATIONS[operation](connection, MISSING_ID), errors)
        current = rows(connection)
        connection.close()
        return {"exception": exception, "rows": current, "persisted_rows": rows(connect())}
    return run


def query_only(operation):
    def run(connect, errors):
        connection = connect()
        order_service.create_order(connection, ORDER_ID)
        connection.execute("PRAGMA query_only = ON")
        enabled = connection.execute("PRAGMA query_only").fetchone()[0]
        if operation == "create":
            action = lambda: order_service.create_order(connection, "NEW-ORDER")
        else:
            action = lambda: OPERATIONS[operation](connection, ORDER_ID)
        exception = attempt(action, errors)
        current = rows(connection)
        connection.close()
        return {"query_only": enabled, "exception": exception,
                "rows": current, "persisted_rows": rows(connect())}
    return run


def commit_read_lock(connect, errors):
    connection = connect()
    order_service.create_order(connection, ORDER_ID)
    connection.execute("PRAGMA journal_mode = DELETE")
    connection.execute("PRAGMA busy_timeout = 0")
    blocker = connect()
    blocker.execute("BEGIN")
    locked_status = order_service.read_status(blocker, ORDER_ID)
    try:
        exception = attempt(lambda: order_service.submit_order(connection, ORDER_ID), errors)
        active_transaction = connection.in_transaction
        current_status = order_service.read_status(connection, ORDER_ID)
        connection.rollback()
        rolled_back_status = order_service.read_status(connection, ORDER_ID)
    finally:
        blocker.rollback()
        blocker.close()
    return {"locked_status": locked_status, "exception": exception,
            "status_after_caller_rollback": rolled_back_status,
            "_observations": {"in_transaction_after_error": active_transaction,
                              "status_before_caller_rollback": current_status},
            "persisted_status": reopened_status(connection, connect)}


def case_definitions():
    baseline = [[ORDER_ID, "pending"]]
    cases = [
        ("O-01", "create pending survives reopen", create_pending,
         {"persisted_status": "pending"}),
    ]
    for number, value in enumerate(("", None, 7), 2):
        cases.append((f"O-{number:02}", f"create rejects id {value!r}", invalid_id(value),
                      {"exception": "ValueError", "rows": [], "persisted_rows": []}))
    cases.extend([
        ("O-05", "duplicate create preserves cancelled order", duplicate_create,
         {"exception": "IntegrityError", "status": "cancelled", "persisted_status": "cancelled"}),
        ("O-06", "cancel persists and repeated cancel persists", repeated_cancel,
         {"first_persisted_status": "cancelled", "repeat_persisted_status": "cancelled"}),
    ])
    for number, status in enumerate(("pending", "submitted", "cancelled"), 7):
        cases.append((f"O-{number:02}", f"mark_paid from {status}", mark_paid(status),
                      {"initial_status": status, "persisted_status": "paid"}))
    for number, operation in enumerate(OPERATIONS, 10):
        cases.append((f"O-{number:02}", f"{operation} rejects missing order without side effects",
                      missing_order(operation), {"exception": "ValueError", "rows": baseline,
                                                 "persisted_rows": baseline}))
    for number, operation in enumerate(("create", "cancel", "submit", "set_status", "mark_paid"), 15):
        cases.append((f"O-{number:02}", f"{operation} propagates SQLite query_only failure",
                      query_only(operation), {"query_only": 1, "exception": "OperationalError",
                                              "rows": baseline, "persisted_rows": baseline}))
    cases.append(("O-20", "submit commit blocked by read lock propagates error; caller rolls back",
                  commit_read_lock, {"locked_status": "pending", "exception": "OperationalError",
                                     "status_after_caller_rollback": "pending",
                                     "persisted_status": "pending"}))
    return cases


def run(case):
    case_id, description, scenario, expected = case
    errors = []
    actual = None
    observations = {}
    try:
        with database() as connect:
            actual = scenario(connect, errors)
            observations = actual.pop("_observations", {})
        passed = actual == expected
    except Exception as error:
        errors.append({"type": type(error).__name__, "message": str(error), "phase": "scenario"})
        passed = False
    return {"case": case_id, "description": description,
            "result": "PASS" if passed else "FAIL", "actual": actual,
            "expected": expected, "observations": observations, "errors": errors}


def main():
    cases = case_definitions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", nargs="+", action="extend", choices=[case[0] for case in cases])
    args = parser.parse_args()
    selected = [case for case in cases if not args.case or case[0] in args.case]
    results = [run(case) for case in selected]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(result["result"] == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
