"""Execute actual local acceptance; never contacts the external service."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage


def check_order_id(order_id, rejected):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        try:
            order_service.create_order(connection, "BASELINE")
            baseline = connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
            error = None
            try:
                order_service.create_order(connection, order_id)
            except Exception as exc:
                error = {"type": type(exc).__name__, "message": str(exc)}
            current = connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
            expected = baseline if rejected else sorted(baseline + [(order_id, "pending")])
            current_status = None if rejected or error else order_service.read_status(connection, order_id)
        finally:
            connection.close()
        connection = storage.connect(path)
        try:
            persisted = connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
            persisted_status = None if rejected or error else order_service.read_status(connection, order_id)
        finally:
            connection.close()
    checks = {
        "outcome_matches": error == {"type": "ValueError", "message": "order_id is required"} if rejected else error is None,
        "current_rows_match": current == expected,
        "persisted_rows_match": persisted == expected,
    }
    if not rejected:
        checks["current_pending"] = current_status == "pending"
        checks["persisted_pending"] = persisted_status == "pending"
        checks["original_value_preserved"] = (order_id, "pending") in current and (order_id, "pending") in persisted
        if order_id != order_id.strip():
            checks["no_trimmed_replacement"] = all(row[0] != order_id.strip() for row in current + persisted)
    return {
        "input_repr": repr(order_id),
        "input_type": type(order_id).__name__,
        "expected_rejection": rejected,
        "result": "PASS" if all(checks.values()) else "FAIL",
        "error": error,
        "checks": checks,
        "baseline_rows": baseline,
        "current_rows": current,
        "persisted_rows": persisted,
    }


def run(scenario):
    if scenario in ("AC-4", "AC-5"):
        inputs = (
            [(value, True) for value in ("", " ", "   ", "\t", "\n", " \t\r\n ", "\u3000", "\u00a0")]
            if scenario == "AC-4" else
            [(value, False) for value in ("ORDER-1", " ORDER-1 ", "\tORDER-1\n")]
            + [(value, True) for value in (None, 0, False, [], {})]
        )
        results = [check_order_id(value, rejected) for value, rejected in inputs]
        return {
            "scenario": scenario,
            "result": "PASS" if all(row["result"] == "PASS" for row in results) else "FAIL",
            "inputs": results,
        }
    if scenario == "AC-3":
        config = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
        return {
            "scenario": scenario,
            "result": "BLOCKED",
            "reason": "No external call is performed by this fixture; authorized endpoint and permission are required",
            "endpoint_configured": bool(config["external_endpoint"]),
            "authorized": config["external_call_authorized"],
        }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        try:
            order_service.create_order(connection, "ORDER-1")
            if scenario == "AC-2":
                order_service.cancel_order(connection, "ORDER-1")
            accepted = order_service.submit_order(connection, "ORDER-1")
        finally:
            connection.close()
        connection = storage.connect(path)
        try:
            status = order_service.read_status(connection, "ORDER-1")
        finally:
            connection.close()
    expected = (True, "submitted") if scenario == "AC-1" else (False, "cancelled")
    return {
        "scenario": scenario,
        "result": "PASS" if (accepted, status) == expected else "FAIL",
        "accepted": accepted,
        "persisted_status": status,
        "expected_accepted": expected[0],
        "expected_status": expected[1],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    scenarios = ("AC-1", "AC-2", "AC-3", "AC-4", "AC-5")
    parser.add_argument("--scenario", choices=scenarios)
    args = parser.parse_args()
    results = [run(scenario) for scenario in ([args.scenario] if args.scenario else scenarios)]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(row["result"] == "FAIL" for row in results) else 3 if any(row["result"] == "BLOCKED" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
