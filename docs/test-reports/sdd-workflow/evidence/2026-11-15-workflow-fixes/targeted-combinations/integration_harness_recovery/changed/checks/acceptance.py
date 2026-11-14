"""Execute isolated file-SQLite acceptance; never contact external services."""
import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import socket
import sqlite3
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage, ui

MISSING_OPERATIONS = ("read_status", "set_status", "cancel_order", "submit_order", "mark_paid")
INVALID_IDS = {"empty": "", "none": None, "integer": 1}
SCENARIOS = (
    "AC-1", "AC-2", "AC-3", "LOCAL-create", "LOCAL-cancel",
    *(f"PAID-{status}" for status in ("pending", "submitted", "cancelled")),
    *(f"MISSING-{operation}" for operation in MISSING_OPERATIONS),
    *(f"INVALID-{name}" for name in INVALID_IDS),
    "VALID-single", "VALID-unicode", "LOCK-create", "LOCK-cancel",
    "LOCK-submit", "LOCK-set_status", "LOCK-paid", "CLOSED-read_status", "LOCAL-no-network",
)


@contextmanager
def network_guard(attempts):
    def denied(*args, **kwargs):
        attempts.append("network call attempted")
        raise RuntimeError("network access prohibited in local acceptance")
    with patch.object(socket.socket, "connect", denied), patch.object(socket.socket, "connect_ex", denied), patch.object(socket, "create_connection", denied), patch.object(socket, "getaddrinfo", denied):
        yield


def invoke(operation, connection, order_id):
    if operation == "mark_paid":
        return ui.mark_paid(connection, order_id)
    if operation == "set_status":
        return order_service.set_status(connection, order_id, "paid")
    return getattr(order_service, operation)(connection, order_id)


def observe_exception(call):
    try:
        returned = call()
    except Exception as error:
        return {"exception": type(error).__name__, "message": str(error)}
    return {"exception": None, "returned": returned}


def local_case(scenario, path, row):
    connection = storage.connect(path)
    states = row["intermediate_states"]
    actual = row["actual"]
    try:
        if scenario.startswith("MISSING-"):
            operation = scenario.removeprefix("MISSING-")
            row["expected"] = {"exception": "ValueError", "order_count": 0}
            actual.update(observe_exception(lambda: invoke(operation, connection, "MISSING")))
            actual["order_count"] = connection.execute("SELECT count(*) FROM orders").fetchone()[0]
            return
        if scenario.startswith("INVALID-"):
            value = INVALID_IDS[scenario.removeprefix("INVALID-")]
            row["expected"] = {"exception": "ValueError", "order_count": 0}
            actual["input"] = value
            actual.update(observe_exception(lambda: order_service.create_order(connection, value)))
            actual["order_count"] = connection.execute("SELECT count(*) FROM orders").fetchone()[0]
            return
        if scenario == "CLOSED-read_status":
            connection.close()
            row["expected"] = {"exception": "ProgrammingError"}
            actual.update(observe_exception(lambda: order_service.read_status(connection, "ORDER-1")))
            return
        if scenario.startswith("VALID-"):
            order_id = "x" if scenario == "VALID-single" else "订单-一"
            row["expected"] = {"persisted_status": "pending", "order_id": order_id}
            order_service.create_order(connection, order_id)
            states.append({"after": "create", "status": order_service.read_status(connection, order_id)})
            connection.close()
            connection = storage.connect(path)
            actual.update(order_id=order_id, persisted_status=order_service.read_status(connection, order_id))
            states.append({"after": "close_and_reopen", "status": actual["persisted_status"]})
            return
        order_service.create_order(connection, "ORDER-1")
        states.append({"after": "create", "status": order_service.read_status(connection, "ORDER-1")})
        expected_status = "pending"
        if scenario in ("AC-2", "LOCAL-cancel", "PAID-cancelled"):
            order_service.cancel_order(connection, "ORDER-1")
            states.append({"after": "cancel", "status": order_service.read_status(connection, "ORDER-1")})
            expected_status = "cancelled"
        if scenario == "PAID-submitted":
            actual["setup_submit_returned"] = order_service.submit_order(connection, "ORDER-1")
            states.append({"after": "submit", "status": order_service.read_status(connection, "ORDER-1")})
        if scenario in ("AC-1", "AC-2"):
            row["expected"] = {"accepted": scenario == "AC-1", "persisted_status": "submitted" if scenario == "AC-1" else "cancelled"}
            actual["accepted"] = order_service.submit_order(connection, "ORDER-1")
            states.append({"after": "submit", "status": order_service.read_status(connection, "ORDER-1")})
        elif scenario.startswith("PAID-"):
            expected_status = "paid"
            ui.mark_paid(connection, "ORDER-1")
            states.append({"after": "mark_paid", "status": order_service.read_status(connection, "ORDER-1")})
        elif scenario.startswith("LOCK-"):
            row["expected"] = {"exception": "OperationalError", "persisted_status": "pending", "locked": True, "order_count": 1}
            connection.execute("PRAGMA busy_timeout = 0")
            locker = sqlite3.connect(path, timeout=0)
            try:
                locker.execute("BEGIN IMMEDIATE")
                actual["locked"] = locker.in_transaction
                states.append({"after": "lock", "write_lock_held": locker.in_transaction})
                operation = {"LOCK-submit": "submit_order", "LOCK-paid": "mark_paid", "LOCK-cancel": "cancel_order", "LOCK-set_status": "set_status", "LOCK-create": "create_order"}[scenario]
                order_id = "ORDER-2" if scenario == "LOCK-create" else "ORDER-1"
                actual.update(observe_exception(lambda: invoke(operation, connection, order_id)))
            finally:
                locker.rollback()
                locker.close()
        elif scenario == "LOCAL-no-network":
            # Exercise every public local operation with the guard active.
            order_service.submit_order(connection, "ORDER-1")
            states.append({"after": "submit", "status": order_service.read_status(connection, "ORDER-1")})
            order_service.cancel_order(connection, "ORDER-1")
            states.append({"after": "cancel", "status": order_service.read_status(connection, "ORDER-1")})
            order_service.set_status(connection, "ORDER-1", "pending")
            states.append({"after": "set_status", "status": order_service.read_status(connection, "ORDER-1")})
            ui.mark_paid(connection, "ORDER-1")
            states.append({"after": "mark_paid", "status": order_service.read_status(connection, "ORDER-1")})
            expected_status = "paid"
        if not row["expected"]:
            row["expected"] = {"persisted_status": expected_status}
    finally:
        connection.close()
    connection = storage.connect(path)
    try:
        actual["order_count"] = connection.execute("SELECT count(*) FROM orders").fetchone()[0]
        actual["persisted_status"] = order_service.read_status(connection, "ORDER-1")
        states.append({"after": "close_and_reopen", "status": actual["persisted_status"]})
    finally:
        connection.close()


