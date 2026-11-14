"""Execute isolated order acceptance checks; never contacts external services."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage, ui

OPERATIONS = {
    "create": order_service.create_order,
    "submit": order_service.submit_order,
    "cancel": order_service.cancel_order,
    "set_status": lambda connection, order_id: order_service.set_status(connection, order_id, "paid"),
    "mark_paid": ui.mark_paid,
}
INVALID_IDS = {"empty": "", "none": None, "integer": 42}
SCENARIOS = (
    "AC-1", "AC-2", "AC-3", "PAY-1", "PAY-2",
    *(f"ID-{operation}-{kind}" for operation in OPERATIONS for kind in INVALID_IDS),
    *(f"MISSING-{operation}" for operation in ("submit", "cancel", "set_status")),
    *(f"DB-{operation}" for operation in OPERATIONS),
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def snapshot(connection):
    return dict(connection.execute("SELECT order_id, status FROM orders ORDER BY order_id"))


def expect_error(result, operation, expected_type):
    try:
        returned = operation()
    except Exception as error:
        result["observed_error"] = {"type": type(error).__name__, "message": str(error)}
        return isinstance(error, expected_type)
    result["unexpected_return"] = returned
    return False


def run(scenario):
    result = {"scenario": scenario, "result": "FAIL", "states": {}}
    try:
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}")
        if scenario == "AC-3":
            config = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
            result.update(
                result="BLOCKED",
                reason="Real external receipt requires an authorized endpoint and network access; this local runner never makes network calls",
                endpoint_configured=bool(config.get("external_endpoint")),
                authorized=config.get("external_call_authorized", False),
                network_access=config.get("network_access_in_this_run", False),
                external_call_performed=False,
            )
            return result
        with tempfile.TemporaryDirectory(prefix="order-acceptance-") as directory:
            path = Path(directory) / "orders.sqlite"
            connection = storage.connect(path)
            try:
                if scenario in ("AC-1", "AC-2", "PAY-1"):
                    order_service.create_order(connection, "ORDER-1")
                    result["states"]["created"] = snapshot(connection)
                    if scenario == "AC-2":
                        order_service.cancel_order(connection, "ORDER-1")
                        result["states"]["cancelled"] = snapshot(connection)
                    result["accepted"] = order_service.submit_order(connection, "ORDER-1")
                    result["states"]["after_submit"] = snapshot(connection)
                    if scenario == "PAY-1":
                        ui.mark_paid(connection, "ORDER-1")
                        result["states"]["after_paid"] = snapshot(connection)
                elif scenario.startswith("ID-"):
                    _, operation, kind = scenario.split("-")
                    result["input_order_id"] = INVALID_IDS[kind]
                    if kind == "integer":
                        # SQLite can coerce 42 to the valid ID "42"; rejection must
                        # protect existing orders as well as absent ones.
                        order_service.create_order(connection, "42")
                    result["states"]["before_operation"] = snapshot(connection)
                    result["expected_error"] = "ValueError"
                    result["error_matches"] = expect_error(
                        result, lambda: OPERATIONS[operation](connection, INVALID_IDS[kind]), ValueError
                    )
                    result["states"]["after_operation"] = snapshot(connection)
                elif scenario == "PAY-2" or scenario.startswith("MISSING-"):
                    operation = "mark_paid" if scenario == "PAY-2" else scenario.removeprefix("MISSING-")
                    result["expected_error"] = "ValueError"
                    result["error_matches"] = expect_error(
                        result, lambda: OPERATIONS[operation](connection, "MISSING"), ValueError
                    )
                    result["states"]["after_operation"] = snapshot(connection)
                else:
                    operation = scenario.removeprefix("DB-")
                    order_service.create_order(connection, "ORDER-1")
                    result["states"]["before_close"] = snapshot(connection)
                    connection.close()
                    result["expected_error"] = "sqlite3.Error"
                    result["error_matches"] = expect_error(
                        result, lambda: OPERATIONS[operation](connection, "ORDER-2" if operation == "create" else "ORDER-1"), sqlite3.Error
                    )
            finally:
                connection.close()
                # Reopen even when a scenario raises, preserving persistence evidence.
                reopened = storage.connect(path)
                try:
                    result["states"]["reopened"] = snapshot(reopened)
                finally:
                    reopened.close()
            if scenario in ("AC-1", "AC-2", "PAY-1"):
                expected_status = {"AC-1": "submitted", "AC-2": "cancelled", "PAY-1": "paid"}[scenario]
                result["expected_accepted"] = scenario != "AC-2"
                result["expected_status"] = expected_status
                result["persisted_status"] = result["states"]["reopened"].get("ORDER-1")
                require(result["states"]["created"] == {"ORDER-1": "pending"}, "Creation must persist pending")
                if scenario == "AC-2":
                    require(result["states"]["cancelled"] == {"ORDER-1": "cancelled"}, "Cancel must persist cancelled")
                require(result["accepted"] is result["expected_accepted"], "Unexpected submit return value")
                submitted_status = "cancelled" if scenario == "AC-2" else "submitted"
                require(result["states"]["after_submit"] == {"ORDER-1": submitted_status}, "Unexpected state after submit")
                require(result["states"]["reopened"] == {"ORDER-1": expected_status}, "Unexpected persisted state after reopen")
            else:
                require(result["error_matches"], f"Expected {result['expected_error']} to propagate")
                expected_state = (
                    {"ORDER-1": "pending"} if scenario.startswith("DB-")
                    else result["states"].get("before_operation", {})
                )
                require(result["states"]["reopened"] == expected_state, "Rejected operation must not change persisted orders")
        result["result"] = "PASS"
    except Exception as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=SCENARIOS)
    args = parser.parse_args()
    results = [run(scenario) for scenario in ([args.scenario] if args.scenario else SCENARIOS)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(row["result"] == "FAIL" for row in results) else 3 if any(row["result"] == "BLOCKED" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
