"""Execute actual local acceptance; never contacts the external service."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import order_service, storage, ui

OPERATIONS = {
    "READ": order_service.read_status,
    "SET": lambda connection, order_id: order_service.set_status(connection, order_id, "paid"),
    "CANCEL": order_service.cancel_order,
    "SUBMIT": order_service.submit_order,
    "PAY": ui.mark_paid,
}
WRITE_OPERATIONS = {"CREATE": order_service.create_order,
                    **{key: value for key, value in OPERATIONS.items() if key != "READ"}}
SCENARIOS = ("AC-1", "AC-2", "AC-3", "STATE-1", "STATE-2", "PAY-1",
             *(f"ERR-2-{key}" for key in OPERATIONS),
             *(f"ERR-3-{key}" for key in WRITE_OPERATIONS))


def _persisted(path, order_id="ORDER-1"):
    connection = storage.connect(path)
    try:
        return order_service.read_status(connection, order_id)
    finally:
        connection.close()


def _expect_exception(operation, expected):
    try:
        operation()
    except Exception as error:
        return {"result": "PASS" if isinstance(error, expected) else "FAIL",
                "expected_exception": expected.__name__,
                "actual_exception": type(error).__name__, "message": str(error)}
    return {"result": "FAIL", "expected_exception": expected.__name__,
            "actual_exception": None, "reason": "Operation returned without the required exception"}


def _run_local(scenario, path, connection):
    if scenario.startswith("ERR-2-"):
        operation = OPERATIONS[scenario.removeprefix("ERR-2-")]
        return _expect_exception(lambda: operation(connection, "MISSING"), ValueError)

    order_service.create_order(connection, "ORDER-1")
    if scenario.startswith("ERR-3-"):
        operation = WRITE_OPERATIONS[scenario.removeprefix("ERR-3-")]
        # SQLite itself rejects writes; no fake connection or service substitute.
        connection.execute("PRAGMA query_only = ON")
        target = "ORDER-2" if scenario == "ERR-3-CREATE" else "ORDER-1"
        result = _expect_exception(lambda: operation(connection, target), sqlite3.OperationalError)
        result.update(persisted_status=_persisted(path), expected_status="pending",
                      order_count=connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
                      expected_order_count=1, fault="SQLite PRAGMA query_only=ON")
        if result["persisted_status"] != "pending" or result["order_count"] != 1:
            result["result"] = "FAIL"
        return result

    intermediate = {"created": order_service.read_status(connection, "ORDER-1")}
    if scenario in ("AC-2", "STATE-2"):
        order_service.cancel_order(connection, "ORDER-1")
        intermediate["cancelled"] = order_service.read_status(connection, "ORDER-1")
    accepted = None
    if scenario in ("AC-1", "AC-2"):
        accepted = order_service.submit_order(connection, "ORDER-1")
    elif scenario == "PAY-1":
        ui.mark_paid(connection, "ORDER-1")
        intermediate["paid"] = order_service.read_status(connection, "ORDER-1")
    connection.close()
    status = _persisted(path)
    expected_status = {"AC-1": "submitted", "AC-2": "cancelled", "STATE-1": "pending",
                       "STATE-2": "cancelled", "PAY-1": "paid"}[scenario]
    expected_intermediate = {"created": "pending"}
    if scenario in ("AC-2", "STATE-2"):
        expected_intermediate["cancelled"] = "cancelled"
    if scenario == "PAY-1":
        expected_intermediate["paid"] = "paid"
    passed = status == expected_status and intermediate == expected_intermediate
    result = {"persisted_status": status, "expected_status": expected_status,
              "intermediate_states": intermediate, "expected_intermediate_states": expected_intermediate}
    if scenario in ("AC-1", "AC-2"):
        expected_accepted = scenario == "AC-1"
        passed = passed and accepted is expected_accepted
        result.update(accepted=accepted, expected_accepted=expected_accepted)
    return {"result": "PASS" if passed else "FAIL", **result}


def run(scenario):
    """Return one independent result, including unexpected setup or product errors."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    try:
        if scenario == "AC-3":
            config = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
            return {"scenario": scenario, "result": "BLOCKED",
                    "reason": "No external call is performed by this fixture; authorized endpoint and permission are required",
                    "endpoint_configured": bool(config["external_endpoint"]),
                    "authorized": config["external_call_authorized"]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.sqlite"
            connection = storage.connect(path)
            try:
                return {"scenario": scenario, **_run_local(scenario, path, connection)}
            finally:
                connection.close()
    except Exception as error:
        return {"scenario": scenario, "result": "FAIL",
                "exception": type(error).__name__, "reason": str(error)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=SCENARIOS)
    args = parser.parse_args(argv)
    results = [run(scenario) for scenario in ([args.scenario] if args.scenario else SCENARIOS)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(row["result"] == "FAIL" for row in results) else 3 if any(row["result"] == "BLOCKED" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