def run(scenario):
    row = {"scenario": scenario, "result": "FAIL", "expected": {}, "actual": {}, "intermediate_states": []}
    attempts = []
    try:
        if scenario not in SCENARIOS:
            raise ValueError(f"unknown scenario: {scenario}")
        if scenario == "AC-3":
            config = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
            row.update(result="BLOCKED", reason="Authorized real endpoint and permission required; no external call performed")
            row["expected"] = {"real_external_receipt_verified": True}
            row["actual"] = {"real_external_receipt_verified": False, "endpoint_configured": bool(config.get("external_endpoint")), "authorized": config.get("external_call_authorized", False), "external_call_performed": False}
            return row
        with network_guard(attempts), tempfile.TemporaryDirectory() as directory:
            local_case(scenario, Path(directory) / "orders.sqlite", row)
        row["expected"]["network_attempts"] = 0
        row["actual"]["network_attempts"] = len(attempts)
        states = row["intermediate_states"]
        # Intermediate setup is part of the scenario, not just diagnostic output.
        expected_states = {"create": "pending", "cancel": "cancelled", "mark_paid": "paid"}
        row["actual"]["intermediate_states_valid"] = all(state["status"] == expected_states[state["after"]] for state in states if state["after"] in expected_states)
        if scenario == "PAID-submitted":
            row["expected"]["setup_submit_returned"] = True
            row["actual"]["intermediate_states_valid"] &= any(state == {"after": "submit", "status": "submitted"} for state in states)
        row["expected"]["intermediate_states_valid"] = True
        row["result"] = "PASS" if all(row["actual"].get(key) == value for key, value in row["expected"].items()) else "FAIL"
    except Exception as error:
        if not row["expected"]:
            row["expected"] = {"completed": True}
        row["actual"].update(exception=type(error).__name__, message=str(error), network_attempts=len(attempts))
    return row


def exit_code(results):
    if any(row["result"] == "FAIL" for row in results):
        return 1
    return 3 if any(row["result"] == "BLOCKED" for row in results) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=SCENARIOS)
    args = parser.parse_args(argv)
    results = []
    for scenario in ([args.scenario] if args.scenario else SCENARIOS):
        try:
            results.append(run(scenario))
        except Exception as error:
            results.append({"scenario": scenario, "result": "FAIL", "expected": {"completed": True}, "actual": {"exception": type(error).__name__, "message": str(error)}, "intermediate_states": []})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return exit_code(results)


if __name__ == "__main__":
    raise SystemExit(main())
